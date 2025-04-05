import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="AI voor Bijwerkingen", layout="centered")

st.title("🧠 AI-voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Voer een **ATC-code** in en ontdek of het medicijn een kans heeft op:")
st.markdown("- ⚠️ Duizeligheid")
st.markdown("- ⚠️ Misselijkheid")
st.markdown("- ⚠️ Huiduitslag")

# 🔹 1. Dataset ophalen en voorbereiden
@st.cache_data
def load_data():
    atc_data = pd.read_csv('drug_atc.tsv', sep='\t', header=None, names=['ATC Code', 'Drug'])
    drug_names = pd.read_csv('drug_names.tsv', sep='\t', header=None, names=['ATC Code', 'Drug Name'])
    side_effects_data = pd.read_csv('meddra_freq.tsv', sep='\t', header=None, names=['ATC Code', 'Side Effect', 'Frequency'])

    df = pd.merge(atc_data, side_effects_data, on='ATC Code', how='inner')
    df = pd.merge(df, drug_names, on='ATC Code', how='inner')

    df = df.dropna(subset=['ATC Code'])
    df['ATC Code'] = df['ATC Code'].astype(str).str.strip()  # Verwijder eventuele spaties rondom de ATC-codes
    df = df[df['ATC Code'] != '']

    df['has_dizziness'] = df['Side Effect'].str.contains('dizziness', case=False, na=False).astype(int)
    df['has_nausea'] = df['Side Effect'].str.contains('nausea', case=False, na=False).astype(int)
    df['has_rash'] = df['Side Effect'].str.contains('rash', case=False, na=False).astype(int)

    df_grouped = df.groupby('ATC Code').agg({
        'has_dizziness': 'max',
        'has_nausea': 'max',
        'has_rash': 'max',
        'Drug Name': 'first'
    }).reset_index()

    return df_grouped

data = load_data()

# 🔹 2. LabelEncoder gebruiken voor ATC-codes
encoder = LabelEncoder()
data['ATC Code Encoded'] = encoder.fit_transform(data['ATC Code'])

# Train modellen voor de drie bijwerkingen
models = {}
for effect in ['has_dizziness', 'has_nausea', 'has_rash']:
    y = data[effect]
    X = data[['ATC Code Encoded']]  # Gebruik de gecodeerde ATC-code als invoer
    
    # Controleer of X en y geen lege waarden bevatten
    if X.empty or y.empty:
        st.error(f"Fout: De gegevens voor {effect} zijn leeg.")
        continue
    
    # Controleer de vormen van X en y
    st.write(f"Trainen voor effect: {effect}")
    st.write(f"Vorm van X: {X.shape}")
    st.write(f"Vorm van y: {y.shape}")
    
    try:
        model = LogisticRegression()
        model.fit(X, y)
        models[effect] = model
    except ValueError as e:
        st.error(f"Fout bij het trainen van het model voor {effect}: {e}")

# 🔹 3. Interface voor input
user_input = st.text_input("✏️ Voer ATC-code in (bijv. N02BE01):", value="N02BE01")

if user_input:
    user_input = user_input.upper()  # Zorg ervoor dat de invoer in hoofdletters is
    st.write(f"Gebruiker invoer: {user_input}")

    # Controleer of de ATC-code in de dataset staat
    if user_input in data['ATC Code'].values:
        st.write(f"Code gevonden in de dataset: {user_input}")
        
        # Haal de naam van het medicijn op
        drug_name = data[data['ATC Code'] == user_input]['Drug Name'].values[0]

        # Encodeer de gebruikersinvoer en voorspel de bijwerkingen
        user_input_encoded = encoder.transform([user_input])
        st.write(f"Geencodeerde ATC-code: {user_input_encoded[0]}")

        dizziness = models['has_dizziness'].predict([[user_input_encoded[0]]])[0]
        nausea = models['has_nausea'].predict([[user_input_encoded[0]]])[0]
        rash = models['has_rash'].predict([[user_input_encoded[0]]])[0]

        st.subheader(f"📊 Voorspellingen voor {drug_name}:")
        st.markdown(f"- **Duizeligheid:** {'⚠️ Kans aanwezig' if dizziness else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Misselijkheid:** {'⚠️ Kans aanwezig' if nausea else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Huiduitslag:** {'⚠️ Kans aanwezig' if rash else '✅ Waarschijnlijk niet'}")
    else:
        st.error("De ATC-code is niet gevonden in de dataset. Probeer een andere code.")
