import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a title to the app
st.title("Healthcare Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/dental_healthcare_sample.csv')

try:
    # Load the data
    df = load_data()
    
    # Display a success message
    st.success("Data loaded successfully!")
    
    # Display sample data
    st.subheader("Sample Data")
    st.dataframe(df.head())
    
    # Display basic statistics
    st.subheader("Data Overview")
    st.write(f"Total Records: {len(df)}")
    st.write(f"Columns: {', '.join(df.columns)}")
    
    # Main page instructions
    st.markdown("""
    ## Welcome to the Healthcare Analytics Dashboard
    
    Please use the sidebar to navigate to different dashboards:
    
    - **Dashboard 1**: Patient Demographics Analysis
    - **Dashboard 2**: Treatment Effectiveness
    - **Dashboard 3**: Cost Analysis
    - **Dashboard 4**: Outcome Metrics
    
    Each dashboard provides different insights into the healthcare data.
    """)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please make sure the data file exists at 'data/healthcare_data.csv'")
