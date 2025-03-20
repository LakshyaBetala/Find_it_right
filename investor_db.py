import pandas as pd
import re

INVESTOR_XLSX_PATH = "investors_data.xlsx"

def load_investor_data():
    try:
        df = pd.read_excel(INVESTOR_XLSX_PATH)
    except FileNotFoundError:
        print(f"Error: The file '{INVESTOR_XLSX_PATH}' was not found.")
        df = pd.DataFrame()  # Empty DataFrame fallback
    except Exception as e:
        print(f"Error loading the file: {e}")
        df = pd.DataFrame()

    # Define required columns and default values
    required_columns = {
        "investor_name": "Unknown",
        "investor_company": "Unknown",
        "investor_experience(years)": "0",
        "no_of_companies_invested": 0,
        "domains": "Unknown",
        "linkedin_url": "Not Available",
        "email": "Not Available",
        "funds_available": "Unknown",
        "past_companies": "Unknown",
        "investor_type": "Unknown",
    }

    # Add missing columns with default values
    for col, default_value in required_columns.items():
        if col not in df.columns:
            df[col] = default_value

    # Handle missing values
    df = df.fillna("Not Available")

    # ✅ Convert `investor_experience(years)` to numeric by extracting digits
    df["investor_experience(years)"] = (
        df["investor_experience(years)"]
        .astype(str)
        .str.extract(r'(\d+)', expand=False)
        .astype(float)
        .fillna(0)
    )

    # ✅ Convert `funds_available` to numeric (removing $, M, B indicators)
    def convert_funds(value):
        if isinstance(value, str):
            value = value.replace("$", "").upper()
            if "M" in value:
                return float(value.replace("M", "")) * 1_000_000
            elif "B" in value:
                return float(value.replace("B", "")) * 1_000_000_000
            else:
                try:
                    return float(value)
                except ValueError:
                    return 0
        return 0

    df["funds_available"] = df["funds_available"].apply(convert_funds)

    # ✅ Convert numeric columns properly
    df["no_of_companies_invested"] = pd.to_numeric(df["no_of_companies_invested"], errors="coerce").fillna(0)

    return df

# Load and normalize the investor data
df = load_investor_data()

# ✅ Function to compute a match score
def compute_match_score(row):
    experience_weight = 0.6  # Higher weight for experience
    companies_weight = 0.4   # Slightly less weight for no. of companies

    score = (
        (row["investor_experience(years)"] * experience_weight) +
        (row["no_of_companies_invested"] * companies_weight)
    )
    return round(score, 2)

# ✅ Function to get matching investors based on domain
def get_matching_investors(selected_domain, investor_type=None):
    if df.empty:
        return {"message": "Investor data is not available."}

    # Filter by domain (Must Match)
    filtered_df = df[df['domains'].astype(str).str.contains(selected_domain, case=False, na=False)].copy()
    
    # Ensure investor_type column exists before filtering
    if investor_type and "investor_type" in df.columns:
        filtered_df = filtered_df[filtered_df['investor_type'].astype(str).str.contains(investor_type, case=False, na=False)]

    if filtered_df.empty:
        return {"message": f"No investors found for domain: {selected_domain}"}

    # Compute match scores
    filtered_df.loc[:, "match_score"] = filtered_df.apply(compute_match_score, axis=1)

    # Normalize the scores for visualization (scale to 100%)
    max_score = filtered_df["match_score"].max()
    if max_score > 0:
        filtered_df.loc[:, "scaled_score"] = (filtered_df["match_score"] / max_score) * 100
    else:
        filtered_df.loc[:, "scaled_score"] = 0  # If all scores are zero

    # Sort by match score (highest first)
    sorted_df = filtered_df.sort_values(by="match_score", ascending=False)

    # Add hover tooltip for scaled_score visualization
    sorted_df.loc[:, "tooltip"] = sorted_df["scaled_score"].apply(lambda x: f"{x:.2f}% Match")

    return sorted_df[["investor_name", "investor_company", "investor_experience(years)", "no_of_companies_invested", 
                      "domains", "linkedin_url", "email", "funds_available", "past_companies", "match_score", "scaled_score", "tooltip"]].to_dict(orient="records")
