import pandas as pd
import streamlit as st
import os
import re

def attempt_date_parsing(df):
    """
    Attempts to parse columns into datetime if they seem like dates.
    Uses column name hints and checks parsing success rate.
    """
    date_keywords = ['date', 'time', 'timestamp', 'joined', 'created', 'updated', 'day', 'month', 'year']
    
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
            
        col_lower = str(col).lower()
        has_hint = any(k in col_lower for k in date_keywords)
        
        # Only try parsing object/string columns
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            sample = df[col].dropna().head(50)
            if sample.empty:
                continue
                
            # If it has a date hint, or looks somewhat like a date (e.g., has hyphens/slashes and digits)
            if has_hint or sample.astype(str).str.contains(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}').any():
                try:
                    valid_original = df[col].notna().sum()
                    if valid_original == 0: continue
                    
                    # Try default parsing first
                    parsed1 = pd.to_datetime(df[col], format='mixed', errors='coerce')
                    valid1 = parsed1.notna().sum()
                    
                    # Try dayfirst parsing for DD-MM-YYYY
                    parsed2 = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
                    valid2 = parsed2.notna().sum()
                    
                    if valid1 >= valid2 and (valid1 / valid_original) >= 0.8:
                        df[col] = parsed1
                    elif (valid2 / valid_original) >= 0.8:
                        df[col] = parsed2
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
