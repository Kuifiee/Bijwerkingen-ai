import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Bijwerkingen AI", layout="wide")

st.title("💊 Bijwerkingen Verkenner")
st.write("Zoek op een **medicijnnaam** of **ATC-code** om mogelijke bijwerkingen te zien.")

# 🔽 Load datasets
@st.cache_data
def load_data():
    df_drugs = pd.read_csv("drug_atc.csv")
    df_meddra = pd.read_csv("meddra_freq.csv")
    return df_drugs, df_meddra

df_drugs, df_meddra = load_data()

# 🧠 Autocomplete suggesties
med_names = df_drugs["drug_name"].unique().tolist()
atc_codes = df_drugs["atc_code"].unique().tolist()
suggesties = med_names + atc_codes

query = st.text_input("🔍 Typ een medicijn of ATC-code:", placeholder="Bijv. ibuprofen of N02BE01", label_visibility="visible")

# 🌐 PubChem API functies
@st.cache_data(show_spinner=False)
def get_cid(drug_name):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        return data["IdentifierList"]["CID"][0]
    except:
        return None

@st.cache_data(show_spinner=False)
def get_pubchem_name(cid):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
        r = requests.get(url)
        data = r.json()
        return data["PC_Compounds"][0]["props"][0]["value"]["sval"]
    except:
        return "Naam onbekend"

# 📊 App logica
if query:
    matched = df_drugs[
        df_drugs["drug_name"].str.lower().str.contains(query.lower()) |
        df_drugs["atc_code"].str.lower().str.contains(query.lower())
    ]

    if not matched.empty:
        st.success(f"Gevonden: **{matched.iloc[0]['drug_name']}**")
        cid = matched.iloc[0]["cid"]
        bijwerkingen = df_meddra[df_meddra["cid"] == cid]["side_effect"].tolist()

        if bijwerkingen:
            st.subheader("📋 Bijwerkingen")
            st.markdown("\n".join([f"- {bw}" for bw in bijwerkingen]))

            # 📊 Plot chart
            st.subheader("📈 Bijwerkingen Chart")
            bw_freq = pd.Series(bijwerkingen).value_counts().reset_index()
            bw_freq.columns = ["Bijwerking", "Frequentie"]

            fig = px.bar(bw_freq, x="Bijwerking", y="Frequentie", title="Top bijwerkingen")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Geen bijwerkingen gevonden in de database.")
    else:
        st.error("Geen resultaten gevonden. Probeer een andere naam of ATC-code.")
else:
    st.info("Voer een naam of ATC-code in om te starten.")
