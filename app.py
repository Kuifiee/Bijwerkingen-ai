import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# 🔹 1. Dataset ophalen en voorbereiden
@st.cache_data
def load_data():
    # Laad de datasets
    atc_data = pd.read_csv('drug_atc.tsv', sep='\t', header=None, names=['ATC Code', 'Drug'])
    drug_names = pd.read_csv('drug_names.tsv', sep='\t', header=None, names=['ATC Code', 'Drug Name'])
    side_effects_data = pd.read_csv('meddra_freq.tsv', sep='\t', header=None, names=['ATC Code', 'Side Effect', 'Frequency'])

    # Laat de eerste paar rijen van de bijwerkingen zien
    st.write("Voorbeeld van de bijwerkingen dataset:", side_effects_data.head())

    # Combineer de datasets
    df = pd.merge(atc_data, side_effects_data, on='ATC Code', how='inner')
    df = pd.merge(df, drug_names, on='ATC Code', how='inner')

    # Verwijder rijen met ontbrekende ATC-codes
    df = df.dropna(subset=['ATC Code'])
    df['ATC Code'] = df['ATC Code'].astype(str).str.strip()  # Verwijder eventuele spaties rondom de ATC-codes
    df = df[df['ATC Code'] != '']

    # Lijst van veelvoorkomende bijwerkingen (in Engels)
    symptoms = [
        'Pain', 'Anxiety', 'Fever', 'Cough', 'Nausea', 'Headache', 'Dizziness', 'Fatigue', 'Rash', 
        'Insomnia', 'Vomiting', 'Diarrhea', 'Constipation', 'Appetite loss', 'Depression', 'Cramps', 
        'Tremor', 'Chest pain', 'Back pain', 'Dyspepsia', 'Edema', 'Swelling', 'Sore throat', 'Dysphagia', 
        'Dizziness', 'Palpitations', 'Erythema', 'Bloating', 'Anorexia', 'Arthralgia', 'Myalgia', 'Dyspnea', 
        'Rhinorrhea', 'Coughing', 'Acne', 'Sore mouth', 'Sore tongue', 'Tinnitus', 'Dysmenorrhea', 
        'Nasal congestion', 'Stomach pain', 'Stomach upset', 'Alopecia', 'Dry mouth', 'Urinary retention', 
        'Urinary frequency', 'Urinary incontinence', 'Vision blurred', 'Malaise', 'Cystitis', 'Hyperhidrosis', 
        'Hypertension', 'Hypotension', 'Dehydration', 'Allergy', 'Liver dysfunction', 'Jaundice', 
        'Hearing loss', 'Weakness', 'Ringing in ears', 'GI upset', 'Sleep disturbances', 'Confusion', 
        'Tiredness', 'Gastritis', 'Gastrointestinal bleeding', 'Chronic pain', 'Shortness of breath', 
        'Elevated liver enzymes', 'Chills', 'Excessive thirst', 'Weight gain', 'Weight loss', 'Decreased libido', 
        'Joint pain', 'Myopathy', 'Hypersensitivity', 'Skin rash', 'Hives', 'Urticaria', 'Pneumonia', 
        'Fatigue', 'Blurred vision', 'Chest tightness', 'Erectile dysfunction', 'Seizures', 'Stroke', 
        'Tachycardia', 'Hypoglycemia', 'Hyperglycemia', 'Hemorrhage', 'Sialorrhea', 'Jaundice', 'Hypokalemia',
        'Hyperkalemia', 'Lymphadenopathy', 'Candidiasis', 'Polyuria', 'Polydipsia', 'Thrombocytopenia', 
        'Anemia', 'Leukopenia', 'Thrombosis', 'Hypothermia', 'Hyperthermia', 'Dyslipidemia', 'Alopecia', 
        'Peripheral edema', 'Syndrome of inappropriate antidiuretic hormone secretion (SIADH)', 'Miosis', 
        'Lacrimation', 'Hepatitis', 'Sickle cell crisis', 'Hematoma', 'Hematuria', 'Fainting', 'Cold extremities',
        'Shivering', 'Hypovolemia', 'Lethargy', 'Eosinophilia', 'Jaundice', 'Euphoria', 'Bradycardia'
    ]

    # Maak nieuwe kolommen voor elke bijwerking
    for symptom in symptoms:
        if symptom in df['Side Effect'].values:
            df[f'has_{symptom.lower().replace(" ", "_")}'] = df['Side Effect'].str.contains(symptom, case=False, na=False).astype(int)
        else:
            df[f'has_{symptom.lower().replace(" ", "_")}'] = 0  # Geen bijwerking aanwezig

    # Laat de gegevens zien van de nieuwe kolommen
    st.write("Voorbeeld van de gegevens met bijwerkingen:", df[['ATC Code', 'Side Effect'] + [f'has_{symptom.lower().replace(" ", "_")}' for symptom in symptoms]].head())

    # Groepeer op ATC-code en gebruik 'max' om aan te geven of een bijwerking aanwezig is
    df_grouped = df.groupby('ATC Code').agg({
        **{f'has_{symptom.lower().replace(" ", "_")}': 'max' for symptom in symptoms},
        'Drug Name': 'first'
    }).reset_index()

    return df_grouped

# 🔹 2. Modeltraining en bijwerkingenvoorspelling
def predict_side_effects(atc_code, model, vectorizer, df):
    if atc_code not in df['ATC Code'].values:
        return "De ATC-code is niet gevonden in de dataset. Probeer een andere code."

    # Haal de bijwerkingen op voor de gegeven ATC-code
    row = df[df['ATC Code'] == atc_code]
    side_effects = row.iloc[0, 2:]  # De bijwerkingen beginnen vanaf de derde kolom

    # Verkrijg de bijwerkingen die aanwezig zijn
    present_side_effects = [col.split('has_')[1].replace('_', ' ').capitalize() for col, val in side_effects.items() if val == 1]
    
    if present_side_effects:
        return f"Bijwerkingen voor ATC-code {atc_code}: {', '.join(present_side_effects)}"
    else:
        return "Er zijn geen bijwerkingen gevonden voor deze ATC-code."

# 🔹 3. Streamlit Interface
st.title('Bijwerkingen Voorspeller')

# Vraag de gebruiker om een ATC-code in te voeren
atc_code_input = st.text_input('Voer een ATC-code in:')

# Laad de gegevens
data = load_data()

# Voorspel bijwerkingen als er een ATC-code is ingevoerd
if atc_code_input:
    result = predict_side_effects(atc_code_input, None, None, data)
    st.write(result)
