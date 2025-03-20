from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

# ✅ Investor Data File Path
INVESTOR_XLSX_PATH = "investors_data.xlsx"

# ✅ Required Model Files
REQUIRED_FILES = ["sbert_model.pkl", "knn_model.pkl", "domain_labels.pkl", INVESTOR_XLSX_PATH]

# 🔹 Verify Required Files Exist
missing_files = [f for f in REQUIRED_FILES if not os.path.exists(f)]
if missing_files:
    raise RuntimeError(f"❌ Missing files: {missing_files}. Ensure all necessary files are present.")

# ✅ Load Pretrained Models
sbert_model = joblib.load("sbert_model.pkl")
knn_model = joblib.load("knn_model.pkl")
domain_labels = joblib.load("domain_labels.pkl")

# ✅ Load KeyBERT for Keyword Extraction
kw_model = KeyBERT()

# ✅ Load & Normalize Investor Data
def load_investor_data():
    try:
        df = pd.read_excel(INVESTOR_XLSX_PATH).fillna("Not Available")
    except Exception as e:
        raise RuntimeError(f"❌ Error loading investor data: {e}")

    # 🔹 Ensure 'investor_experience(years)' is numeric
    df["investor_experience(years)"] = (
        df["investor_experience(years)"]
        .astype(str)
        .str.extract(r'(\d+)', expand=False)
        .astype(float)
        .fillna(0)
    )

    # 🔹 Ensure 'no_of_companies_invested' is numeric
    df["no_of_companies_invested"] = pd.to_numeric(df["no_of_companies_invested"], errors="coerce").fillna(0)

    return df

# 🔹 Load Investor Data Once
investors_df = load_investor_data()

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ API Input Models
class ProjectInput(BaseModel):
    description: str

class DomainSelection(BaseModel):
    selected_domain: str

# 🔹 Extract Keywords from Project Description
def extract_keywords(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words="english", top_n=10)
    return " ".join([kw[0] for kw in keywords])

# 🔹 Predict Domain Based on Project Description
@app.post("/predict/")
def predict_domain(input: ProjectInput):
    if not input.description.strip():
        raise HTTPException(status_code=400, detail="❌ Project description cannot be empty.")

    try:
        # 🔹 Extract Keywords
        input_keywords = extract_keywords(input.description)

        # 🔹 Encode with SBERT & Ensure Correct Shape
        input_vector = sbert_model.encode([input_keywords]).reshape(1, -1)

        # 🔹 Predict Top 3 Domains
        distances, indices = knn_model.kneighbors(input_vector, n_neighbors=3)
        predicted_domains = [domain_labels[idx] for idx in indices[0]]

        return {
            "predicted_domains": predicted_domains,
            "confidence_scores": distances[0].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 🔹 Get Matching Investors for Selected Domain
@app.post("/investors/")
def get_investors(selection: DomainSelection):
    selected_domain = selection.selected_domain.strip()

    # 🔹 Validate Input
    if not selected_domain:
        raise HTTPException(status_code=400, detail="❌ Selected domain cannot be empty.")

    # 🔹 Filter Investors by Domain
    filtered_investors = investors_df[investors_df["domains"].astype(str).str.contains(selected_domain, case=False, na=False)].copy()

    if filtered_investors.empty:
        return {"message": f"❌ No investors found for domain: {selected_domain}"}

    # 🔹 Compute Match Scores
    filtered_investors["match_score"] = (
        filtered_investors["investor_experience(years)"] * 0.7 + 
        filtered_investors["no_of_companies_invested"] * 0.3
    )

    # 🔹 Sort by Match Score (Highest First)
    sorted_investors = filtered_investors.sort_values(by="match_score", ascending=False).reset_index(drop=True)

    return sorted_investors[[
        "investor_name", "investor_company", "investor_experience(years)", "no_of_companies_invested",
        "domains", "linkedin_url", "email", "funds_available", "past_companies", "match_score"
    ]].to_dict(orient="records")
