import streamlit as st
import pandas as pd

# Function to load and preprocess data
@st.cache_data
def load_and_preprocess_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        required_columns = [
            'Country', 'Company', 'Year', 'Division', 'Department',
            'Job Property', 'Status', 'Duration in Hours', 'Cost (€)', 'Trainee ID', 'Completion Date' # Added Completion Date
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
            return None

        # Convert Completion Date to datetime and drop rows where conversion fails
        df['Completion Date'] = pd.to_datetime(df['Completion Date'], errors='coerce')
        df.dropna(subset=['Completion Date'], inplace=True)
        
        # Ensure 'Year' is treated as a string for consistent filtering if needed
        if 'Year' in df.columns:
            df['Year'] = df['Year'].astype(str)
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Function to apply filters and collect group by columns
def apply_filters(df):
    filtered_df = df.copy()
    group_by_columns = []
    selected_filters = {}

    st.sidebar.header('Filter Options')
    st.sidebar.write("Leave a filter unselected to include all options.")

    # --- NEW DATE FILTER ---
    st.sidebar.subheader("Date Range Filter")

    if not filtered_df.empty and 'Completion Date' in filtered_df.columns:
        # Determine min/max dates for the selector
        min_date = filtered_df['Completion Date'].min().date()
        max_date = filtered_df['Completion Date'].max().date()
        
        # Date input for the cutoff date
        selected_date = st.sidebar.date_input(
            "Select Cutoff Date (Data BEFORE this date)",
            value=max_date, # Default to the latest date available
            min_value=min_date,
            max_value=max_date,
            help="Only data with a 'Completion Date' *before* the selected date will be included."
        )

        # Apply the date filter
        if selected_date:
            cutoff_datetime = pd.to_datetime(selected_date)
            
            # Filter for dates strictly less than the selected cutoff date
            mask = filtered_df['Completion Date'] < cutoff_datetime
            
            # Store the date filter info for the dynamic title
            selected_filters['Completion Date (Before)'] = [str(selected_date)]
            
            filtered_df = filtered_df[mask]
    else:
        st.sidebar.warning("Completion Date column missing or data is empty. Skipping date filter.")


    # --- EXISTING CATEGORICAL FILTERS ---
    st.sidebar.subheader("Categorical Filters")
    
    # If you really have a column named 'Job Property2', keep it. Otherwise use 'Job Property'.
    # Assuming 'Job Property' is the correct column name based on the required_columns list.
    filters = {
        'Country': 'Country',
        'Company': 'Company',
        'Year': 'Year',
        'Division': 'Division',
        'Department': 'Department',
        'Job Property': 'Job Property2',
        'Status': 'Status',
        'Gender': 'Gender2'
    }

    for filter_label, column_name in filters.items():
        # Skip gracefully if column is missing
        if column_name not in filtered_df.columns:
            st.sidebar.warning(f"Column '{column_name}' not found; skipping filter '{filter_label}'.")
            continue

        # Build choices as strings to avoid int<->str sort/compare errors
        raw_vals = filtered_df[column_name].dropna().unique()
        choices = sorted((str(v) for v in raw_vals), key=str.casefold)

        selected = st.sidebar.multiselect(
            f"Select {filter_label}",
            options=choices,
            default=[],
            help=f"Leave empty to include all {filter_label.lower()}s."
        )

        if selected:
            # Compare as strings to match the UI choices; keep original dtypes in the df
            mask = filtered_df[column_name].astype(str).isin(set(selected))
            filtered_df = filtered_df[mask]
            group_by_columns.append(column_name)
            selected_filters[filter_label] = selected

    return filtered_df, group_by_columns, selected_filters


# Function to create a professional dynamic title with italic categories and bold values
def create_dynamic_title(selected_filters):
    title_parts = []
    for filter_label, values in selected_filters.items():
        # Convert all values to strings to avoid TypeError
        string_values = [str(value) for value in values]
        if string_values:
            # Italic for category and bold for values
            title_parts.append(f"<i>{filter_label}:</i> <b>{', '.join(string_values)}</b>")
    
    if title_parts:
        title = "Filtered by: " + " | ".join(title_parts)
    else:
        title = "All Data"
    # Custom HTML and CSS for professional styling
    styled_title = f"""
    <div style="background-color:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #e0e0e0; margin-top:20px;">
        <h2 style="color:#333333; font-family:'Helvetica Neue', sans-serif; font-size:24px; font-weight:500;">
            {title}
        </h2>
    </div>
    """
    
    return styled_title

# Function to calculate KPIs
def calculate_kpis(grouped_df):
    total_duration = grouped_df['duration_in_hours_sum'].sum()
    total_cost = grouped_df['cost_sum'].sum()
    total_unique_trainees = grouped_df['unique_trainee_id_count'].sum()
    cost_per_unique_trainee = total_cost / total_unique_trainees if total_unique_trainees else 0
    duration_per_unique_trainee = total_duration / total_unique_trainees if total_unique_trainees else 0
    
    totals = {
        'total_duration_formatted': f"{total_duration:,.2f}",
        'total_cost_formatted': f"{total_cost:,.2f}",
        'total_unique_trainees_formatted': f"{total_unique_trainees:,}",
        'cost_per_unique_trainee_formatted': f"{cost_per_unique_trainee:,.2f}",
        'duration_per_unique_trainee_formatted': f"{duration_per_unique_trainee:,.2f}",
    }
    return totals

# Function to display KPIs in custom-styled cards
def display_kpis(totals):
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; justify-content: space-around; margin-bottom: 20px; gap: 10px;">
        <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; min-width: 250px; flex-grow: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #4CAF50; margin-top: 0;">Total Duration (Hours)</h3>
            <p style="font-size: 24px; font-weight: bold;">{}</p>
            <div style="height: 5px; background-color: #4CAF50; border-radius: 2px;"></div>
        </div>
        <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; min-width: 250px; flex-grow: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #FF5722; margin-top: 0;">Total Cost (€)</h3>
            <p style="font-size: 24px; font-weight: bold;">{}</p>
            <div style="height: 5px; background-color: #FF5722; border-radius: 2px;"></div>
        </div>
        <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; min-width: 250px; flex-grow: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #3F51B5; margin-top: 0;">Total Unique Trainees</h3>
            <p style="font-size: 24px; font-weight: bold;">{}</p>
            <div style="height: 5px; background-color: #3F51B5; border-radius: 2px;"></div>
        </div>
    </div>
    <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 10px;">
        <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; min-width: 250px; flex-grow: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #009688; margin-top: 0;">Cost per Unique Trainee (€)</h3>
            <p style="font-size: 24px; font-weight: bold;">{}</p>
            <div style="height: 5px; background-color: #009688; border-radius: 2px;"></div>
        </div>
        <div style="background-color: #f0f4f7; padding: 20px; border-radius: 10px; min-width: 250px; flex-grow: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #9C27B0; margin-top: 0;">Duration per Unique Trainee (Hours)</h3>
            <p style="font-size: 24px; font-weight: bold;">{}</p>
            <div style="height: 5px; background-color: #9C27B0; border-radius: 2px;"></div>
        </div>
    </div>
    """.format(totals['total_duration_formatted'], 
               totals['total_cost_formatted'], 
               totals['total_unique_trainees_formatted'], 
               totals['cost_per_unique_trainee_formatted'], 
               totals['duration_per_unique_trainee_formatted']),
               unsafe_allow_html=True)
    # Add a divider between the KPI section and the grouped table
    st.markdown("<hr style='border-top: 3px solid #bbb;'>", unsafe_allow_html=True)
    
# Main app code
def main():
    # Custom HTML and CSS for the header
    header_html = """
    <div style="background-color:#4CAF50; padding:20px; border-radius:10px; margin-bottom:20px; box-shadow: 0 6px 10px rgba(0,0,0,0.2);">
        <h1 style="color:white; text-align:center; font-family:Arial, sans-serif;">
            📚 L&D Training Plans 📊
        </h1>
        <p style="color:white; text-align:center; font-size:18px; font-family:Arial, sans-serif;">
            Empowering Employees through Skill Building and Continuous Learning
        </p>
    </div>
    """

    # Display the header in the Streamlit app
    st.markdown(header_html, unsafe_allow_html=True)

    # Unique key for this page
    PAGE_KEY = 'ld_training_data'

    # File uploader
    uploaded_file = st.file_uploader('Choose an Excel file', type='xlsx')

    if uploaded_file is not None:
        # Load and store data in session state
        st.session_state[f'{PAGE_KEY}_uploaded_file'] = uploaded_file
        st.session_state[f'{PAGE_KEY}_df'] = load_and_preprocess_data(uploaded_file)

    # Check if data is available in session state
    if f'{PAGE_KEY}_df' in st.session_state and st.session_state[f'{PAGE_KEY}_df'] is not None:
        df = st.session_state[f'{PAGE_KEY}_df']

        # Apply filters and get group by columns
        filtered_df, group_by_columns, selected_filters = apply_filters(df)
        dynamic_title = create_dynamic_title(selected_filters)
        
        # Display dynamic title
        st.markdown(dynamic_title, unsafe_allow_html=True)
        st.markdown("<hr style='border-top: 3px solid #bbb;'>", unsafe_allow_html=True)
        
        # Display the filtered data
        with st.expander('View Filtered Raw Data'):
            st.write(filtered_df)

        # Check if filtered data is not empty
        if not filtered_df.empty:
            if group_by_columns:
                # Group by the selected columns
                grouped_df = filtered_df.groupby(group_by_columns).agg(
                    duration_in_hours_sum=('Duration in Hours', 'sum'),
                    cost_sum=('Cost (€)', 'sum'),
                    # Calculate unique trainees within each group
                    unique_trainee_id_count=('Trainee ID', pd.Series.nunique) 
                ).reset_index()
                
                # Calculate metrics after grouping
                grouped_df['cost_per_unique_trainee'] = grouped_df['cost_sum'] / grouped_df['unique_trainee_id_count']
                grouped_df['duration_per_unique_trainee'] = grouped_df['duration_in_hours_sum'] / grouped_df['unique_trainee_id_count']
            
            else:
                # Aggregate over the entire filtered dataset without grouping
                total_unique = filtered_df['Trainee ID'].nunique()
                total_cost_sum = filtered_df['Cost (€)'].sum()
                total_duration_sum = filtered_df['Duration in Hours'].sum()
                
                cost_per = total_cost_sum / total_unique if total_unique else 0
                duration_per = total_duration_sum / total_unique if total_unique else 0
                
                grouped_df = pd.DataFrame({
                    'duration_in_hours_sum': [total_duration_sum],
                    'cost_sum': [total_cost_sum],
                    'unique_trainee_id_count': [total_unique],
                    'cost_per_unique_trainee': [cost_per],
                    'duration_per_unique_trainee': [duration_per]
                })

            # Calculate KPIs from the (potentially single-row) grouped_df
            totals = calculate_kpis(grouped_df)

            # Display KPIs
            st.subheader("Key Performance Indicators (KPIs)")
            display_kpis(totals)

            # Display the grouped and aggregated data
            if group_by_columns:
                st.subheader(f"Grouped Data by: {', '.join(group_by_columns)}")
                with st.expander('View Detailed Aggregation Table'):
                    st.dataframe(grouped_df.style.format({
                        'duration_in_hours_sum': "{:,.2f}",
                        'cost_sum': "€{:,.2f}",
                        'unique_trainee_id_count': "{:,}",
                        'cost_per_unique_trainee': "€{:,.2f}",
                        'duration_per_unique_trainee': "{:,.2f}"
                    }), use_container_width=True)
            elif not group_by_columns and len(grouped_df) == 1:
                 st.info("Aggregation performed across the entire filtered dataset (no grouping columns selected).")
                 
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.warning('Please upload an Excel file to proceed.')

# Call the main function directly
main()
