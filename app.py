import streamlit as st
import pandas as pd
import plotly.express as px

# Pagina instellingen
st.set_page_config(page_title="Bijwerkingen AI", layout="wide")
st.title("💊 Bijwerkingen Verkenner Pro")
st.write("Typ een medicijnnaam of ATC-code om gerelateerde bijwerkingen te bekijken.")

# 📄 CSV-bestanden inladen
@st.cache_data(show_spinner=False)
def load_data():
    drug_df = pd.read_csv("drug_atc.csv")
    side_df = pd.read_csv("meddra_freq.csv")
    return drug_df, side_df

drug_df, side_df = load_data()

# 🔍 Live autosuggest zoekbalk
all_options = pd.concat([drug_df['drug'], drug_df['atc_code']]).dropna().unique().tolist()
query = st.text_input("Zoek op medicijnnaam of ATC-code:", placeholder="Bijv. Ibuprofen of A1B1C1")

# Alleen tonen als er input is
if query:
    # 🔎 Zoek naar overeenkomende medicijnen
    matches = drug_df[(drug_df['drug'].str.contains(query, case=False)) | (drug_df['atc_code'].str.contains(query, case=False))]

    if not matches.empty:
        for _, row in matches.iterrows():
            st.markdown("---")
            st.subheader(f"🔬 {row['drug']} ({row['atc_code']})")
            selected_cid = row['cid']

            # 📋 Toon bijwerkingen
            effects = side_df[side_df['cid'] == selected_cid]['side_effect'].tolist()
            if effects:
                st.markdown("**Mogelijke bijwerkingen:**")
                st.markdown("\n".join([f"- {effect}" for effect in effects]))

                # 📊 Toon grafiek
                chart_df = pd.DataFrame(effects, columns=['Bijwerking'])
                fig = px.histogram(chart_df, x='Bijwerking', title='Bijwerkingen overzicht')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Geen bijwerkingen gevonden.")
    else:
        st.error("Geen resultaten gevonden. Probeer een andere naam of ATC-code.")
else:
    st.info("Begin met typen om suggesties te krijgen en resultaten te zien.")
