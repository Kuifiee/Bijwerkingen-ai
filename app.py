
# app.py – AI-app voor bijwerkingen voorspellen via ATC-code
# Auteur: Faisal + ChatGPT

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="AI voor Bijwerkingen", layout="centered")

st.title("🧠 AI-voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Voer een **ATC-code** in en ontdek of het medicijn een kans heeft op:")
st.markdown("- ⚠️ Duizeligheid")
st.markdown("- ⚠️ Misselijkheid")
st.markdown("- ⚠️ Huiduitslag")

# 🔹 1. Dataset ophalen en voorbereiden
@st.cache_data
def load_data():
    # Laad de dataset (TSV-bestand)
    df = pd.read_table("meddra_freq.tsv", sep="\t")  # Gebruik sep="\t" voor tab-separated
    
    # Verwerk de bijwerkingen en voeg nieuwe kolommen toe
    df['Side Effect'] = df['Side Effect'].str.lower()
    df['has_dizziness'] = df['Side Effect'].str.contains('dizziness').astype(int)
    df['has_nausea'] = df['Side Effect'].str.contains('nausea').astype(int)
    df['has_rash'] = df['Side Effect'].str.contains('rash').astype(int)
    
    # Groepeer de data op ATC-code en bereken de aanwezigheid van bijwerkingen
    df_grouped = df.groupby('ATC Code').agg({
        'has_dizziness': 'max',
        'has_nausea': 'max',
        'has_rash': 'max'
    }).reset_index()
    
    df_grouped['ATC Code'] = df_grouped['ATC Code'].fillna('unknown')
    return df_grouped

data = load_data()

# 🔹 2. Model trainen per bijwerking
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data['ATC Code'])

models = {}
for effect in ['has_dizziness', 'has_nausea', 'has_rash']:
    y = data[effect]
    model = LogisticRegression()
    model.fit(X, y)
    models[effect] = model

# 🔹 3. Interface voor input
user_input = st.text_input("✏️ Voer ATC-code in (bijv. N02BE01):", value="N02BE01")

if user_input:
    x_new = vectorizer.transform([user_input.upper()])
    
    dizziness = models['has_dizziness'].predict(x_new)[0]
    nausea = models['has_nausea'].predict(x_new)[0]
    rash = models['has_rash'].predict(x_new)[0]
    
    st.subheader("📊 Voorspellingen:")
    st.markdown(f"- **Duizeligheid:** {'⚠️ Kans aanwezig' if dizziness else '✅ Waarschijnlijk niet'}")
    st.markdown(f"- **Misselijkheid:** {'⚠️ Kans aanwezig' if nausea else '✅ Waarschijnlijk niet'}")
    st.markdown(f"- **Huiduitslag:** {'⚠️ Kans aanwezig' if rash else '✅ Waarschijnlijk niet'}")
