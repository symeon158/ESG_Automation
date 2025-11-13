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

project_7_page = st.Page(
    "views/Manpower.py",
    title="Manpower",
    icon="🧍",
)

project_5_page = st.Page(
    "views/OD.py",
    title="OD",
    icon="🏋️",
)



# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Info": [about_page],
        "ESG": [project_1_page, project_2_page, project_5_page],
        "Manpower Budget": [project_7_page],
    }
)


# --- SHARED ON ALL PAGES ---
#st.logo("assets/codingisfun_logo.png")
st.sidebar.markdown("Created with ❤️ by [Symeon Papadopoulos](https://www.linkedin.com/in/symeon-papadopoulos-b242b1166/)")


# --- RUN NAVIGATION ---
pg.run()



