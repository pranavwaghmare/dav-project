import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(uploaded_file):
    """
    Loads data from an uploaded CSV or Excel file safely.
    Returns a Pandas DataFrame or None if an error occurs.
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file format. Please upload CSV or Excel."
        
        if df.empty:
            return None, "The uploaded file is empty."
            
        return df, None
    except Exception as e:
        return None, f"Error loading file: {str(e)}"
