import pandas as pd
import streamlit as st

# Functie om de data in te laden
@st.cache
def load_data():
    # Inladen van de datasets
    atc_data = pd.read_csv('drug_atc.tsv', sep='\t', header=None, names=['CID', 'ATC Code'])
    meddra_data = pd.read_csv('meddra_freq.tsv', sep='\t', header=None, names=['CID', 'Side Effect'])

    # Merge de twee datasets op de CID-code
    merged_data = pd.merge(atc_data, meddra_data, on='CID', how='left')
    
    return merged_data

# Laad de data
data = load_data()

# Titel van de app
st.title("Bijwerkingen per ATC-code")

# Vraag de gebruiker om een ATC-code in te voeren
atc_code = st.text_input("Voer de ATC-code in:")

# Functie om bijwerkingen te tonen op basis van de ATC-code
def get_side_effects(atc_code):
    # Filter de data op basis van de ATC-code
    filtered_data = data[data['ATC Code'] == atc_code]
    
    if not filtered_data.empty:
        # Toon de bijwerkingen
        side_effects = filtered_data['Side Effect'].unique()
        return ', '.join(side_effects)
    else:
        return "Geen bijwerkingen gevonden voor deze ATC-code."

# Toon bijwerkingen voor de ingevoerde ATC-code
if atc_code:
    side_effects = get_side_effects(atc_code)
    st.write(f"Bijwerkingen voor ATC-code {atc_code}:")
    st.write(side_effects)
