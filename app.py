import streamlit as st
import os
import pandas as pd
from market_research_agent import generate_use_cases

# Set page configuration
st.set_page_config(
    page_title="AI Use Case Generator",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #4527A0;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #5E35B1;
    margin-bottom: 1rem;
}
.info-text {
    font-size: 1rem;
    color: #333;
}
.result-container {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>AI & GenAI Use Case Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='info-text'>This tool uses a multi-agent system to research industries or companies and generate relevant AI use cases with implementation resources.</p>", unsafe_allow_html=True)

# Create sidebar for API key inputs
with st.sidebar:
    st.header("API Configuration")
    st.info("Enter your API keys to enable the search functionality.")

    openai_api_key = st.text_input("OpenAI API Key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", type="password")

    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if tavily_api_key:
        os.environ["TAVILY_API_KEY"] = tavily_api_key

    st.markdown("### About")
    st.info(
        "This application uses CrewAI and LangChain to create a multi-agent system "
        "that researches industries, generates AI use cases, and finds relevant resources."
    )

# Main content
st.markdown("<h2 class='sub-header'>Enter Industry or Company Information</h2>", unsafe_allow_html=True)

# Input form
with st.form("industry_form"):
    industry_or_company = st.text_input("Industry or Company Name", placeholder="e.g., Healthcare, Retail, Tesla, etc.")
    submitted = st.form_submit_button("Generate Use Cases")

# Process form submission
if submitted:
    if not industry_or_company:
        st.error("Please enter an industry or company name.")
    elif not openai_api_key or not tavily_api_key:
        st.error("Please enter your API keys in the sidebar.")
    else:
        with st.spinner(f"Researching {industry_or_company} and generating AI use cases... This may take a few minutes."):
            try:
                # Call the generate_use_cases function from market_research_agent.py
                results = generate_use_cases(industry_or_company)

                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["Industry Research", "AI Use Cases", "Implementation Resources"])

                with tab1:
                    st.markdown(f"<h3>Industry Research: {industry_or_company}</h3>", unsafe_allow_html=True)
                    st.markdown(results["industry_research"])

                with tab2:
                    st.markdown(f"<h3>AI Use Cases for {industry_or_company}</h3>", unsafe_allow_html=True)
                    st.markdown(results["use_cases"])

                with tab3:
                    st.markdown(f"<h3>Implementation Resources</h3>", unsafe_allow_html=True)
                    st.markdown(results["resources"])

                # Show success message
                st.success(f"Successfully generated AI use cases for {industry_or_company}!")
                st.info("Results have been saved as markdown files in the 'reports' directory.")

                # Add a button to open the reports directory
                if st.button("Open Reports Directory"):
                    import os
                    import webbrowser
                    reports_dir = os.path.abspath("reports")
                    if os.path.exists(reports_dir):
                        webbrowser.open(f"file://{reports_dir}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API keys and try again.")

# Display architecture diagram
st.markdown("<h2 class='sub-header'>System Architecture</h2>", unsafe_allow_html=True)
st.markdown("""
```mermaid
graph TD
    A[User Input] --> B[Industry Research Agent]
    B --> C[Use Case Generation Agent]
    C --> D[Resource Collection Agent]
    D --> E[Results]
    E --> F[Markdown Reports]
    E --> G[Web Interface Display]

    style B fill:#4527A0,stroke:#333,stroke-width:2px,color:white
    style C fill:#5E35B1,stroke:#333,stroke-width:2px,color:white
    style D fill:#7E57C2,stroke:#333,stroke-width:2px,color:white
```
""", unsafe_allow_html=True)

# Display sample use cases
if not submitted:
    st.markdown("<h2 class='sub-header'>Sample Use Cases</h2>", unsafe_allow_html=True)
    st.markdown("""
    ### AI-Powered Predictive Maintenance
    - **Objective**: Reduce equipment downtime and maintenance costs
    - **AI Application**: Machine learning algorithms analyze sensor data to predict failures
    - **Benefits**: Minimizes downtime, extends equipment lifespan, reduces costs

    ### Real-Time Quality Control with Computer Vision
    - **Objective**: Enhance product quality by detecting defects during manufacturing
    - **AI Application**: AI-powered computer vision systems identify defects in real-time
    - **Benefits**: Improves defect detection, reduces scrap rates, enhances customer satisfaction

    ### AI-Enabled Knowledge Management System
    - **Objective**: Improve employee productivity with easy access to company knowledge
    - **AI Application**: GenAI-powered chatbot for querying internal documents
    - **Benefits**: Accelerates onboarding, reduces support queries, enhances collaboration
    """)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center'>Created with ❤️ using CrewAI, LangChain, and Streamlit By Suhas Pete</p>", unsafe_allow_html=True)