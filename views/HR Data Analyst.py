import streamlit as st
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

   
    df['Ημ/νία γέννησης'] = pd.to_datetime(df['Ημ/νία γέννησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία αποχώρησης'] = pd.to_datetime(df['Ημ/νία αποχώρησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία πρόσληψης'] = pd.to_datetime(df['Ημ/νία πρόσληψης'], format='%d/%m/%Y', errors='coerce')
     

    df['Hire Year'] = df['Ημ/νία πρόσληψης'].dt.year
    df['Departure Year'] = df['Ημ/νία αποχώρησης'].dt.year
    
    # Rename "Κωδικός εργαζόμενου" to "Αριθμός μητρώου" if it exists
    if 'Κωδικός εργαζόμενου' in df.columns and 'Αριθμός μητρώου' not in df.columns:
        df = df.rename(columns={'Κωδικός εργαζόμενου': 'Αριθμός μητρώου'})
    df['Αριθμός μητρώου'] = df['Αριθμός μητρώου'].astype(str)
    # Translate contract type values in "Σύμβαση"
    if 'Σύμβαση' in df.columns:
        df['Σύμβαση'] = df['Σύμβαση'].replace({
            'PERMANENT': 'ΑΟΡΙΣΤΟΥ ΧΡΟΝΟΥ',
            'TEMPORARY': 'ΟΡΙΣΜΕΝΟΥ ΧΡΟΝΟΥ'
        })
        
    return df

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Custom HTML and CSS for the header
header_html = """
<div style="background: linear-gradient(to right, #0066CC, #3399FF); padding: 20px; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
    <h1 style="color: white; text-align: center; font-family: 'Verdana', sans-serif; font-size: 36px;">
        📊 HR Data Analyst 📈
    </h1>
    <p style="color: white; text-align: center; font-size: 20px; font-family: 'Verdana', sans-serif;">
        Leveraging Data to Drive Strategic HR Decisions
    </p>
</div>
"""

# Display the header in the Streamlit app
st.markdown(header_html, unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader('Choose a CSV file', type='csv')

# Load and store data in session state
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.df = load_and_preprocess_data(uploaded_file)
if 'file_saved' not in st.session_state:
    st.session_state.file_saved = False

    
# Check if data is available in session state
import os

if st.session_state.df is not None:
    df = st.session_state.df.copy()
    df['Αριθμός μητρώου'] = df['Αριθμός μητρώου'].astype(str).str.strip()

    # Safe numeric conversion
    if df['Ονομαστικός μισθός'].dtype == 'object':
        df['Ονομαστικός μισθός'] = pd.to_numeric(
            df['Ονομαστικός μισθός'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        )
    else:
        df['Ονομαστικός μισθός'] = pd.to_numeric(df['Ονομαστικός μισθός'], errors='coerce')

    # Salary adjustment
    # Define all day-rate contract types
    day_rate_contracts = {
        'ΑΛΜ - ΗΜΕΡΟΜΙΣΘΙΟΙ',
        'ΜΕΤΑΛΛΟΥ ΗΜΕΡΟΜΙΣΘΙΟΙ 1Η ΚΑΤΗΓΟΡΙΑ',
        'ΜΕΤΑΛΛΟΥ ΗΜΕΡΟΜΙΣΘΙΟΙ 2Η ΚΑΤΗΓΟΡΙΑ'
    }
    
    # Multiply nominal salary ×26 only for those
    df['Ονομαστικός μισθός'] = df.apply(
        lambda row: row['Ονομαστικός μισθός'] * 26
        if str(row.get('Περιγραφή Σύμβασης', '')).strip().upper() in day_rate_contracts
        else row['Ονομαστικός μισθός'],
        axis=1
    )


    

    # Replace dots with commas in numeric columns before saving
    df_to_save = df.copy()
    df_to_save['Ονομαστικός μισθός'] = df_to_save['Ονομαστικός μισθός'].apply(
        lambda x: f"{x:.2f}".replace('.', ',') if pd.notnull(x) else ''
    )

    from io import BytesIO
    output = BytesIO()
    df_to_save.to_csv(output, index=False, encoding='iso-8859-7', sep=';')
    st.download_button(
        label="Download CSV",
        data=output.getvalue(),
        file_name="updated_file.csv",
        mime="text/csv",
    )

    original_filename = getattr(st.session_state.uploaded_file, 'name', 'ESG_2025.csv')

    # Save locally with commas instead of dots
    local_save_path = r"C:\Users\sy.papadopoulos\OneDrive - Alumil S.A\Desktop\Esg Group"
    filename = "ESG 2025.csv"
    full_path = os.path.join(local_save_path, original_filename)

    if not os.path.exists(local_save_path):
        os.makedirs(local_save_path)

    if not st.session_state.file_saved:
        df_to_save.to_csv(full_path, index=False, encoding='iso-8859-7', sep=';')
        st.session_state.file_saved = True
    # st.success(f"File successfully saved locally at: {full_path}")


    #st.success(f"File successfully saved locally at: {full_path}")



    tab1, tab2 = st.tabs(["🧍Headcount", "🚶‍➡️Hires and Departures🚶"])

    # Common settings
    # Sidebar for settings
    st.sidebar.header('Settings')
    exclude_input = st.sidebar.text_area('Exclude Set (comma-separated)', '1015791, 1015535, 1015956, 1015307, 1016492, 1017069, 1017070, 1017501, 1017508, 1100096, 1200014, 1200030')
    exclude_set = set(exclude_input.split(', '))
    year_input = st.sidebar.number_input('Year', value=2025, min_value=2000, max_value=2100, step=1)
    year_input_2 = st.sidebar.number_input('Year for Hires & Departures', value=2025, min_value=2000, max_value=2100, step=1)
    selected_date = st.sidebar.date_input("Select a reference date for age group", value=pd.to_datetime('2025-12-31'))
    # Sidebar Input for Exclusion
    exclude_input_departures = st.sidebar.text_area('Exclude Set for Departures (comma-separated)', 
    "1015768, 1015903, 1016610, 1017066, 1017182, "
    "1017247, 1017255, 1018277, 1011285, 1017525, "
    "1015710, 1017200, 1017346, 1017471, 1017475, "
    "1017476, 1017477, 1017478, 1017479, 1017480, 1017482, "
    "1017483, 1017484, 1017485, 1017512, 1017668, 1017622, 1017578"
) 

    # Convert input into a set of IDs (strip to remove any accidental spaces)
    exclude_set_departures = set(map(str.strip, exclude_input_departures.split(',')))

    

    # Recalculate age based on selected date
    reference_date = pd.Timestamp(selected_date)
    df['Age as of Selected Date'] = (reference_date - df['Ημ/νία γέννησης']).dt.days // 365

    bins = [-1, 29, 50, float('inf')]
    labels = ['<30', '30-50', '>50']
    df['Age Group'] = pd.cut(df['Age as of Selected Date'], bins=bins, labels=labels)

    with tab1:
        st.sidebar.header('Grouping Criteria')
        group_columns = st.sidebar.multiselect(
            'Select columns to group by:',
            options=['Περιγραφή εταιρίας', 'Πόλη', 'Division', 'Department', 'Job Property','Όνομα Φύλου', 'Σύμβαση', 'Age Group']
        )
        # Filter Criteria
        st.sidebar.header('Filter Criteria')
        selected_companies = st.sidebar.multiselect('Select Companies:', options=df['Περιγραφή εταιρίας'].unique(), key='companies_main')
        selected_cities = st.sidebar.multiselect('Select Cities:', options=df['Πόλη'].unique(), key='cities_main')
        selected_divisions = st.sidebar.multiselect('Select Division:', options=df['Division'].unique(), key='division_main')
        selected_departments = st.sidebar.multiselect('Select Department:', options=df['Department'].unique(), key='department_main')
        selected_genders = st.sidebar.multiselect('Select Genders:', options=df['Όνομα Φύλου'].unique(), key='genders_main')
        selected_property = st.sidebar.multiselect('Select Job Property:', options=df['Job Property'].unique(), key='property_main')
        selected_contracts = st.sidebar.multiselect('Select Contracts:', options=df['Σύμβαση'].unique(), key='contracts_main')
        selected_age_groups = st.sidebar.multiselect('Select Age Groups:', options=df['Age Group'].unique(), key='age_groups_main')

        filtered_df = df[
    # Exclude rows based on 'Αριθμός μητρώου'
    ~df['Αριθμός μητρώου'].isin(exclude_set) &
    
    # Ensure 'Ημ/νία πρόσληψης' is not null and less than 'year_input'
    (df['Ημ/νία πρόσληψης'].notna() & (df['Ημ/νία πρόσληψης'].dt.year <= year_input)) &

    # 'Ημ/νία αποχώρησης' is either null or its year is less than 'year_input'
    (df['Ημ/νία αποχώρησης'].isna() | (df['Ημ/νία αποχώρησης'].dt.year > year_input))
]

        total_count = filtered_df.shape[0]
        if selected_companies:
            filtered_df = filtered_df[filtered_df['Περιγραφή εταιρίας'].isin(selected_companies)]
        if selected_cities:
            filtered_df = filtered_df[filtered_df['Πόλη'].isin(selected_cities)]
        if selected_divisions:
            filtered_df = filtered_df[filtered_df['Division'].isin(selected_divisions)]
        if selected_departments:
            filtered_df = filtered_df[filtered_df['Department'].isin(selected_departments)]
        if selected_genders:
            filtered_df = filtered_df[filtered_df['Όνομα Φύλου'].isin(selected_genders)]
        if selected_property:
            filtered_df = filtered_df[filtered_df['Job Property'].isin(selected_property)]
        if selected_contracts:
            filtered_df = filtered_df[filtered_df['Σύμβαση'].isin(selected_contracts)]
        if selected_age_groups:
            filtered_df = filtered_df[filtered_df['Age Group'].isin(selected_age_groups)]
            filtered_df['Age Group'] = filtered_df['Age Group'].cat.remove_unused_categories()

        count = filtered_df.shape[0]

        col1, col2 = st.columns(2)
        with col2:
            st.markdown(f"""
                <style>
                .card {{
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                .card-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                }}
                .card-value {{
                    font-size: 40px;
                    font-weight: bold;
                    color: #007BFF;
                }}
                </style>
                <div class="card">
                    <div class="card-title">Count Criteria</div>
                    <div class="card-value">{count}</div>
                </div>
            """, unsafe_allow_html=True)

        with col1:
            st.markdown(f"""
                <style>
                .card {{
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    position: relative;
                }}

                .card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 5px;
                    height: 100%;
                    background-color: #007BFF;
                    border-radius: 10px 0 0 10px;
                }}

                .card-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                }}

                .card-value {{
                    font-size: 40px;
                    font-weight: bold;
                    color: #007BFF;
                }}
                </style>
                <div class="card">
                    <div class="card-title">Total Number of Rows</div>
                    <div class="card-value">{total_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with st.expander('DataFrame:'):
            st.write(filtered_df)

        # st.sidebar.header('Grouping Criteria')
        # group_columns = st.sidebar.multiselect(
        #     'Select columns to group by:',
        #     options=['Περιγραφή εταιρίας', 'Πόλη', 'Division', 'Department', 'Job Property','Όνομα Φύλου', 'Σύμβαση', 'Age Group']
        # )

        if group_columns:
            grouped_df = filtered_df.groupby(group_columns)['Αριθμός μητρώου'].count().reset_index()
            grouped_df = grouped_df.sort_values(by='Αριθμός μητρώου', ascending=False)
            grouped_df.rename(columns={'Αριθμός μητρώου': 'Count'}, inplace=True)
            
            with st.expander('Grouped DataFrame:'):
                st.write(grouped_df)

            if not grouped_df.empty:
                if len(group_columns) == 1:
                    fig = px.bar(
                        grouped_df, 
                        x=group_columns[0], 
                        y='Count', 
                        color=group_columns[0], 
                        title='Grouped Data Column Chart',
                        labels={'Count': 'Number of Records', group_columns[0]: group_columns[0]}
                    )
                else:
                    fig = px.bar(
                        grouped_df, 
                        x=group_columns[0], 
                        y='Count', 
                        color=group_columns[1] if len(group_columns) > 1 else group_columns[0], 
                        barmode='stack', 
                        title='Grouped Data Column Chart',
                        labels={'Count': 'Number of Records', group_columns[0]: group_columns[0]}
                    )
                    if len(group_columns) > 2:
                        fig.update_layout(
                            legend_title_text=group_columns[1],
                            xaxis_title=group_columns[0],
                            yaxis_title='Count',
                            barmode='stack'
                        )

                st.plotly_chart(fig)
            else:
                st.warning('The grouped DataFrame is empty. Please adjust your filters.')
        else:
            st.warning('Please select at least one grouping criteria to generate the plot.')


    

        # Ensure required columns exist
        required_cols = ['Εταιρία', 'Περιγραφή Θέσης Εργασίας', 'Job Property', 'Όνομα Φύλου']
        if all(col in filtered_df.columns for col in required_cols):

            # Keep only Company 101
            df_101 = filtered_df[filtered_df['Εταιρία'] == 101].copy()

            # Ensure string operations don’t break
            df_101['Περιγραφή Θέσης Εργασίας'] = df_101['Περιγραφή Θέσης Εργασίας'].astype(str).str.lower()
            df_101['Job Property'] = df_101['Job Property'].astype(str).str.lower()

            # Define role categories
            def classify_role(row):
                title = row['Περιγραφή Θέσης Εργασίας'].lower()
                prop = row['Job Property'].lower()
                raw_grade = row.get('GRADE', '0')

                try:
                    grade = float(str(raw_grade).replace(',', '.'))
                except (ValueError, TypeError):
                    grade = 0

                if 'trainee' in title:
                    return 'Trainee'
                elif 'director' in title:
                    return 'Director'
                elif 'commercial unit developer' in title and grade > 16:
                    return 'Manager'
                elif ('manager' in title or 'head' in title or 'ceo' in title) and grade >= 18:
                    return 'Director'
                elif ('manager' in title or 'head' in title or 'supervisor' in title or 'lead' in title or 'executive' in title) and grade > 13:
                    return 'Manager'
                elif prop == 'administrative':
                    return 'Office Worker'
                elif prop == 'operational':
                    return 'Worker'
                else:
                    return None



            # Apply classification
            df_101['Role Category'] = df_101.apply(classify_role, axis=1)

            # Keep only classified rows
            role_df = df_101[df_101['Role Category'].notnull()]

            # Group and count
            role_summary = (
                role_df
                .groupby(['Role Category', 'Περιγραφή Θέσης Εργασίας', 'Αριθμός μητρώου', 'Όνομα Φύλου', 'Επώνυμο', 'Ονομα', 'GRADE'])
                .size()
                .reset_index(name='Count')
            )

            
            # Group by Gender and Role Category
            gender_total = (
                role_summary
                .groupby(['Όνομα Φύλου', 'Role Category'])['Count']
                .sum()
                .reset_index()
                .rename(columns={'Count': 'Total by Group'})
            )

            # Calculate grand total for all groups (for percentage)
            grand_total = gender_total['Total by Group'].sum()

            # Add percentage of grand total
            gender_total['% of Grand Total'] = (
                gender_total['Total by Group'] / grand_total * 100
            ).round(2)


            # Display results
            st.markdown("""
                <div style="background-color: #f1f1f1; padding: 15px 25px; border-left: 5px solid #007BFF;
                            border-radius: 8px; margin-top: 20px; margin-bottom: 10px;
                            font-family: 'Segoe UI', sans-serif;">
                    <h3 style="color: #007BFF; margin: 0;">👥 Staff Breakdown by Role Category (Company 101)</h3>
                    <p style="color: #444; margin: 5px 0 0;">Grouped by Role Category and Gender</p>
                </div>
            """, unsafe_allow_html=True)

            st.dataframe(role_summary)

            st.write("Summary by Gender:")
            st.dataframe(gender_total)



        
        # Additional Table: Group by specific columns where GRADE >= 18
        if 'GRADE' in filtered_df.columns and 'Ονομα' in filtered_df.columns:
            filtered_df['GRADE'] = pd.to_numeric(filtered_df['GRADE'], errors='coerce')

            # Filter GRADE >= 18
            grade_filtered_df = filtered_df[filtered_df['GRADE'] >= 18]

            # Group and count
            group_table = (
                grade_filtered_df
                .groupby(['Περιγραφή εταιρίας', "Όνομα Φύλου", 'Επώνυμο', 'Ονομα', 'Αριθμός μητρώου', 'GRADE', 'Περιγραφή Θέσης Εργασίας'])
                .agg({'Ονομα': 'count'})
                .rename(columns={'Ονομα': 'Count'})
                .reset_index()
            )

            # Compute total by gender
            gender_summary = (
                group_table
                .groupby("Όνομα Φύλου")['Count']
                .sum()
                .reset_index()
                .rename(columns={'Count': 'Total by Gender'})
            )

            # Calculate grand total
            grand_total = gender_summary['Total by Gender'].sum()

            # Add percentage column
            gender_summary['% of Grand Total'] = (gender_summary['Total by Gender'] / grand_total * 100).round(2)

            # Display results
            st.markdown("""
                    <div style="background-color: #f9f9f9; padding: 15px 25px; border-left: 5px solid #007BFF;
                                border-radius: 8px; margin-top: 20px; margin-bottom: 10px;
                                font-family: 'Segoe UI', sans-serif;">
                        <h3 style="color: #007BFF; margin: 0;">👔 High Executives (GRADE ≥ 18)</h3>
                        <p style="color: #555; margin: 5px 0 0;">Overview of senior staff by company, gender, and role</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.dataframe(group_table)

            st.write("Summary by Gender:")
            st.dataframe(gender_summary)

    with tab2:
        st.header("Hires and Departures")

        # Filter Criteria for Hires and Departures
        st.sidebar.header('Grouping Criteria for Hires and Departures')
        group_columns_hd_2 = st.sidebar.multiselect(
            'Select columns for Hires to group by:',
            options=['Περιγραφή εταιρίας','Πόλη', 'Όνομα Φύλου', 'Age Group'],
            key='group_columns_hd_2'
        )

        group_columns_hd = st.sidebar.multiselect(
            'Select columns for Departures to group by:',
            options=['Περιγραφή εταιρίας','Πόλη', 'Όνομα Φύλου', 'Age Group', 'Περιγραφή Αιτ. Αποχώρησης'],
            key='group_columns_hd'
        )

        st.sidebar.header('Filter Criteria for Hires and Departures')
        selected_companies_hd = st.sidebar.multiselect('Select Companies:', options=df['Περιγραφή εταιρίας'].unique(), key='companies_hd')
        selected_cities_hd = st.sidebar.multiselect('Select Cities:', options=df['Πόλη'].unique(), key='cities_hd')
        selected_genders_hd = st.sidebar.multiselect('Select Genders:', options=df['Όνομα Φύλου'].unique(), key='genders_hd')
        selected_age_groups_hd = st.sidebar.multiselect('Select Age Groups:', options=df['Age Group'].cat.categories.tolist(), key='age_groups_hd')
        selected_departure_reasons = st.sidebar.multiselect('Select Departure Reasons:', options=df['Περιγραφή Αιτ. Αποχώρησης'].unique(), key='departure_reasons_hd')

        # General filtering (applied to both hires and departures)
        filtered_df_hd = df[~df['Αριθμός μητρώου'].isin(exclude_set)]
        if selected_companies_hd:
            filtered_df_hd = filtered_df_hd[filtered_df_hd['Περιγραφή εταιρίας'].isin(selected_companies_hd)]
        if selected_cities_hd:
            filtered_df_hd = filtered_df_hd[filtered_df_hd['Πόλη'].isin(selected_cities_hd)]
        if selected_genders_hd:
            filtered_df_hd = filtered_df_hd[filtered_df_hd['Όνομα Φύλου'].isin(selected_genders_hd)]
        if selected_age_groups_hd:
            filtered_df_hd = filtered_df_hd[filtered_df_hd['Age Group'].isin(selected_age_groups_hd)]
            filtered_df_hd['Age Group'] = filtered_df_hd['Age Group'].cat.remove_unused_categories()

        # Hires filtering (exclude "Περιγραφή Αιτ. Αποχώρησης" filter)
        hires_df = filtered_df_hd[filtered_df_hd['Hire Year'] == year_input_2]
        hires = hires_df.shape[0]

        # Filter departures based on the selected year and exclude the specified IDs
        departures_df = filtered_df_hd[
            (filtered_df_hd['Departure Year'] == year_input_2) &
            ~filtered_df_hd['Αριθμός μητρώου'].astype(str).isin(exclude_set_departures)
        ]

        if selected_departure_reasons:
            departures_df = departures_df[departures_df['Περιγραφή Αιτ. Αποχώρησης'].isin(selected_departure_reasons)]
        departures = departures_df.shape[0]

        # Display cards for hires and departures
        col1_hd, col2_hd = st.columns(2)
        with col1_hd:
            st.markdown(f"""
                <style>
                .card {{
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                .card-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                }}
                .card-value {{
                    font-size: 40px;
                    font-weight: bold;
                    color: #007BFF;
                }}
                </style>
                <div class="card">
                    <div class="card-title">Hires in {year_input_2}</div>
                    <div class="card-value">{hires}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2_hd:
            st.markdown(f"""
                <style>
                .card {{
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                .card-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #333;
                }}
                .card-value {{
                    font-size: 40px;
                    font-weight: bold;
                    color: #007BFF;
                }}
                </style>
                <div class="card">
                    <div class="card-title">Departures in {year_input_2}</div>
                    <div class="card-value">{departures}</div>
                </div>
            """, unsafe_allow_html=True)

        # Grouping and plotting for hires
        # st.sidebar.header('Grouping Criteria for Hires and Departures')
        # group_columns_hd_2 = st.sidebar.multiselect(
        #     'Select columns for Hires to group by:',
        #     options=['Περιγραφή εταιρίας','Πόλη', 'Όνομα Φύλου', 'Age Group'],
        #     key='group_columns_hd_2'
        # )

        if group_columns_hd_2:
            hires_grouped_df_hd = hires_df.groupby(group_columns_hd_2)['Αριθμός μητρώου'].count().reset_index()
            hires_grouped_df_hd.rename(columns={'Αριθμός μητρώου': 'Count'}, inplace=True)
            
            with st.expander('Grouped DataFrame for Hires:'):
                st.write(hires_grouped_df_hd)

            if not hires_grouped_df_hd.empty:
                fig_hd_hires = px.bar(
                    hires_grouped_df_hd,
                    x=group_columns_hd_2[0],
                    y='Count',
                    color=group_columns_hd_2[0] if len(group_columns_hd_2) == 1 else group_columns_hd_2[1],
                    title='Grouped Data Column Chart for Hires',
                    labels={'Count': 'Number of Hires', group_columns_hd_2[0]: group_columns_hd_2[0]}
                )
                st.plotly_chart(fig_hd_hires)
        else:
            st.warning('Please select at least one grouping criteria for Hires to generate the plot.')

        # Grouping and plotting for departures
        #   

        if group_columns_hd:
            departures_grouped_df_hd = departures_df.groupby(group_columns_hd)['Αριθμός μητρώου'].count().reset_index()
            departures_grouped_df_hd.rename(columns={'Αριθμός μητρώου': 'Count'}, inplace=True)
            
            with st.expander('Grouped DataFrame for Departures:'):
                st.write(departures_grouped_df_hd)

            if not departures_grouped_df_hd.empty:
                fig_hd_departures = px.bar(
                    departures_grouped_df_hd,
                    x=group_columns_hd[0],
                    y='Count',
                    color=group_columns_hd[0] if len(group_columns_hd) == 1 else group_columns_hd[1],
                    title='Grouped Data Column Chart for Departures',
                    labels={'Count': 'Number of Departures', group_columns_hd[0]: group_columns_hd[0]}
                )
                st.plotly_chart(fig_hd_departures)
        else:
            st.warning('Please select at least one grouping criteria for Departures to generate the plot.')

else:
    st.write('Please upload a CSV file to proceed.')





