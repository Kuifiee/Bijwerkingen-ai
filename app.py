import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bijwerkingen AI", layout="centered")
st.title("💊 Bijwerkingen Verkenner (Top 500 Geneesmiddelen)")

# 🔄 Data inladen
@st.cache_data
def load_data():
    df_drug = pd.read_csv("drug_atc.csv")
    df_se = pd.read_csv("meddra_freq.csv")
    merged = pd.merge(df_drug, df_se, on="cid")
    return df_drug, df_se, merged

df_drug, df_se, merged_df = load_data()

# 🔍 Autosuggest via textinput + dropdowns
st.subheader("🔎 Zoek medicijn of filter op kenmerken")
search_term = st.text_input("Typ een medicijnnaam of ATC-code").strip().lower()

filtered_df = merged_df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df["drug"].str.lower().str.contains(search_term) |
        filtered_df["atc_code"].str.lower().str.contains(search_term)
    ]

col1, col2 = st.columns(2)
with col1:
    selected_freq = st.selectbox("📈 Frequentie", ["-- Alles --"] + sorted(df_se["frequency"].unique()))
    if selected_freq != "-- Alles --":
        filtered_df = filtered_df[filtered_df["frequency"] == selected_freq]

with col2:
    selected_atc_prefix = st.selectbox("💊 ATC-code begint met", ["-- Alles --"] + sorted(set(df_drug["atc_code"].str[:3])))
    if selected_atc_prefix != "-- Alles --":
        filtered_df = filtered_df[filtered_df["atc_code"].str.startswith(selected_atc_prefix)]

# 📋 Resultaten
st.markdown(f"**Aantal resultaten:** {len(filtered_df)}")
st.dataframe(filtered_df, use_container_width=True)

# 📊 Grafiek
if not filtered_df.empty:
    fig = px.histogram(
        filtered_df,
        x="side_effect",
        color="frequency",
        title="Verdeling van bijwerkingen",
        labels={"side_effect": "Bijwerking"},
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# 🤖 Simulatie van AI-voorspelling
st.subheader("🤖 AI Voorspelling (simulatie)")

with st.expander("Klik om voorspelling te simuleren"):
    ai_input = st.text_input("Voer een ATC-code of CID in").strip().upper()

    if ai_input:
        import random
        example_effects = ["hoofdpijn", "misselijkheid", "vermoeidheid", "huiduitslag", "slaperigheid"]
        predicted = random.sample(example_effects, 3)
        st.markdown("### 📌 Voorspelde bijwerkingen")
        for effect in predicted:
            st.write(f"• {effect}")

# 📥 Export
st.download_button(
    "📥 Download huidige resultaten als CSV",
    data=filtered_df.to_csv(index=False),
    file_name="bijwerkingen_resultaten.csv",
    mime="text/csv"
)
