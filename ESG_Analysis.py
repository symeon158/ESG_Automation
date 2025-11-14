import streamlit as st

st.set_page_config(layout="wide")

# --- PAGE SETUP ---
about_page = st.Page(
    "views/about ESG.py",
    title="About ESG",
    icon=":material/account_circle:",
    default=True,
)

project_1_page = st.Page(
    "views/HR Data Analyst.py",
    title="HR Data Analyst",
    icon=":material/bar_chart:",
)

project_2_page = st.Page(
    "views/Comp&Ben.py",
    title="Comp&Ben",
    icon="💵",
)

project_5_page = st.Page(
    "views/OD.py",
    title="OD",
    icon="🏋️",
)

project_7_page = st.Page(
    "views/Manpower.py",
    title="Manpower",
    icon="🧍",
)

# --- NEW PAGE: Manpower Budget Info ---
manpower_info_page = st.Page(
    "views/Manpower Budget Info.py",     # create this file in /views/
    title="Manpower Budget Info",
    icon="🧍💼",
)

# --- NAVIGATION SETUP ---
pg = st.navigation(
    {
        "Info": [about_page],
        "Manpower Budget Info": [manpower_info_page],  # 👈 New top-level
        "ESG": [project_1_page, project_2_page, project_5_page],
        "Manpower Budget": [project_7_page],
    }
)


# --- SHARED ON ALL PAGES ---
st.sidebar.markdown(
    "Created with ❤️ by [Symeon Papadopoulos](https://www.linkedin.com/in/symeon-papadopoulos-b242b1166/)"
)

# --- RUN NAVIGATION ---
pg.run()



