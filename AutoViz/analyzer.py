import pandas as pd
import numpy as np

def detect_semantic_role(col_name, series):
    """
    Identifies the semantic role of a column rather than just its raw dtype.
    Roles: temporal, identifier, categorical_binary, categorical_entity, measure
    """
    col_name_lower = str(col_name).lower()
    clean_series = series.dropna()
    num_unique = clean_series.nunique()
    total_valid = len(clean_series)
    
    if total_valid == 0:
        return 'unknown'
        
    unique_ratio = num_unique / total_valid

    # 1. Temporal
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'temporal'

    # 2. Categorical Binary
    if num_unique == 2:
        return 'categorical_binary'

    # 3. Identifier
    id_keywords = ['id', 'roll', 'reg', 'email', 'phone', 'contact', 'uuid', 'guid']
    has_id_keyword = any(keyword in col_name_lower.split('_') or keyword == col_name_lower for keyword in id_keywords)
    
    if has_id_keyword and unique_ratio > 0.8:
        return 'identifier'
    
    if series.dtype == 'object' and unique_ratio > 0.95:
        # High cardinality text is likely an identifier or free text, not useful for grouping
        return 'identifier'

    # 4. Measure vs Categorical Entity
    if pd.api.types.is_numeric_dtype(series):
        if 'year' in col_name_lower and 1900 <= clean_series.min() <= 2100 and clean_series.max() <= 2100:
             return 'temporal'
             
        if has_id_keyword:
             return 'identifier' # numeric ids
             
        is_int = pd.api.types.is_integer_dtype(series)
        
        # Entities can have higher cardinality if they are integers (e.g., Store=1..45)
        if num_unique <= 100 and (is_int or unique_ratio < 0.05):
             # Don't classify obvious measures as entities unless they are really small cardinality
             if num_unique <= 15:
                 return 'categorical_entity'
             elif is_int and not any(k in col_name_lower for k in ['salary', 'sales', 'revenue', 'amount', 'price', 'profit', 'cgpa', 'score', 'temperature', 'fuel', 'cpi', 'unemployment']):
                 return 'categorical_entity'
                 
        return 'measure'
    else:
        # Non-numeric
        if num_unique <= 20 or unique_ratio < 0.5:
            return 'categorical_entity'
        else:
            return 'identifier' # Fallback for high-cardinality text

def detect_theme(df):
    """
    Guesses the dataset theme based on column names to provide context.
    """
    cols = ' '.join(df.columns).lower()
    
    themes = {
        'Sales': ['order', 'product', 'price', 'quantity', 'sales', 'revenue', 'customer', 'store', 'discount'],
        'HR': ['employee', 'salary', 'department', 'attrition', 'performance', 'hire', 'manager'],
        'Education': ['student', 'branch', 'mark', 'cgpa', 'attendance', 'semester', 'course']
    }
    
    theme_scores = {theme: sum(1 for kw in keywords if kw in cols) for theme, keywords in themes.items()}
    
    best_theme = max(theme_scores, key=theme_scores.get)
    if theme_scores[best_theme] >= 2:
        return best_theme
    return 'Generic'

def detect_metrics(df, measure_cols):
    """
    Ranks measurement columns by analytical importance based on semantics.
    Returns (primary_metrics, secondary_metrics)
    """
    if not measure_cols:
        return [], []
        
    tier1_kws = ['sales', 'revenue', 'salary', 'total', 'amount', 'price', 'profit', 'cgpa', 'score', 'mark']
    tier2_kws = ['quantity', 'attendance', 'rate', 'margin', 'count']
    
    tier1, tier2, others = [], [], []
    
    for col in measure_cols:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in tier1_kws):
            tier1.append(col)
        elif any(kw in col_lower for kw in tier2_kws):
            tier2.append(col)
        else:
            others.append(col)
            
    if tier1:
        return tier1, tier2 + others
    elif tier2:
        return tier2, others
    else:
        return others, []

def profile_dataset(df):
    """
    Analyzes the dataframe and returns a semantic profile.
    """
    profile = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'theme': detect_theme(df),
        'roles': {
            'temporal': [],
            'identifier': [],
            'categorical_binary': [],
            'categorical_entity': [],
            'measure': []
        },
        'primary_metrics': [],
        'secondary_metrics': []
    }
    
    for col in df.columns:
        role = detect_semantic_role(col, df[col])
        if role in profile['roles']:
             profile['roles'][role].append(col)
             
    p, s = detect_metrics(df, profile['roles']['measure'])
    profile['primary_metrics'] = p
    profile['secondary_metrics'] = s
                 
    return profile
