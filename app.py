import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Bijwerkingen AI", layout="centered")

st.title("💊 Bijwerkingen Verkenner")

st.write("Zoek op een **medicijnnaam** of **ATC-code** om mogelijke bijwerkingen te zien.")

# 🔍 Zoekfunctie
query = st.text_input("Typ een medicijn of ATC-code:")

@st.cache_data(show_spinner=False)
def search_cid(drug_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
    r = requests.get(url)
    if r.status_code == 200 and "IdentifierList" in r.json():
        return r.json()["IdentifierList"]["CID"][0]
    return None

@st.cache_data(show_spinner=False)
def get_side_effects_from_sider(cid):
    # SIDER heeft een publieke dump, hier simuleren we een fetch uit een lokale of eigen API
    # Voor nu gebruiken we dummydata als voorbeeld
    dummy_data = {
        2244: ["nausea", "vomiting", "rash"],
        1983: ["headache", "dizziness"],
        3672: ["dry mouth", "fatigue", "insomnia"]
    }
    return dummy_data.get(cid, [])

@st.cache_data(show_spinner=False)
def get_pubchem_info(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        try:
            name = data["PC_Compounds"][0]["props"][0]["value"]["sval"]
            return name
        except:
            return "Naam onbekend"
    return "Naam onbekend"

# 👉 App logica
if query:
    with st.spinner("Zoeken naar informatie..."):
        cid = search_cid(query)
        if cid:
            drug_name = get_pubchem_info(cid)
            st.success(f"🧪 Gevonden stof: **{drug_name}** (CID: {cid})")
            side_effects = get_side_effects_from_sider(cid)

            if side_effects:
                st.subheader("📋 Mogelijke bijwerkingen")
                for effect in side_effects:
                    st.write(f"• {effect}")
            else:
                st.warning("Geen bijwerkingen gevonden in de dataset.")
        else:
            st.error("Geen gegevens gevonden. Probeer een andere naam of ATC-code.")
else:
    st.info("Voer een naam of ATC-code in om te starten.")
