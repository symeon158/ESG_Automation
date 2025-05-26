import streamlit as st


st.set_page_config(layout="centered")
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
project_3_page = st.Page(
    "views/L&D.py",
    title="L&D",
    icon="🏋️",
)
project_4_page = st.Page(
    "views/ChatBot RAG.py",
    title="ChatBot",
    icon="🤖",
)

project_5_page = st.Page(
    "views/OD.py",
    title="OD",
    icon="🏋️",
)
project_6_page = st.Page(
    "views/AI_Tabular.py",
    title="AI Tabular",
    icon="🤖",
)
project_7_page = st.Page(
    "views/Sql_AI.py",
    title="SQL AI",
    icon="🤖",
)
project_8_page = st.Page(
    "views/Graph_RAG.py",
    title="ChatBot Graph_RAG",
    icon="🤖",
)

project_9_page = st.Page(
    "views/aggrid.py",
    title="Aggrid_St",
    icon="💻",
)

project_10_page = st.Page(
    "views/chatbot.py",
    title="ChatBot_RAG_LLM",
    icon="🤖",
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_1_page, project_2_page, project_5_page, project_9_page,  project_4_page, project_6_page],
    }
)


# --- SHARED ON ALL PAGES ---
#st.logo("assets/codingisfun_logo.png")
st.sidebar.markdown("Created with ❤️ by [Symeon Papadopoulos](https://www.linkedin.com/in/symeon-papadopoulos-b242b1166/)")


# --- RUN NAVIGATION ---
pg.run()