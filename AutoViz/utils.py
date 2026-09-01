import pandas as pd
import streamlit as st
import os
import re

def attempt_date_parsing(df):
    """
    Attempts to parse columns into datetime if they seem like dates.
    Uses column name hints and checks parsing success rate.
    """
    date_keywords = ['date', 'time', 'timestamp', 'joined', 'created', 'updated']
    
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
            
        col_lower = str(col).lower()
        has_hint = any(k in col_lower for k in date_keywords)
        
        # Only try parsing object/string columns
        if df[col].dtype == 'object':
            # Fast check on a sample
            sample = df[col].dropna().head(20)
            if sample.empty:
                continue
                
            # If it has a date hint, or looks somewhat like a date (e.g., has hyphens/slashes and digits)
            if has_hint or sample.astype(str).str.contains(r'\d{2,4}[-/]\d{1,2}[-/]\d{1,4}').any():
                try:
                    # Attempt conversion on the whole column
                    parsed = pd.to_datetime(df[col], format='mixed', errors='coerce')
                    
                    # If conversion succeeded for at least 80% of non-null values
                    valid_original = df[col].notna().sum()
                    valid_parsed = parsed.notna().sum()
                    
                    if valid_original > 0 and (valid_parsed / valid_original) >= 0.8:
                        df[col] = parsed
                except:
                    pass
    return df

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
            
        df = attempt_date_parsing(df)
            
        return df, None
    except Exception as e:
        return None, f"Error loading file: {str(e)}"
