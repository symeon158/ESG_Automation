import streamlit as st
import pandas as pd
import plotly.express as px
import math


# Unique key for the Compensation & Benefits page
COMP_PAGE_KEY = 'Comp_Ben'

# Function to load and preprocess data
@st.cache_data
def load_and_preprocess_data(uploaded_file):
    df = pd.read_csv(uploaded_file, encoding='iso-8859-7', delimiter=';')

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
            if df[col].astype(str).str.contains(value).any() and new_name not in renamed_columns:
                df = df.rename(columns={col: new_name})
                renamed_columns.add(new_name)
                break

                
    df['Αριθμός μητρώου'] = df['Αριθμός μητρώου'].astype(str)
    df['Ημ/νία γέννησης'] = pd.to_datetime(df['Ημ/νία γέννησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία αποχώρησης'] = pd.to_datetime(df['Ημ/νία αποχώρησης'], format='%d/%m/%Y', errors='coerce')
    df['Ημ/νία πρόσληψης'] = pd.to_datetime(df['Ημ/νία πρόσληψης'], format='%d/%m/%Y', errors='coerce')
   
    if df['Ονομαστικός μισθός'].dtype == 'object':
        df['Ονομαστικός μισθός'] = pd.to_numeric(
            df['Ονομαστικός μισθός'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        )
    else:
        df['Ονομαστικός μισθός'] = pd.to_numeric(df['Ονομαστικός μισθός'], errors='coerce')


    # Add conditional logic for salary calculation based on "Περιγραφή Σύμβασης"
    df['Ονομαστικός μισθός'] = df.apply(
        lambda row: row['Ονομαστικός μισθός'] * 26 if row['Περιγραφή Σύμβασης'] == 'ΑΛΜ - ΗΜΕΡΟΜΙΣΘΙΟΙ' else row['Ονομαστικός μισθός'],
        axis=1
    )
   
    df['Hire Year'] = df['Ημ/νία πρόσληψης'].dt.year
    df['Departure Year'] = df['Ημ/νία αποχώρησης'].dt.year

    return df

# Page-specific logic
#st.markdown("### Compensation & Benefits")
# Custom HTML and CSS for the Comp & Ben header
header_html = """
<div style="background: linear-gradient(to right, #FFD700, #C0C0C0); padding: 20px; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
    <h1 style="color: white; text-align: center; font-family: 'Trebuchet MS', sans-serif; font-size: 36px;">
        💰 Compensation & Benefits 💼
    </h1>
    <p style="color: white; text-align: center; font-size: 20px; font-family: 'Trebuchet MS', sans-serif;">
        Rewarding Excellence, Securing the Future
    </p>
</div>
"""
# Display the header in the Streamlit app
st.markdown(header_html, unsafe_allow_html=True)

# Sidebar message with CSS for styling
st.sidebar.markdown(
    """
    <div style="
        background-color: #f4f4f4; 
        padding: 10px; 
        border-radius: 10px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    ">
        📌 **Select a Year** to dynamically calculate the Kpis.
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader('Choose a CSV file', type='csv', key=f'{COMP_PAGE_KEY}_file_uploader')

if uploaded_file:
    st.session_state[f'{COMP_PAGE_KEY}_uploaded_file'] = uploaded_file
    st.session_state[f'{COMP_PAGE_KEY}_df'] = load_and_preprocess_data(uploaded_file)

if f'{COMP_PAGE_KEY}_df' in st.session_state:
    df = st.session_state[f'{COMP_PAGE_KEY}_df']
    # Allow user to select start and end years for analysis
    start_year, end_year = st.sidebar.slider(
        "Select Year Range for Monthly Headcount Tab", min_value=2020, max_value=2030, value=(2024, 2025), key="year_range_slider"
    )

    year = st.sidebar.slider("Select Year for Salary & Turnover Analysis Tab", min_value=2020, max_value=2030, value=2024, key="year_slider")


    # 🔻 Dynamic exchange rate inputs (INSERT THIS HERE)
    companies_with_conversion = [
        'ALUMIL YU INDUSTRY SA',
        'ALUMIL ALBANIA Sh.P.K',
        'ALUMIL ROM INDUSTRY SA',
        'ALUMIL MISR FOR TRADING S.A.E.',
        'ALPRO VLASENICA A.D.',
        'ALUMIL MIDDLE EAST JLT'
    ]

    with st.sidebar.expander("💱 Set Exchange Rates"):
        exchange_rates = {}
        for company in companies_with_conversion:
            exchange_rates[company] = st.number_input(
                f"{company}", min_value=0.0, format="%.4f", step=0.0001,
                value={
                    'ALUMIL YU INDUSTRY SA': 0.008546,
                    'ALUMIL ALBANIA Sh.P.K': 0.01023,
                    'ALUMIL ROM INDUSTRY SA': 0.2010,
                    'ALUMIL MISR FOR TRADING S.A.E.': 0.019,
                    'ALPRO VLASENICA A.D.': 0.5142,
                    'ALUMIL MIDDLE EAST JLT': 0.25
                }.get(company, 1.0)
            )

    # 🔻 Use this exchange_rates dict in any function that requires currency conversion


    # Sidebar input for Exclusion - Active Employees
    exclude_input = st.sidebar.text_area("Exclude Active IDs (comma-separated)", 
        "1016492, 1017069, 1017070, 1100096, 1200014, 1200030, 1015535, 1015307, 1015791, 1015956")

    # Sidebar input for Exclusion - Departures
    exclude_departures_input = st.sidebar.text_area("Exclude Departures IDs (comma-separated)", 
        "1015768, 1015903, 1016610, 1017066, 1017182, "
        "1017247, 1017255, 1018277, 1011285, 1017525, "
        "1015710, 1017200, 1017346, 1017471, 1017475, "
        "1017476, 1017477, 1017478, 1017479, 1017480, 1017482, "
        "1017483, 1017484, 1017485, 1017512, 1017668, 1017622, 1017578")

    # Convert input into a set of IDs (strip spaces to avoid errors)
    exclude_ids = set(map(str.strip, exclude_input.split(',')))
    excluded_ids = set(map(str.strip, exclude_departures_input.split(',')))
    # Filter dataframe
    df = df[~df['Αριθμός μητρώου'].astype(str).isin(exclude_ids)]

    def calculate_overall_gender_pay_gap(df, year):
        df['Ονομαστικός μισθός'] = df['Ονομαστικός μισθός'].astype(float)
        df = df.dropna(subset=['Ονομαστικός μισθός'])  # Remove null salary values
        df = df[df['Ονομαστικός μισθός'] > 0]  # Exclude zero salaries

        start_of_year = pd.Timestamp(f"{year}-01-01")
        end_of_year = pd.Timestamp(f"{year}-12-31")

        df_filtered = df[
            (df['Ημ/νία πρόσληψης'] <= end_of_year) & 
            ((df['Ημ/νία αποχώρησης'].isna()) | (df['Ημ/νία αποχώρησης'] >= start_of_year))
        ]

        gender_salary = df_filtered.groupby('Όνομα Φύλου')['Ονομαστικός μισθός'].mean()

        if 'ΑΝΔΡΑΣ' in gender_salary and 'ΓΥΝΑΙΚΑ' in gender_salary:
            male_avg = gender_salary['ΑΝΔΡΑΣ']
            female_avg = gender_salary['ΓΥΝΑΙΚΑ']
            gender_pay_gap = ((male_avg - female_avg) / male_avg) * 100
        else:
            gender_pay_gap = None

        return gender_pay_gap


    # Function to calculate Gender Pay Gap per company
    def calculate_gender_pay_gap(df):
        df['Ονομαστικός μισθός'] = df['Ονομαστικός μισθός'].astype(float)
        df = df.dropna(subset=['Ονομαστικός μισθός'])  # Remove null salary values
        df = df[df['Ονομαστικός μισθός'] > 0]  # Exclude zero salaries
        start_of_2024 = pd.Timestamp(f"{year}-01-01")
        end_of_2024 = pd.Timestamp(f"{year}-12-31")
        df_2024 = df[
            (df['Ημ/νία πρόσληψης'] <= end_of_2024) & 
            ((df['Ημ/νία αποχώρησης'].isna()) | (df['Ημ/νία αποχώρησης'] >=  start_of_2024))
        ]
        
        results = []
        for company in df_2024['Περιγραφή εταιρίας'].unique():
            company_df = df_2024[df_2024['Περιγραφή εταιρίας'] == company]
            gender_salary = company_df.groupby('Όνομα Φύλου')['Ονομαστικός μισθός'].mean()
            
            if 'ΑΝΔΡΑΣ' in gender_salary and 'ΓΥΝΑΙΚΑ' in gender_salary:
                male_median = gender_salary['ΑΝΔΡΑΣ']
                female_median = gender_salary['ΓΥΝΑΙΚΑ']
                gender_pay_gap = ((male_median - female_median) / male_median) * 100
            else:
                gender_pay_gap = None
            
            results.append({'Περιγραφή εταιρίας': company, 'Gender Pay Gap (%)': gender_pay_gap})
        
        return pd.DataFrame(results)
    
    def calculate_overall_annual_remuneration_ratio(df, year, exchange_rates):
        # exchange_rates = {
        #     'ALUMIL YU INDUSTRY SA': 0.008546,
        #     'ALUMIL ALBANIA Sh.P.K': 0.01023,
        #     'ALUMIL ROM INDUSTRY SA': 0.2010,
        #     'ALUMIL MISR FOR TRADING S.A.E.': 0.019,
        #     'ALPRO VLASENICA A.D.': 0.5142,
        #     'ALUMIL MIDDLE EAST JLT': 0.25
        # }

        # Make a local copy to avoid modifying original df
        df_local = df.copy()

        # Safe conversion
        df_local['ΜΙΚΤΕΣ ΑΠΟΔ'] = pd.to_numeric(
            df_local['ΜΙΚΤΕΣ ΑΠΟΔ'].apply(lambda x: str(x).replace(',', '.')),
            errors='coerce'
        )

        # Convert to EUR
        df_local['Annual Salary EUR'] = df_local.apply(
            lambda row: row['ΜΙΚΤΕΣ ΑΠΟΔ'] * exchange_rates.get(row['Περιγραφή εταιρίας'], 1.0)
            if pd.notna(row['ΜΙΚΤΕΣ ΑΠΟΔ']) else None,
            axis=1
        )

        # Filter for active employees during the year
        start_of_year = pd.Timestamp(f"{year}-01-01")
        end_of_year = pd.Timestamp(f"{year}-12-31")

        df_filtered = df_local[
            (df_local['Ημ/νία πρόσληψης'] <= start_of_year) &
            ((df_local['Ημ/νία αποχώρησης'].isna()) | (df_local['Ημ/νία αποχώρησης'] > end_of_year))
        ]

        valid_salaries = df_filtered['Annual Salary EUR'].dropna()
        if len(valid_salaries) > 1:
            highest_salary = valid_salaries.max()
            median_salary = valid_salaries[valid_salaries != highest_salary].median()
            annual_rem_ratio = highest_salary / median_salary if median_salary > 0 else None
        else:
            annual_rem_ratio = None

        return annual_rem_ratio



    # Function to calculate Annual Remuneration Ratio per company
    def calculate_annual_remuneration_ratio(df, year=year):
    # Replace commas with dots and convert to numeric safely
        df['ΜΙΚΤΕΣ ΑΠΟΔ'] = pd.to_numeric(df['ΜΙΚΤΕΣ ΑΠΟΔ'].str.replace(',', '.', regex=False), errors='coerce')
        
        # Use 'ΜΙΚΤΕΣ ΑΠΟΔ' as annual salary
        df['Annual Salary'] = df['ΜΙΚΤΕΣ ΑΠΟΔ']

        # Define the end of 2024
        end_of_2024 = pd.Timestamp(f"{year}-12-31")
        start_of_2024 = pd.Timestamp(f"{year}-01-01")

        # Filter employees active in 2024
        df_2024 = df[
            (df['Ημ/νία πρόσληψης'] <= start_of_2024) & 
            ((df['Ημ/νία αποχώρησης'].isna()) | (df['Ημ/νία αποχώρησης'] > end_of_2024))
        ]

        results = []
        for company in df_2024['Περιγραφή εταιρίας'].unique():
            company_df = df_2024[df_2024['Περιγραφή εταιρίας'] == company]

            # Handle cases where there might be missing or non-numeric values
            valid_salaries = company_df['Annual Salary'].dropna()
            if len(valid_salaries) > 1:  
                highest_salary = valid_salaries.max()
                median_salary = valid_salaries[valid_salaries != highest_salary].median()

                annual_rem_ratio = highest_salary / median_salary if median_salary > 0 else None
            else:
                annual_rem_ratio = None  # Not enough valid data for calculation

            results.append({'Περιγραφή εταιρίας': company, 'Annual Remuneration Ratio': annual_rem_ratio})

        return pd.DataFrame(results)

    def calculate_monthly_headcount_year(df, start_year=2020, end_year=2030):
   

    # Generate all months from start_year to end_year
        months = pd.date_range(f'{start_year}-01-01', f'{end_year}-12-31', freq='MS')

        # Iterate through months and compute headcount dynamically
        for month in months:
            next_month = month + pd.offsets.MonthBegin(1)
            col_name = month.strftime("%Y-%m")  # e.g., "2024-01"
            
            df[col_name] = df.apply(
                lambda row: (row['Ημ/νία πρόσληψης'] < next_month) and 
                            (pd.isna(row['Ημ/νία αποχώρησης']) or row['Ημ/νία αποχώρησης'] >= next_month),
                axis=1
            )

        return df


    
    # Calculate Monthly Headcount
    def calculate_monthly_headcount(df, year = year):
        months = pd.date_range(f'{year}-01-01', f'{year}-12-31', freq='MS')
        for month in months:
            next_month = month + pd.offsets.MonthBegin(1)
            col_name = f'{month.strftime("%Y-%m")}'
            df[col_name] = df.apply(
                lambda row: (row['Ημ/νία πρόσληψης'] < next_month) and 
                            (pd.isna(row['Ημ/νία αποχώρησης']) or row['Ημ/νία αποχώρησης'] >= next_month),
                axis=1
            )
        return df
    

    df = calculate_monthly_headcount(df)


    def calculate_combined_metrics(df, year):
        start_of_period = pd.Timestamp(f"{year-1}-12-31")
        end_of_period = pd.Timestamp(f"{year}-12-31")

        # Apply filtering to exclude IDs dynamically
        df = df[~df['Αριθμός μητρώου'].astype(str).isin(exclude_ids)]

        results = []
        companies = df['Περιγραφή εταιρίας'].unique()

        for company in companies:
            company_df = df[df['Περιγραφή εταιρίας'] == company]

            # Headcount at the start of the period (end of previous year)
            start_headcount = company_df[
                (company_df['Ημ/νία πρόσληψης'] <= start_of_period) &
                ((company_df['Ημ/νία αποχώρησης'].isna()) | (company_df['Ημ/νία αποχώρησης'] > start_of_period))
            ].shape[0]

            # Headcount at the end of the period (end of current year)
            end_headcount = company_df[
                (company_df['Ημ/νία πρόσληψης'] <= end_of_period) &
                ((company_df['Ημ/νία αποχώρησης'].isna()) | (company_df['Ημ/νία αποχώρησης'] > end_of_period))
            ].shape[0]

            # Calculate average employees
            average_employees = (start_headcount + end_headcount) / 2

            # Filter departures to exclude specific IDs
            departures_df = company_df[~company_df['Αριθμός μητρώου'].astype(str).isin(excluded_ids)]

            # Voluntary and involuntary exits
            voluntary_exits = departures_df[
                (departures_df['Περιγραφή Αιτ. Αποχώρησης'] == "VOLUNTARY DEPARTURE") &
                (departures_df['Ημ/νία αποχώρησης'].dt.year == year)
            ].shape[0]

            involuntary_exits = departures_df[
                (departures_df['Περιγραφή Αιτ. Αποχώρησης'].str.contains('involuntary', case=False, na=False)) &
                (departures_df['Ημ/νία αποχώρησης'].dt.year == year)
            ].shape[0]

            retirements_exits = departures_df[
                (departures_df['Περιγραφή Αιτ. Αποχώρησης'].str.contains('retirement', case=False, na=False)) &
                (departures_df['Ημ/νία αποχώρησης'].dt.year == year)
            ].shape[0]

            # Turnover calculations
            voluntary_turnover = (voluntary_exits / average_employees * 100) if average_employees > 0 else 0
            involuntary_turnover = (involuntary_exits / average_employees * 100) if average_employees > 0 else 0
            retirement_turnover = (retirements_exits / average_employees * 100) if average_employees > 0 else 0
            total_turnover = voluntary_turnover + involuntary_turnover + retirement_turnover

            # Append results
            results.append({
                'Περιγραφή εταιρίας': company,
                'Start of Period Headcount': start_headcount,
                'End of Period Headcount': end_headcount,
                'Average Employees': round(average_employees, 2),
                'Voluntary Departures': voluntary_exits,
                'Involuntary Departures': involuntary_exits,
                'Retirement Departures': retirements_exits,
                'Voluntary Turnover (%)': round(voluntary_turnover, 2),
                'Involuntary Turnover (%)': round(involuntary_turnover, 2),
                'Retirement Turnover (%)': round(retirement_turnover, 2),
                'Total Turnover (%)': round(total_turnover, 2)
            })

        #return pd.DataFrame(results)
        results_df = pd.DataFrame(results)
        # Calculate totals
        totals = pd.DataFrame([{
        'Περιγραφή εταιρίας': 'TOTAL',
        'Start of Period Headcount': results_df['Start of Period Headcount'].sum(),
        'End of Period Headcount': results_df['End of Period Headcount'].sum(),
        'Average Employees': round(results_df['Average Employees'].sum(), 2),
        'Voluntary Departures': results_df['Voluntary Departures'].sum(),
        'Involuntary Departures': results_df['Involuntary Departures'].sum(),
        'Retirement Departures': results_df['Retirement Departures'].sum(),
        'Voluntary Turnover (%)': round((results_df['Voluntary Departures'].sum() / results_df['Average Employees'].sum()) * 100, 2),
        'Involuntary Turnover (%)': round((results_df['Involuntary Departures'].sum() / results_df['Average Employees'].sum()) * 100, 2),
        'Retirement Turnover (%)': round((results_df['Retirement Departures'].sum() / results_df['Average Employees'].sum()) * 100, 2),
        'Total Turnover (%)': round((
            (results_df['Voluntary Departures'].sum() +
            results_df['Involuntary Departures'].sum() +
            results_df['Retirement Departures'].sum()) / results_df['Average Employees'].sum()) * 100, 2)

    }])
        # Append totals row
        results_df = pd.concat([results_df, totals], ignore_index=True)

        return results_df

    # Calculate start and end of period headcount for each company
    def calculate_headcount(df, year=year):
        start_of_period = pd.Timestamp(f"{year-1}-12-31")
        end_of_period = pd.Timestamp(f"{year}-12-31")

        results = []
        companies = df['Περιγραφή εταιρίας'].unique()

        for company in companies:
            company_df = df[df['Περιγραφή εταιρίας'] == company]

            # Headcount at the start of the period (end of 2023)
            start_headcount = company_df[
                (company_df['Ημ/νία πρόσληψης'] <= start_of_period) &
                ((company_df['Ημ/νία αποχώρησης'].isna()) | (company_df['Ημ/νία αποχώρησης'] > start_of_period))
            ].shape[0]

            # Headcount at the end of the period (end of 2024)
            end_headcount = company_df[
                (company_df['Ημ/νία πρόσληψης'] <= end_of_period) &
                ((company_df['Ημ/νία αποχώρησης'].isna()) | (company_df['Ημ/νία αποχώρησης'] > end_of_period))
            ].shape[0]

            results.append({
                'Περιγραφή εταιρίας': company,
                'Start of Period Headcount': start_headcount,
                'End of Period Headcount': end_headcount
            })

        return pd.DataFrame(results)


    # Aggregate headcount by company
    def aggregate_headcount_by_month(df):
        months = [col for col in df.columns if col.startswith(str(year))]
        grouped = df.groupby('Περιγραφή εταιρίας')[months].sum().reset_index()
        return grouped

    headcount_table = aggregate_headcount_by_month(df)

    def aggregate_headcount_by_group(df, year=year):
        # Identify the columns for the specified year
        months = [col for col in df.columns if col.startswith(str(year))]
        
        # Fill missing values in 'Div' and 'Τμήμα' with a placeholder (optional: keep as NaN for blanks)
        df['Division'] = df['Division'].fillna('Blank')
        df['Department'] = df['Department'].fillna('Blank')
        
        # Group by the specified columns and sum the selected columns
        grouped = df.groupby(['Περιγραφή εταιρίας', 'Division', 'Department'])[months].sum().reset_index()
        
        return grouped

    # Usage
    headcount_Grouped_table = aggregate_headcount_by_group(df, year=year)





    def get_top_10_percent_employees(df):
        results = []
        companies = df['Περιγραφή εταιρίας'].unique()

        for company in companies:
            company_df = df[df['Περιγραφή εταιρίας'] == company]

            # Sort by total compensation
            sorted_df = company_df.sort_values(by='Ονομαστικός μισθός', ascending=False)

            # Calculate the number of employees in the top 10%
            top_10_percent_count = max(1, int(len(sorted_df) * 0.1))

            # Get the top 10% employees
            top_10_percent_df = sorted_df.head(top_10_percent_count)

            # Add to results
            for _, row in top_10_percent_df.iterrows():
                results.append({
                    'Περιγραφή εταιρίας': company,
                    'Αριθμός μητρώου': row['Αριθμός μητρώου'],
                    'Επώνυμο': row['Επώνυμο'],
                    'Ονομα': row['Ονομα'],
                    'Ονομαστικός μισθός': row['Ονομαστικός μισθός']
                })

        return pd.DataFrame(results)


    def get_top_10_percent_employees_2024(df):
        results = []
        companies = df['Περιγραφή εταιρίας'].unique()

        # Filter employees active during 2024
        start_of_2024 = pd.Timestamp("2024-01-01")
        end_of_2024 = pd.Timestamp(f"{year}-12-31")
        df_2024 = df[
            (df['Ημ/νία πρόσληψης'] <= end_of_2024) & 
            ((df['Ημ/νία αποχώρησης'].isna()) | (df['Ημ/νία αποχώρησης'] > end_of_2024))
        ]


        for company in companies:
            company_df = df_2024[df_2024['Περιγραφή εταιρίας'] == company]

            # Sort by total compensation
            sorted_df = company_df.sort_values(by='ΜΙΚΤΕΣ ΑΠΟΔ', ascending=False)

            # Calculate the number of employees in the top 10%
            top_10_percent_count = math.ceil(len(sorted_df) * 0.1)

            # Get the top 10% employees
            top_10_percent_df = sorted_df.head(top_10_percent_count)

            # Add to results
            for _, row in top_10_percent_df.iterrows():
                results.append({
                    'Περιγραφή εταιρίας': company,
                    'Αριθμός μητρώου': row['Αριθμός μητρώου'],
                    'Επώνυμο': row['Επώνυμο'],
                    'Ονομα': row['Ονομα'],
                    'Συνολικές Αποδοχές': row['ΜΙΚΤΕΣ ΑΠΟΔ']
                })

        return pd.DataFrame(results)



    # Display results in tabs
    tab1, tab2 = st.tabs(["👉 Monthly Headcount", "Salary & Turnover Analysis"])

    with tab1:
        #st.write("Column Names:", df.columns)
        # Grouping options for the user
        groupby_options = ['Περιγραφή εταιρίας', 'Division', 'Department']
        selected_groupby = st.multiselect("🔀 Group by:", groupby_options, default=['Περιγραφή εταιρίας'])     

        # Compute monthly headcount for multiple years
        df = calculate_monthly_headcount_year(df, start_year, end_year)
        
        if not selected_groupby:
            st.warning("⚠️ Please select at least one grouping field to display the headcount table.")
        else:

        # Aggregate the headcount by company for all selected years
            def aggregate_headcount_by_month(df, groupby_fields, start_year, end_year):
                months = [col for col in df.columns if any(str(y) in col for y in range(start_year, end_year + 1))]
                grouped = df.groupby(groupby_fields)[months].sum().reset_index()
                return grouped


            headcount_table = aggregate_headcount_by_month(df, selected_groupby, start_year, end_year)


            # Define mapping only for display titles
            display_name_map = {
                'Περιγραφή εταιρίας': 'Company',
                'Division': 'Division',
                'Department': 'Department'
            }

            # Build dynamic title string
            grouping_description = ", ".join([display_name_map.get(col, col) for col in selected_groupby])

            # Dynamic title with CSS styling
            st.markdown(
                f"""
                <div style='
                    text-align: center; 
                    font-family: "Arial", sans-serif; 
                    font-size: 20px; 
                    font-weight: bold; 
                    color: #333; 
                    margin-bottom: 10px;
                '>
                    📊 Monthly Headcount by {grouping_description} ({start_year} - {end_year})
                </div>
                """,
                unsafe_allow_html=True
            )



            with st.expander(f'📋 View Monthly Headcount Table ({start_year} - {end_year}):'):
                # Convert only numeric columns to a proper numeric format
                numeric_cols = headcount_table.select_dtypes(include=['number']).columns
                st.dataframe(headcount_table.style.format({col: "{:,.0f}" for col in numeric_cols}))

        import io
        import pandas as pd
        import streamlit as st

        def export_and_display_unpivoted_headcount(df, start_year, end_year):
            # 1. Detect month columns
            month_cols = [col for col in df.columns if any(str(y) in col for y in range(start_year, end_year + 1))]

            # 2. Melt/unpivot to long format
            unpivoted_df = df.melt(
                id_vars=[col for col in df.columns if col not in month_cols],
                value_vars=month_cols,
                var_name='Month',
                value_name='Headcount'
            )

            # 3. Show in Streamlit table
            st.markdown(
                "<h4 style='color:#333;'>📄 Unpivoted Monthly Headcount Table (Long Format)</h4>",
                unsafe_allow_html=True
            )
            with st.expander(f'📋 View Monthly Headcount Table Unpivoted ({start_year} - {end_year}):'):
                st.dataframe(unpivoted_df.style.format({'Headcount': '{:,.0f}'}))

            # 4. Export to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                unpivoted_df.to_excel(writer, index=False, sheet_name='Unpivoted Headcount')

            # 5. Download button
            st.download_button(
                label="📥 Download as Excel",
                data=output.getvalue(),
                file_name="Unpivoted_Headcount.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        export_and_display_unpivoted_headcount(headcount_table, start_year, end_year)

        # Row space before the table
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        # Minimalist header for monthly headcount
#         st.markdown(
#                 f"""
#                 <div style='
#                     text-align: center; 
#                     font-family: "Arial", sans-serif; 
#                     font-size: 20px; 
#                     font-weight: bold; 
#                     color: #333; 
#                     margin-bottom: 10px;
#                 '>
#                     📊 Monthly Headcount by Company ({year})
#                 </div>
#                 """,
#                 unsafe_allow_html=True
# )
#         # Expander for the headcount table
#         with st.expander('📋 View Headcount Table:'):
#             st.write(headcount_table)

#         # Minimalist header for division/department-level headcount
#         st.markdown(
#             f"""
#             <div style='
#                 text-align: center; 
#                 font-family: "Arial", sans-serif; 
#                 font-size: 20px; 
#                 font-weight: bold; 
#                 color: #333; 
#                 margin-top: 20px; 
#                 margin-bottom: 10px;
#             '>
#                 🏢 Monthly Headcount by Company, Division, and Department ({year})
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         # Row space before the table
#         st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

#         # Expander for the grouped headcount table
#         with st.expander('📋 View Detailed Headcount Table:'):
#             st.write(headcount_Grouped_table)


        # Force aggregation only by company name
        headcount_company_table = df.groupby('Περιγραφή εταιρίας')[
            [col for col in df.columns if col.startswith(str(year))]
        ].sum().reset_index()
        
        # Create the heatmap
        fig = px.imshow(
            headcount_company_table.set_index('Περιγραφή εταιρίας').T,
            labels={'x': 'Company', 'y': 'Month', 'color': 'Headcount'},
            title=f'Monthly Headcount by Company ({year})',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig)


    with tab2:
        #st.header("Salary & Turnover Analysis")
        # Minimalist header for Salary & Turnover Analysis
        st.markdown(
            f"""
            <div style='
                text-align: center; 
                font-family: "Arial", sans-serif; 
                font-size: 36px; 
                font-weight: bold; 
                color: #333; 
                margin-bottom: 10px;
            '>
                💰📉 Salary & Turnover Analysis ({year})
            </div>
            """,
            unsafe_allow_html=True
        )

        # Row space before the table
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        

        # Ensure the required columns exist
        if 'Ονομαστικός μισθός' in df.columns and 'Περιγραφή εταιρίας' in df.columns and 'Ημ/νία αποχώρησης' in df.columns:
            try:
                # Convert columns to appropriate data types
                # Replace commas with dots in the 'Ονομαστικός μισθός' column
                # Only replace commas if column is not numeric
                if df['Ονομαστικός μισθός'].dtype == 'object':
                    df['Ονομαστικός μισθός'] = pd.to_numeric(
                        df['Ονομαστικός μισθός'].astype(str).str.replace(',', '.', regex=False),
                        errors='coerce'
                    )
                else:
                    df['Ονομαστικός μισθός'] = pd.to_numeric(df['Ονομαστικός μισθός'], errors='coerce')

                df['Ημ/νία αποχώρησης'] = pd.to_datetime(df['Ημ/νία αποχώρησης'], errors='coerce')
                # Calculate KPIs per company
                st.subheader(f"🎯 Overall Gender Pay Gap & Remuneration Ratio for {year}")
                ratio = calculate_overall_annual_remuneration_ratio(df, year, exchange_rates)
                gender_pay_gap = calculate_overall_gender_pay_gap(df, year)

                col1, col2 = st.columns(2)

                with col1:
                    if gender_pay_gap is not None:
                        st.metric(label="👩‍💼👨‍💼 Gender Pay Gap", value=f"{gender_pay_gap:.2f}%")
                    else:
                        st.warning("⚠️ Not enough data for Gender Pay Gap.")

                with col2:
                    if ratio is not None:
                        st.metric(label="💸 Annual Remuneration Ratio", value=f"{ratio:.2f}x")
                    else:
                        st.warning("⚠️ Not enough data for Annual Remuneration Ratio.")

                gender_pay_gap_df = calculate_gender_pay_gap(df)
                annual_rem_ratio_df = calculate_annual_remuneration_ratio(df)
                
                # Merge the two dataframes for better visualization
                kpi_df = gender_pay_gap_df.merge(annual_rem_ratio_df, on='Περιγραφή εταιρίας')
                
                # Display results
                st.subheader("📊 Gender Pay Gap & Annual Remuneration Ratio per Company")
                with st.expander("📊 Gender Pay Gap & Annual Remuneration Ratio per Company"):
                    st.dataframe(kpi_df.style.format({'Gender Pay Gap (%)': '{:.2f}%', 'Annual Remuneration Ratio': '{:.2f}'}))
                # Filter rows where 'Ημ/νία αποχώρησης' is blank or in the year 2024
                filtered_df = df[(df['Ημ/νία αποχώρησης'].isna()) | (df['Ημ/νία αποχώρησης'].dt.year > year)]

                # exchange_rates = {
                #             'ALUMIL YU INDUSTRY SA': 0.008546,
                #             'ALUMIL ALBANIA Sh.P.K': 0.01023,
                #             'ALUMIL ROM INDUSTRY SA': 0.2010,
                #             'ALUMIL MISR FOR TRADING S.A.E.': 0.019,
                #             'ALPRO VLASENICA A.D.': 0.5142,
                #             'ALUMIL MIDDLE EAST JLT': 0.25
                #         }

                # Exclude the max 'Ονομαστικός μισθός' for each company and calculate the median
                filtered_df = filtered_df.loc[~filtered_df.index.isin(
                    filtered_df.groupby('Περιγραφή εταιρίας')['ΜΙΚΤΕΣ ΑΠΟΔ'].idxmax()
                )]
                analysis_df = filtered_df.groupby('Περιγραφή εταιρίας')['ΜΙΚΤΕΣ ΑΠΟΔ'].median().reset_index()

                # Rename columns for better readability
                analysis_df.rename(columns={
                    'ΜΙΚΤΕΣ ΑΠΟΔ': 'Median Salary (Excluding Max)'
                }, inplace=True)
                
                # Calculate median in EUR
                analysis_df['Median Salary (Excluding Max) in EUR'] = analysis_df.apply(
                    lambda row: row['Median Salary (Excluding Max)'] * exchange_rates.get(row['Περιγραφή εταιρίας'], 1), axis=1
                )
                
                # ✅ Sort by descending EUR value
                analysis_df = analysis_df.sort_values(by='Median Salary (Excluding Max) in EUR', ascending=False).reset_index(drop=True)


                # Calculate the top 10% employees for 2024
                top_10_percent_df_2024 = get_top_10_percent_employees_2024(df)
                with st.expander(f"Table: Top 10% Employees by Total Compensation for {year}:"):
                    st.write(top_10_percent_df_2024)
                # Display the results as a table
                # Subheader for Median Salary Table
                st.markdown(
                    """
                    <div style='
                        text-align: left; 
                        font-family: "Arial", sans-serif; 
                        font-size: 18px; 
                        font-weight: 600; 
                        color: #444; 
                        margin-top: 15px; 
                        margin-bottom: 10px;
                    '>
                        📋 Table: Median Salary by Company (Excluding Max Salary)
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander(f'Median Salary by Company for ({year})'):
                    st.write(analysis_df)

                # Plotly bar chart visualization
                fig = px.bar(
                    analysis_df,
                    x='Περιγραφή εταιρίας',
                    y='Median Salary (Excluding Max) in EUR',
                    title="Median Salary by Company (Excluding Max Salary)",
                    labels={
                        'Περιγραφή εταιρίας': 'Company',
                        'Median Salary (Excluding Max) in EUR': 'Median Salary'
                    },
                    text='Median Salary (Excluding Max) in EUR'
                )
                # Reorder the categories based on descending order
                fig.update_layout(
                    xaxis={'categoryorder': 'total descending'}
                )
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

                # Display the plot
                st.markdown(
                    """
                    <div style='
                        text-align: left; 
                        font-family: "Arial", sans-serif; 
                        font-size: 18px; 
                        font-weight: 600; 
                        color: #444; 
                        margin-top: 15px; 
                        margin-bottom: 10px;
                    '>
                        📊 Visualization: Median Salary by Company (Excluding Max Salary)
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.plotly_chart(fig)

                

                # Call the function and display the results
                headcount_df = calculate_headcount(df)
                #st.subheader("Table: Start and End of Period Headcount by Company")
                #st.write(headcount_df)
                
                st.markdown(
                    f"""
                    <div style='
                        text-align: left; 
                        font-family: "Arial", sans-serif; 
                        font-size: 22px; 
                        font-weight: 600; 
                        color: #333; 
                        padding: 10px 0;
                        border-bottom: 2px solid #D6D6D6;
                        margin-bottom: 15px;
                    '>
                        💼 Turnover Metrics ({year})
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                # Calculate combined metrics
                combined_metrics_df = calculate_combined_metrics(df, year=year)

                # Exclude TOTAL row from the heatmap
                combined_metrics_df_no_total = combined_metrics_df[combined_metrics_df['Περιγραφή εταιρίας'] != 'TOTAL']

                # Apply styling with background gradient and format numeric columns to 1 decimal place
                styled_df = (
                    combined_metrics_df_no_total
                    .style.background_gradient(cmap='Blues')
                    .format({col: "{:.1f}" for col in combined_metrics_df_no_total.select_dtypes(include='number').columns})
                )

                # Display the styled DataFrame as HTML in Streamlit
                st.dataframe(styled_df)

                st.subheader("Summary (TOTAL)")
                st.dataframe(combined_metrics_df[combined_metrics_df['Περιγραφή εταιρίας'] == 'TOTAL'])

                #st.write(combined_metrics_df)


                # Calculate combined metrics
                combined_metrics_df = calculate_combined_metrics(df, year=year)

                # Display the table as a heatmap
                #st.subheader("Heatmap: Combined Metrics by Company")

                # Convert DataFrame to numeric values where applicable
                heatmap_data = combined_metrics_df.set_index('Περιγραφή εταιρίας')
                numeric_columns = ['Start of Period Headcount', 'End of Period Headcount',
                                'Average Employees', 'Voluntary Departures', 
                                'Involuntary Departures', 'Voluntary Turnover (%)', 
                                'Involuntary Turnover (%)', 'Total Turnover (%)']
                heatmap_data = heatmap_data[numeric_columns]
                
                # Plot heatmap without normalization
                fig = px.imshow(
                    heatmap_data,
                    labels=dict(x="Metrics", y="Company", color="Value"),
                    title="Heatmap of Combined Metrics by Company",
                    text_auto=True,
                    color_continuous_scale="Blues"
                )

                # Adjust figure size
                fig.update_layout(
                    width=1200,  # Set the width of the heatmap
                    height=800,  # Set the height of the heatmap
                    xaxis_title="Metrics",
                    yaxis_title="Company"
                )


                # Plot voluntary and involuntary turnover
                fig = px.bar(
                    combined_metrics_df.melt(
                        id_vars='Περιγραφή εταιρίας', 
                        value_vars=['Voluntary Turnover (%)', 'Involuntary Turnover (%)'], 
                        var_name='Turnover Type', 
                        value_name='Percentage'
                    ),
                    x='Περιγραφή εταιρίας',
                    y='Percentage',
                    color='Turnover Type',
                    title=f"Voluntary and Involuntary Turnover by Company ({year})",
                    labels={'Περιγραφή εταιρίας': 'Company', 'Percentage': 'Turnover (%)'},
                    text='Percentage'  # Add this to include data labels
                )

                # Format the data labels
                fig.update_traces(
                    texttemplate='%{text:.2f}%',  # Format the labels as percentages with 2 decimal places
                    textposition='outside'       # Position the labels outside the bars
                )

                # Adjust layout for better readability
                fig.update_layout(
                    xaxis_title="Company",
                    yaxis_title="Turnover (%)",
                    width=1200,
                    height=800
                )

                # Display the plot
                # Subheader for Turnover Visualization
                st.markdown(
                    """
                    <div style='
                        text-align: left; 
                        font-family: "Arial", sans-serif; 
                        font-size: 18px; 
                        font-weight: 600; 
                        color: #444; 
                        margin-top: 15px; 
                        margin-bottom: 10px;
                    '>
                        📊 Visualization: Voluntary and Involuntary Turnover by Company
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.plotly_chart(fig)

               

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.write("The required columns ('Ονομαστικός μισθός', 'Περιγραφή εταιρίας', 'Ημ/νία αποχώρησης') are missing from the dataset.")




else:
    st.write('Please upload a CSV file to proceed.')

