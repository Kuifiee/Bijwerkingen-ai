import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="AI voor Bijwerkingen", layout="centered")

st.title("🧠 AI-voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Voer een **medicijnnaam** of **ATC-code** in en ontdek de kans op:")
st.markdown("- ⚠️ Duizeligheid")
st.markdown("- ⚠️ Misselijkheid")
st.markdown("- ⚠️ Huiduitslag")

@st.cache_data
def load_data():
    # Bijwerkingen-data
    df = pd.read_csv("meddra_freq.tsv", sep="\t")
    df["Side Effect"] = df["Side Effect"].str.lower()
    df["has_dizziness"] = df["Side Effect"].str.contains("dizziness").astype(int)
    df["has_nausea"] = df["Side Effect"].str.contains("nausea").astype(int)
    df["has_rash"] = df["Side Effect"].str.contains("rash").astype(int)
    side_effects = df.groupby("ATC Code").agg({
        "has_dizziness": "max",
        "has_nausea": "max",
        "has_rash": "max"
    }).reset_index()

    # Medicijnnamen-data
    drug_names = pd.read_csv("drug_names.tsv", sep="\t")
    return side_effects, drug_names

data, drug_data = load_data()

# Combineer de data voor lookup (ATC + naam)
combined = pd.merge(drug_data, data, on="ATC Code", how="left")

# Maak een zoeklijst
zoeklijst = pd.concat([
    combined["Drug"],
    combined["ATC Code"]
]).dropna().unique()

user_input = st.text_input("🔎 Zoek op medicijn of ATC-code:", value="Paracetamol").strip().upper()

if user_input:
    st.write(f"🔍 Je zocht op: `{user_input}`")

    # Zoek matches
    match = combined[
        (combined["Drug"].str.upper() == user_input) |
        (combined["ATC Code"].str.upper() == user_input)
    ]

    if not match.empty:
        for _, row in match.iterrows():
            st.subheader(f"💊 {row['Drug']} ({row['ATC Code']})")
            st.markdown(f"- **Duizeligheid:** {'⚠️ Kans aanwezig' if row['has_dizziness'] else '✅ Waarschijnlijk niet'}")
            st.markdown(f"- **Misselijkheid:** {'⚠️ Kans aanwezig' if row['has_nausea'] else '✅ Waarschijnlijk niet'}")
            st.markdown(f"- **Huiduitslag:** {'⚠️ Kans aanwezig' if row['has_rash'] else '✅ Waarschijnlijk niet'}")
    else:
        st.warning("Geen resultaten gevonden. Probeer een andere naam of ATC-code.")
