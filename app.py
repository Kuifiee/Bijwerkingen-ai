import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Bijwerkingen AI", layout="centered")

st.title("💊 Bijwerkingen Verkenner")

@st.cache_data(show_spinner=False)
def load_data():
    drugs = pd.read_csv("drug_atc.csv")
    side_effects = pd.read_csv("meddra_freq.csv")
    return drugs, side_effects

drugs_df, side_effects_df = load_data()

# 🔍 Zoekbalk met live suggesties
query = st.text_input("Typ een medicijnnaam of ATC-code om bijwerkingen te zoeken:")

# Genereer suggesties tijdens het typen
if query:
    suggestions = drugs_df[drugs_df['name'].str.contains(query, case=False, na=False)]
    if not suggestions.empty:
        selected_drug = st.selectbox("Selecteer een medicijn:", suggestions["name"].unique())
    else:
        st.warning("Geen suggesties gevonden.")
        selected_drug = None
else:
    selected_drug = None

# 📊 Toon info wanneer iets is geselecteerd
if selected_drug:
    selected_data = drugs_df[drugs_df['name'] == selected_drug].iloc[0]
    cid = selected_data['cid']
    atc = selected_data['atc']

    st.success(f"🧪 Gevonden medicijn: **{selected_drug}** (ATC: {atc}, CID: {cid})")

    effects = side_effects_df[side_effects_df["cid"] == cid]["side_effect"].tolist()

    if effects:
        st.subheader("📋 Mogelijke bijwerkingen")
        for e in effects:
            st.write(f"• {e}")

        # 📈 Visualisatie
        effect_counts = pd.Series(effects).value_counts().reset_index()
        effect_counts.columns = ["Bijwerking", "Aantal"]

        fig = px.bar(effect_counts, x="Bijwerking", y="Aantal", title="Bijwerkingen visualisatie", color="Bijwerking")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Geen bijwerkingen gevonden voor dit medicijn.")
