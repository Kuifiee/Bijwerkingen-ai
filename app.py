import pandas as pd
import streamlit as st

# App configuratie
st.set_page_config(page_title="AI voor Bijwerkingen", layout="centered")
st.title("🧠 AI-voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Voer een **ATC-code** in en ontdek welke bijwerkingen daarbij horen.")

# Laad de data
@st.cache_data
def load_data():
    atc_df = pd.read_csv("drug_atc.tsv", sep="\t", header=None, names=["ATC Code", "Drug Name"])
    side_effects_df = pd.read_csv("meddra_freq.tsv", sep="\t", header=None, names=["ATC Code", "Side Effect"])
    return atc_df, side_effects_df

# Data laden
atc_df, side_effects_df = load_data()

# Gebruiker invoer voor ATC-code
user_input = st.text_input("✏️ Voer ATC-code in (bijv. N02BE01):", value="N02BE01")

if user_input:
    # Zoek de bijwerkingen op basis van de ATC-code
    matched_data = side_effects_df[side_effects_df['ATC Code'] == user_input.upper()]
    
    if not matched_data.empty:
        st.subheader("📊 Bijwerkingen:")
        for _, row in matched_data.iterrows():
            st.markdown(f"- **{row['Side Effect']}**")
    else:
        st.error("De opgegeven ATC-code is niet gevonden in de dataset. Probeer een andere code.")
