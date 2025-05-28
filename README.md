# 📊 ESG Automation Dashboard

## 🔍 Overview
The **ESG Automation Dashboard** is a powerful, data-driven Streamlit application designed to automate and centralize Environmental, Social, and Governance (ESG) reporting within HR. This tool enables dynamic analysis of key ESG metrics like headcount, turnover, contract types, gender representation, compensation trends, and executive roles—empowering HR teams with strategic, real-time insights.
- 👉 Use the App [Streamlit Cloud](https://esgautomation-6lucvjswyrkv3q5eadl9op.streamlit.app/OD)

## 🎯 Purpose
This project was created to:
- Automate ESG-related HR reporting workflows
- Eliminate manual and error-prone Excel tracking
- Align workforce reporting with ESG and sustainability goals
- Enable interactive, web-based analytics for HR decision-making
- Support transparent and inclusive pay practices, training planning, and hiring analysis

## 🚀 Features
- ✅ **Interactive filtering** by division, department, contract type, gender, age group, and more  
- 📈 **Visual analytics** for hires, departures, and headcount trends  
- 🧠 **Role classification engine** for auto-tagging staff as Worker, Manager, Director, etc.
- 🧮 Pay Gap Insights: Detect and analyze remuneration gaps between demographic groups
- 🧑‍🏫 OD & Training module: View training plan completions and compare performance by division, gender, or region  
- 👥 **Diversity insights** for gender representation across senior roles  
- 💾 **Export to CSV** for external reporting or ESG audits  
- 📊 **Grouped KPIs** with dynamic Plotly charts and responsive dashboard cards

## 🧠 Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/) 1.33+
- **Data Analysis:** [Pandas](https://pandas.pydata.org/)
- **Visualization:** [Plotly Express](https://plotly.com/python/plotly-express/)
- **Deployment:** [Streamlit Community Cloud](https://streamlit.io/cloud)

## 📁 Project Structure
├── ESG_Analysis.py             # Pages setup
├── Comp&Ben.py                 # Salary & Turnover Analysis, Overall Gender Pay Gap, Remuneration Ratio, Turnover Analysis
├── OD.py                       # Organizational Development: Training & skills planning
├── HR Data Analyst.py          # Holistic HR view: headcount, hires, departures, executive mapping
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Optional: Theme and layout settings
└── data/
    └── example_hr_data.csv     # Sample input format (not public)


## 📊 Use Cases
- Monitor monthly and annual headcount trends across companies, divisions and departments
- Analyze hires and departures, voluntary vs involuntary turnover
- Compare contract types (e.g., full-time, part-time, temporary)
- Evaluate training plan completions, segmenting by business unit and genderDetect gender pay gaps across grades and job titles
- Assess managerial and executive representation by diversity groups
- Export insights for ESG audits, board reports, or compliance documentation
  
## 🌐Deployment
This application is designed for internal use. It has deployed on Streamlit Cloud!
- Try it On [Streamlit Cloud](https://esgautomation-6lucvjswyrkv3q5eadl9op.streamlit.app/OD)

## 👨‍💼 About the Author
**[Papadopoulos_Symeon]** — HR Data Analyst & ESG Reporting Lead.  
This project reflects a unique blend of experience in data analytics, workforce planning, and ESG automation.

## 💬 Contact
📨 Connect on [LinkedIn](https://www.linkedin.com/in/symeon-papadopoulos-b242b1166/)  

---

> _\"Turning raw workforce data into actionable ESG intelligence.\"_

