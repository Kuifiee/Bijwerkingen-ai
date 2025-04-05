import pandas as pd
import streamlit as st

# Zet de pagina-instellingen van de Streamlit-app
st.set_page_config(page_title="Voorspeller voor Geneesmiddelbijwerkingen", layout="centered")

st.title("🧠 Voorspeller voor Geneesmiddelbijwerkingen")
st.markdown("Voer een **ATC-code** of **medicijnnaam** in en ontdek of het medicijn een kans heeft op:")
st.markdown("- ⚠️ Duizeligheid")
st.markdown("- ⚠️ Misselijkheid")
st.markdown("- ⚠️ Huiduitslag")

@st.cache_data
def load_data():
    # Laad de datasets
    drug_names = pd.read_csv('drug_names.tsv', sep='\t', header=None, names=['drug_id', 'drug_name'])
    drug_atc = pd.read_csv('drug_atc.tsv', sep='\t', header=None, names=['drug_id', 'atc_code'])
    meddra_freq = pd.read_csv('meddra_freq.tsv', sep='\t', header=None, names=['cid1', 'cid2', 'atc_code', 'empty', 'percentage', 'value1', 'value2', 'llt', 'atc_code_duplicate', 'side_effect'])

    # Converteer naar kleine letters voor consistente zoekopdrachten
    drug_names['drug_name'] = drug_names['drug_name'].str.lower()
    meddra_freq['side_effect'] = meddra_freq['side_effect'].str.lower()

    return drug_names, drug_atc, meddra_freq

drug_names, drug_atc, meddra_freq = load_data()

# Gebruikersinvoer
user_input = st.text_input("✏️ Voer ATC-code of medicijnnaam in (bijv. N02BE01 of paracetamol):").strip().lower()

if user_input:
    # Controleer of de invoer een ATC-code is (meestal 7 tekens lang en begint met een letter)
    if len(user_input) == 7 and user_input[0].isalpha():
        atc_code = user_input.upper()
    else:
        # Zoek de drug_id op basis van de medicijnnaam
        drug_id_row = drug_names[drug_names['drug_name'] == user_input]
        if drug_id_row.empty:
            st.warning("Geen informatie gevonden voor deze medicijnnaam.")
            st.stop()
        drug_id = drug_id_row.iloc[0]['drug_id']

        # Zoek de ATC-code op basis van de drug_id
        atc_code_row = drug_atc[drug_atc['drug_id'] == drug_id]
        if atc_code_row.empty:
            st.warning("Geen ATC-code gevonden voor deze medicijnnaam.")
            st.stop()
        atc_code = atc_code_row.iloc[0]['atc_code']

    st.write(f"**Gevonden ATC-code:** {atc_code}")

    # Zoek bijwerkingen op basis van de ATC-code
    side_effects = meddra_freq[meddra_freq['atc_code'] == atc_code]['side_effect'].tolist()

    if not side_effects:
        st.warning("Geen bijwerkingen gevonden voor deze ATC-code.")
    else:
        # Controleer op specifieke bijwerkingen
        has_dizziness = any("dizziness" in effect for effect in side_effects)
        has_nausea = any("nausea" in effect for effect in side_effects)
        has_rash = any("rash" in effect for effect in side_effects)

        st.subheader("📊 Voorspellingen:")
        st.markdown(f"- **Duizeligheid:** {'⚠️ Kans aanwezig' if has_dizziness else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Misselijkheid:** {'⚠️ Kans aanwezig' if has_nausea else '✅ Waarschijnlijk niet'}")
        st.markdown(f"- **Huiduitslag:** {'⚠️ Kans aanwezig' if has_rash else '✅ Waarschijnlijk niet'}")

        with st.expander("📄 Alle gevonden bijwerkingen"):
            st.write(side_effects)
