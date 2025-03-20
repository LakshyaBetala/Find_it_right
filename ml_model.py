import pandas as pd
import numpy as np
import joblib
import nltk
import string
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

nltk.download('punkt')
nltk.download('stopwords')

# 🔹 Define domains with expanded keywords
domains = {
    "FinTech": "banking finance investment fraud detection trading cryptocurrency payments stock exchange digital banking financial security fintech loans credit",
    "EdTech": "learning education e-learning students courses AI tutors online classes skill development virtual learning academic platforms EdTech schools universities",
    "Web3 & Crypto": "blockchain decentralization smart contracts NFTs DeFi cryptocurrencies DAO consensus Ethereum tokenization crypto DeFi",
    "Healthcare": "medicine health diagnostics AI doctors hospitals treatment disease patient monitoring clinical trials medical AI pharma biotech",
    "AgriTech": "agriculture crops farming irrigation soil monitoring yield prediction fertilizers precision agriculture AgriTech food production supply chain",
    "Cybersecurity": "security encryption hacking firewalls malware phishing authentication cyber threats risk assessment digital forensics cyber attacks network security",
    "IoT": "internet of things connected devices automation sensors cloud computing smart homes industry 4.0 IoT wearables edge computing smart cities",
    "AI & ML": "machine learning artificial intelligence deep learning neural networks predictive modeling data science AI ML neural networks reinforcement learning",
    "Robotics": "robots automation sensors industrial robots robotic arms AI-powered robots autonomous systems humanoid robots drone technology",
    "AR/VR": "augmented reality virtual reality 3D immersive experiences gaming headsets mixed reality digital twins metaverse",
    "EnergyTech": "renewable energy solar wind sustainability energy efficiency smart grids carbon footprint electric vehicles green tech carbon capture",
    "LegalTech": "law compliance regulations AI-powered legal services contract analysis legal documents automation risk management",
    "GovTech": "government digital transformation public services AI-powered governance smart cities citizen engagement e-governance digital policies",
    "Supply Chain": "logistics warehousing inventory management supply chain AI demand forecasting transportation optimization blockchain logistics",
    "EntertainmentTech": "streaming platforms AI-driven content recommendation gaming industry interactive media content production",
    "MarTech": "marketing automation CRM AI-powered advertising personalization digital marketing analytics customer segmentation",
    "FoodTech": "food delivery nutrition AI-powered recipes personalized diets meal planning restaurant automation smart kitchen plant-based food technology",
    "Ecommerce": "online shopping digital storefronts AI-driven product recommendations ecommerce platforms dropshipping order fulfillment payment gateways",
    "Fashion": "clothing design AI-powered fashion trends retail innovation textile technology sustainable fashion wearable technology",
    "Prop-Tech": "real estate AI-driven property valuation smart homes proptech property management real estate marketplaces digital land registries",
    "Automobile": "automotive electric vehicles self-driving AI-powered vehicle systems connected cars car rental ride-sharing mobility solutions",
    "Bio-Tech": "biotechnology genetic engineering bioinformatics medical research pharmaceuticals biomanufacturing precision medicine gene therapy CRISPR technology",
    "TravelTech": "travel booking AI-powered itineraries hotel tech smart tourism virtual tourism travel safety location intelligence travel apps",
    "Security": "surveillance AI-powered threat detection access control biometrics smart security cybersecurity digital identity protection",
    "EventTech": "event management virtual events AI-powered ticketing audience engagement hybrid events digital event analytics immersive event technology",
    "Metaverse": "virtual worlds blockchain-powered assets VR experiences decentralized social networks digital avatars digital economy virtual property",
}

# 🔹 Load SBERT Model for Better Embeddings
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# 🔹 Initialize KeyBERT once
kw_model = KeyBERT()

# 🔹 Function to extract keywords using KeyBERT
def extract_keywords(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=10)
    return " ".join([kw[0] for kw in keywords])

# 🔹 Extract embeddings directly from domain descriptions
domain_vectors = np.array([sbert_model.encode(desc) for desc in domains.values()])

# 🔹 Train a Nearest Neighbors model for domain matching (K=3 for better results)
knn = NearestNeighbors(n_neighbors=3, metric='cosine')
knn.fit(domain_vectors)

# 🔹 Save models
joblib.dump(sbert_model, "sbert_model.pkl")
joblib.dump(knn, "knn_model.pkl")
joblib.dump(list(domains.keys()), "domain_labels.pkl")

print("✅ Updated Model with New Domains Trained & Saved Successfully!")
