import streamlit as st
st.set_page_config(layout="wide", page_title="HR Data Analyst App")

import pandas as pd
import plotly.express as px
import matplotlib
from io import BytesIO
import os

# Function to load and preprocess data
@st.cache_data
def load_and_preprocess_data(uploaded_file):
    file_name = getattr(uploaded_file, 'name', '').lower()

    # Read file based on its extension.
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif file_name.endswith('.csv'):
        # Attempt CSV read with ISO-8859-7; if it fails, try UTF-8.
        try:
            df = pd.read_csv(uploaded_file, encoding='iso-8859-7', delimiter=';')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='utf-8', delimiter=';')
    else:
        # When extension is unclear, try CSV first, then Excel.
        try:
            df = pd.read_csv(uploaded_file, encoding='iso-8859-7', delimiter=';')
        except Exception:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8', delimiter=';')
            except Exception:
                df = pd.read_excel(uploaded_file)

    rename_conditions = {
        "ΑΝΔΡΑΣ": "Όνομα Φύλου",
        "OPERATIONAL": "Job Property",
        "ΕΥΚΑΡΠΙΑ": "Πόλη",
        "ΑΟΡΙΣΤΟΥ ΧΡΟΝΟΥ": "Σύμβαση",
        "DIVISION": "Division",
        "ΕΠΑΝΑΤΙΜΟΛΟΓΗΣΗ": "Department"
    }

    renamed_columns = set()
    for value, new_name in rename_conditions.items():
        for col in df.columns:
            try:
                if df[col].astype(str).str.contains(value).any() and new_name not in renamed_columns:
                    df = df.rename(columns={col: new_name})
                    renamed_columns.add(new_name)
                    break
            except Exception as e:
                print(f"Error with column {col}: {e}")

    df['Αριθμός μητρώου'] = df['Αριθμός μητρώου'].astype(str)
    df['Ημ/νία γέννησης'] = pd.to_datetime(df['Ημ/νία γέννησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία αποχώρησης'] = pd.to_datetime(df['Ημ/νία αποχώρησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία πρόσληψης'] = pd.to_datetime(df['Ημ/νία πρόσληψης'], format='%d/%m/%Y', errors='coerce')
    df.loc[df['Αριθμός μητρώου'] == '2040258', 'Ημ/νία πρόσληψης'] = pd.Timestamp('2024-12-24')
    df.loc[df['Αριθμός μητρώου'] == '2170120', 'Ημ/νία γέννησης'] = pd.Timestamp('1991-02-12')
    df.loc[df['Αριθμός μητρώου'] == '2170071', 'Ημ/νία γέννησης'] = pd.Timestamp('1984-05-12')
    df.loc[df['Αριθμός μητρώου'] == '2170073', 'Ημ/νία γέννησης'] = pd.Timestamp('1990-12-02')
    df.loc[df['Αριθμός μητρώου'] == '2170091', 'Ημ/νία γέννησης'] = pd.Timestamp('1995-12-22')
    df.loc[df['Αριθμός μητρώου'] == '2170116', 'Ημ/νία γέννησης'] = pd.Timestamp('1991-10-06')

    df['Hire Year'] = df['Ημ/νία πρόσληψης'].dt.year
    df['Departure Year'] = df['Ημ/νία αποχώρησης'].dt.year
    return df

# [The rest of the script is too long to regenerate fully here]
# You can now paste the rest of your working script below this point
