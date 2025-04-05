import pandas as pd
import streamlit as st

# App configuratie
st.set_page_config(page_title="AI voor Bijwerkingen", layout="centered", initial_sidebar_state="expanded")
st.title("🔬 AI-voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Ontdek welke bijwerkingen kunnen optreden op basis van de ATC-code van een geneesmiddel.")

# Informatie en uitleg
st.sidebar.header("Instructies")
st.sidebar.write("""
    - Voer een ATC-code in (bijvoorbeeld **N02BE01**).
    - Ontvang een lijst met bijwerkingen die gekoppeld zijn aan het medicijn.
    - Deze app maakt gebruik van gegevens over ATC-codes en bijwerkingen om voorspellingen te doen.
""")

# Laad de data
@st.cache_data
def load_data():
    # Laad de ATC codes en bijwerkingen
    atc_df = pd.read_csv("drug_atc.tsv", sep="\t", header=None, names=["ATC Code", "Drug Name"])
    side_effects_df = pd.read_csv("meddra_freq.tsv", sep="\t", header=None, names=["ATC Code", "Side Effect"])
    return atc_df, side_effects_df

# Data laden
atc_df, side_effects_df = load_data()

# Gebruiker invoer voor ATC-code
user_input = st.text_input("🔎 Voer ATC-code in:", value="N02BE01", max_chars=10)

# Kijken of de ATC-code bestaat
if user_input:
    # Zoek de bijwerkingen op basis van de ATC-code
    matched_data = side_effects_df[side_effects_df['ATC Code'] == user_input.upper()]
    
    # Controleer of er bijwerkingen zijn voor de ingevoerde ATC-code
    if not matched_data.empty:
        st.subheader("📊 Gevonden bijwerkingen:")
        for _, row in matched_data.iterrows():
            st.markdown(f"- **{row['Side Effect']}**")
    else:
        st.error("❌ De opgegeven ATC-code werd niet gevonden in de dataset. Probeer een andere code.")

# Stijl en visuele verbeteringen
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #f1f1f1;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stMarkdown>p {
            font-size: 18px;
        }
        .stTextInput>div>input {
            background-color: #f0f0f0;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Footer om de app af te maken
st.markdown("---")
st.markdown("📅 **Versie 1.0** | 📈 **Bijwerkingen AI**")
st.markdown("Gegevens bron: [meddra_freq.tsv & drug_atc.tsv]")
