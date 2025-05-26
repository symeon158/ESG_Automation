import streamlit as st

logo_url = "https://aldom.gr/wp-content/uploads/2020/05/alumil.png"
# Define the HTML and CSS
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG Automation Alumil S.A.</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

        body {
            background-color: #f4f4f9;
            font-family: 'Poppins', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .title {
            font-size: 3em;
            color: #333;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            position: relative;
            font-weight: bold;
            background: linear-gradient(to right, #FFD700, #000000);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 3s infinite;
        }
        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        .title::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 5px;
            background-color: #FFD700;
            bottom: -10px;
            left: 0;
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.5s ease-out;
        }
        .title:hover::after {
            transform: scaleX(1);
            transform-origin: bottom left;
        }
    </style>
</head>
<body>
    <div class="title">ESG AUTOMATION ALUMIL S.A.</div>
</body>
</html>
"""

# Display the content using Streamlit
st.markdown(html_content, unsafe_allow_html=True)

st.write(" ")

# ESG Information Page
st.title("🌱 Environmental, Social, and Governance (ESG)")

st.markdown("""
**Driving Sustainable Business**

In today’s world, companies are evaluated not only based on their financial performance but also on how they manage their responsibilities toward the environment, society, and governance practices. ESG is the key framework for this evaluation.

### 🌍 Environmental
- **Energy Usage:** Efficient energy consumption and renewable energy adoption.
- **Waste Management:** Reducing waste and promoting recycling.
- **Carbon Footprint:** Initiatives to lower greenhouse gas emissions.
- **Water Conservation:** Sustainable water usage and conservation strategies.

### 🤝 Social
- **Employee Wellbeing:** Ensuring a safe and inclusive workplace.
- **Diversity & Inclusion:** Promoting equal opportunities for all employees.
- **Community Engagement:** Supporting and giving back to local communities.
- **Customer Satisfaction:** Upholding high standards in product and service quality.

### 🏛️ Governance
- **Board Diversity:** Encouraging diverse leadership in decision-making.
- **Transparency:** Open and honest reporting of company performance.
- **Anti-Corruption Policies:** Strong policies to prevent unethical practices.
- **Shareholders' Rights:** Ensuring fair treatment of investors and stakeholders.

**Automating ESG**  
By automating ESG reporting, companies can streamline their efforts in tracking and achieving their sustainability goals efficiently, building a better world for future generations.
""")

# Inject CSS for sidebar logo styling
st.markdown("""
    <style>
    .sidebar-logo {
        padding-top: 30px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .sidebar-logo img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border: 2px solid #FFD700;
        padding: 5px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Custom HTML to render the styled logo in the sidebar
st.sidebar.markdown(
    f"""
    <div class="sidebar-logo">
        <img src="{logo_url}" alt="Alumil Logo">
    </div>
    """,
    unsafe_allow_html=True
)

