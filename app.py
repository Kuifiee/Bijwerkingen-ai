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
    # Laad de ATC-codes, medicijnnamen en bijwerkingen data
    atc_data = pd.read_csv('drug_atc.tsv', sep='\t', header=None, names=['ATC Code', 'Drug'])
    drug_names = pd.read_csv('drug_names.tsv', sep='\t', header=None, names=['ATC Code', 'Drug Name'])
    side_effects_data = pd.read_csv('meddra_freq.tsv', sep='\t', header=None, names=['ATC Code', 'Side Effect', 'Frequency'])

    # Combineer de dataframes op de ATC Code
    df = pd.merge(atc_data, side_effects_data, on='ATC Code', how='inner')
    df = pd.merge(df, drug_names, on='ATC Code', how='inner')

    # Verwijder eventuele lege ATC-codes en andere mogelijke ongeldige waarden
    df = df.dropna(subset=['ATC Code'])
    
    # Filter op geldige ATC-codes (zorg ervoor dat het geen lege of ongeldige codes zijn)
    df['ATC Code'] = df['ATC Code'].astype(str).str.strip()  # Verwijder eventuele spaties rondom de ATC-codes
    df = df[df['ATC Code'] != '']  # Verwijder lege ATC-codes

    # Voeg bijwerkingen toe als indicatoren
    df['has_dizziness'] = df['Side Effect'].str.contains('dizziness', case=False, na=False).astype(int)
    df['has_nausea'] = df['Side Effect'].str.contains('nausea', case=False, na=False).astype(int)
    df['has_rash'] = df['Side Effect'].str.contains('rash', case=False, na=False).astype(int)

    # Groepeer per ATC Code en voeg de bijwerkingen samen
    df_grouped = df.groupby('ATC Code').agg({
        'has_dizziness': 'max',
        'has_nausea': 'max',
        'has_rash': 'max',
        'Drug Name': 'first'  # Zorg ervoor dat de naam van het medicijn behouden blijft
    }).reset_index()
    
    return df_grouped

data = load_data()

# 🔹 2. Model trainen per bijwerking
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data['ATC Code'].astype(str))  # Zorg ervoor dat de ATC-code als string wordt behandeld

models = {}
for effect in ['has_dizziness', 'has_nausea', 'has_rash']:
    y = data[effect]
    model = LogisticRegression()
    model.fit(X, y)
    models[effect] = model

# 🔹 3. Interface voor input
user_input = st.text_input("✏️ Voer ATC-code in (bijv. N02BE01):", value="N02BE01")

if user_input:
    user_input = user_input.upper()  # Zorg ervoor dat de invoer in hoofdletters is

    # Controleer of de ATC-code in de dataset staat
    if user_input in data['ATC Code'].values:
        # Haal de naam van het medicijn op
        drug_name = data[data['ATC Code'] == user_input]['Drug Name'].values[0]

        # Voorspel de bijwerkingen
        x_new = vectorizer.transform([user_input])
        
        dizziness = models['has_dizziness'].predict(x_new)[0]
        nausea = models['has_nausea'].predict(x_new)[0]
        rash = models['has_rash'].predict(x_new)[0]
        
        st.subheader(f"📊 Voorspellingen voor {drug_name}:")
        st.markdown(f"- **Duizeligheid:** {'⚠️ Kans aanwezig' if dizziness else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Misselijkheid:** {'⚠️ Kans aanwezig' if nausea else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Huiduitslag:** {'⚠️ Kans aanwezig' if rash else '✅ Waarschijnlijk niet'}")
    else:
        st.error("De ATC-code is niet gevonden in de dataset. Probeer een andere code.")
