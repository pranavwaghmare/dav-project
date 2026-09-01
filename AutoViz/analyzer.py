import pandas as pd
import numpy as np
import re

def is_identifier_column(col_name, series):
    """
    Heuristics to detect if a column is an identifier (ID, Roll Number, etc.)
    """
    col_name_lower = str(col_name).lower()
    
    # Common identifier names
    id_keywords = ['id', 'roll', 'reg', 'email', 'phone', 'mobile', 'contact', 'uuid', 'guid', 'slno', 's.no', 'serial']
    
    # Check if any id_keyword is a distinct word in the column name or exactly matches
    for keyword in id_keywords:
        if keyword in col_name_lower.split('_') or keyword in col_name_lower.split(' ') or keyword == col_name_lower:
            # Check if it has a high number of unique values (most IDs are unique per row)
            if len(series.dropna()) > 0 and len(series.unique()) / len(series.dropna()) > 0.8:
                return True
                
    # Phone numbers or emails often have distinct patterns or highly unique string types
    if series.dtype == 'object' and len(series.dropna()) > 0:
        unique_ratio = len(series.unique()) / len(series.dropna())
        if unique_ratio > 0.95: 
            # Could be names or emails
            return True
            
    return False

def profile_dataset(df):
    """
    Analyzes the dataframe and returns a dictionary of column types and dataset stats.
    """
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'columns': {
            'numerical': [],
            'categorical': [],
            'datetime': [],
            'identifiers': []
        }
    }
    
    for col in df.columns:
        series = df[col]
        
        # Check if identifier
        if is_identifier_column(col, series):
            stats['columns']['identifiers'].append(col)
            continue
            
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            stats['columns']['datetime'].append(col)
            continue
            
        # Check numerical vs categorical
        if pd.api.types.is_numeric_dtype(series):
            # Sometimes categorical data is encoded as numbers (e.g., 0, 1 for Gender)
            # If a numeric column has very few unique values, it might be categorical
            unique_count = series.nunique()
            if unique_count <= 10 and unique_count < len(df) * 0.1:
                 stats['columns']['categorical'].append(col)
            else:
                 stats['columns']['numerical'].append(col)
        else:
            # Non-numeric, non-datetime -> categorical
            unique_count = series.nunique()
            # If it has too many unique values, it might just be free text or names (already caught mostly by identifier logic, but just in case)
            if unique_count > 0 and unique_count < len(df) * 0.5:
                stats['columns']['categorical'].append(col)
            else:
                 stats['columns']['identifiers'].append(col) # Fallback for high-cardinality text
                 
    return stats
