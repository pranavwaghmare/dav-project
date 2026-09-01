import pandas as pd
import numpy as np

def generate_kpis(df, profile):
    """
    Generates dynamic KPIs based on the dataset.
    """
    kpis = []
    
    # Always show total records
    kpis.append({"label": "Total Records", "value": profile['total_rows']})
    
    numerical_cols = profile['columns']['numerical']
    
    if not numerical_cols:
        return kpis
        
    # Find important metrics to show as KPIs
    # Look for keywords in numerical columns
    for col in numerical_cols:
        col_lower = str(col).lower()
        if 'cgpa' in col_lower or 'gpa' in col_lower or 'mark' in col_lower or 'score' in col_lower:
            avg_val = df[col].mean()
            max_val = df[col].max()
            kpis.append({"label": f"Average {col}", "value": f"{avg_val:.2f}"})
            kpis.append({"label": f"Highest {col}", "value": f"{max_val:.2f}"})
            break # Just do one main score
            
    for col in numerical_cols:
        col_lower = str(col).lower()
        if 'attendance' in col_lower:
            avg_val = df[col].mean()
            kpis.append({"label": f"Average {col}", "value": f"{avg_val:.2f}%"})
            
            # Count below 75 if it seems like a percentage
            if df[col].max() <= 100:
                 below_75 = len(df[df[col] < 75])
                 kpis.append({"label": f"Below 75% {col}", "value": below_75})
            break
            
    for col in numerical_cols:
        col_lower = str(col).lower()
        if 'package' in col_lower or 'salary' in col_lower or 'lpa' in col_lower:
             avg_val = df[col].mean()
             max_val = df[col].max()
             kpis.append({"label": f"Average {col}", "value": f"{avg_val:.2f}"})
             kpis.append({"label": f"Highest {col}", "value": f"{max_val:.2f}"})
             break

    # If we didn't find any specific keywords, just take the first numerical column
    if len(kpis) == 1 and numerical_cols:
        col = numerical_cols[0]
        avg_val = df[col].mean()
        kpis.append({"label": f"Average {col}", "value": f"{avg_val:.2f}"})

    return kpis[:4] # Return at most 4 KPIs

def generate_insights(df, profile):
    """
    Generates text-based insights based on statistical observations.
    """
    insights = []
    
    numerical_cols = profile['columns']['numerical']
    categorical_cols = profile['columns']['categorical']
    
    if not numerical_cols:
        return ["Not enough numerical data to generate deep insights."]
        
    # 1. Insight: Categorical group with highest average for a numerical metric
    if categorical_cols and numerical_cols:
        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]
        
        # Try to find a 'better' numerical column (like CGPA or Package)
        for col in numerical_cols:
            if any(k in str(col).lower() for k in ['cgpa', 'package', 'salary', 'mark']):
                num_col = col
                break
                
        # Try to find a 'better' categorical column (like Branch or Department)
        for col in categorical_cols:
             if any(k in str(col).lower() for k in ['branch', 'dept', 'department', 'course']):
                 cat_col = col
                 break
                 
        avg_by_cat = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
        if len(avg_by_cat) > 1:
            top_cat = avg_by_cat.index[0]
            insights.append(f"**{top_cat}** has the highest average **{num_col}** among all {cat_col}s.")
            
    # 2. Insight: Percentage condition (e.g., Attendance)
    for col in numerical_cols:
        if 'attendance' in str(col).lower() and df[col].max() <= 100:
            below_75 = len(df[df[col] < 75])
            total = len(df)
            if total > 0:
                pct = (below_75 / total) * 100
                insights.append(f"**{pct:.1f}%** of records have **{col}** below 75%.")
            break
            
    # 3. Insight: Correlation
    if len(numerical_cols) >= 2:
        # Find two most interesting columns
        col1, col2 = numerical_cols[0], numerical_cols[1]
        for c in numerical_cols:
            if 'attendance' in str(c).lower(): col1 = c
            if 'cgpa' in str(c).lower(): col2 = c
            
        if col1 != col2:
            correlation = df[col1].corr(df[col2])
            if pd.notna(correlation):
                strength = "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak"
                direction = "positive" if correlation > 0 else "negative"
                if abs(correlation) > 0.3:
                     insights.append(f"**{col1}** and **{col2}** show a **{strength} {direction} correlation**.")
                     
    if not insights:
        insights.append("Data processed successfully. Explore the charts below for visual insights.")
        
    return insights
