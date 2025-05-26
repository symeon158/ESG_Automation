import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

# Function to load and preprocess data
@st.cache_data
def load_and_preprocess_data(main_file, contracts_file):
    file_name = getattr(main_file, 'name', '').lower()

    # Read main data
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(main_file)
    elif file_name.endswith('.csv'):
        try:
            df = pd.read_csv(main_file, encoding='iso-8859-7', delimiter=';')
        except UnicodeDecodeError:
            df = pd.read_csv(main_file, encoding='utf-8', delimiter=';')
    else:
        try:
            df = pd.read_csv(main_file, encoding='iso-8859-7', delimiter=';')
        except Exception:
            try:
                df = pd.read_csv(main_file, encoding='utf-8', delimiter=';')
            except Exception:
                df = pd.read_excel(main_file)

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

    # Read contracts
    if contracts_file is not None:
        contracts_df = pd.read_csv(contracts_file, encoding='iso-8859-7', delimiter=';')
    else:
        st.error("Please upload the Contracts.csv file.")
        st.stop()

    df['Αριθμός μητρώου'] = df['Αριθμός μητρώου'].astype(str).str.strip()
    contracts_df['Αριθμός μητρώου'] = contracts_df['Αριθμός μητρώου'].astype(str).str.strip()

    df = df.merge(
        contracts_df[['Αριθμός μητρώου', 'Σύμβαση']],
        on='Αριθμός μητρώου',
        how='left',
        suffixes=('', '_new')
    )

    df['Σύμβαση'] = df['Σύμβαση_new'].combine_first(df['Σύμβαση'])
    df.drop(columns=['Σύμβαση_new'], inplace=True)

    df['Ημ/νία γέννησης'] = pd.to_datetime(df['Ημ/νία γέννησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία αποχώρησης'] = pd.to_datetime(df['Ημ/νία αποχώρησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία πρόσληψης'] = pd.to_datetime(df['Ημ/νία πρόσληψης'], format='%d/%m/%Y', errors='coerce')

    df['Hire Year'] = df['Ημ/νία πρόσληψης'].dt.year
    df['Departure Year'] = df['Ημ/νία αποχώρησης'].dt.year
    return df



st.markdown("## 📊 HR Data Analyst Dashboard")

main_file = st.file_uploader("Upload main employee data file", type=['csv', 'xlsx'])
contracts_file = st.file_uploader("Upload Contracts.csv", type='csv')

if main_file and contracts_file:
    df = load_and_preprocess_data(main_file, contracts_file)
    st.success("✅ Data loaded successfully!")
    st.dataframe(df.head())
else:
    st.warning("Please upload both the main file and Contracts.csv.")
