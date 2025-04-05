import pandas as pd
import streamlit as st

# Laad de bestanden
drug_atc = pd.read_csv('drug_atc.tsv', sep='\t')
meddra_freq = pd.read_csv('meddra_freq.tsv', sep='\t')

# Zorg ervoor dat de CIDs als strings worden behandeld, en verwijder eventuele extra witruimtes
drug_atc['CID'] = drug_atc['CID'].astype(str).str.strip()
meddra_freq['CID'] = meddra_freq['CID'].astype(str).str.strip()

# Functie om bijwerkingen op te halen voor een ATC-code
def get_side_effects_for_atc_code(atc_code):
    # Krijg de CIDs die bij de ATC-code horen
    cids_for_atc = drug_atc[drug_atc['ATC Code'] == atc_code]['CID'].unique()
    
    # Filter de bijwerkingen uit de meddra_freq dataset die overeenkomen met de CIDs
    effects = meddra_freq[meddra_freq['CID'].isin(cids_for_atc)]
    
    if not effects.empty:
        # Geef de unieke bijwerkingen voor deze ATC-code
        return effects['Side Effect'].unique()
    else:
        return "Geen bijwerkingen gevonden voor deze ATC-code."

# Streamlit app
st.title('Bijwerkingen Zoeker')

# Vraag om ATC-code in te voeren
atc_code_input = st.text_input("Voer een ATC-code in (bijvoorbeeld A01):")

if atc_code_input:
    # Krijg bijwerkingen voor de ingevoerde ATC-code
    side_effects = get_side_effects_for_atc_code(atc_code_input)
    
    # Toon de bijwerkingen of een foutmelding
    st.write("Bijwerkingen voor ATC-code ", atc_code_input, ":")
    if isinstance(side_effects, str):  # Geen bijwerkingen gevonden
        st.error(side_effects)
    else:
        for effect in side_effects:
            st.write(f"- {effect}")
