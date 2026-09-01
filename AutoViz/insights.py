import pandas as pd
import numpy as np

def get_agg_func(col_name, theme='Generic'):
    """
    Determines the appropriate aggregation function (sum or mean) based on metric semantics.
    """
    col_lower = str(col_name).lower()
    
    sum_kws = ['sales', 'revenue', 'total', 'amount', 'quantity', 'profit']
    mean_kws = ['price', 'salary', 'cgpa', 'attendance', 'rate', 'score', 'mark', 'age', 'margin', 'performance']
    
    if any(kw in col_lower for kw in sum_kws):
        return 'sum'
    if any(kw in col_lower for kw in mean_kws):
        return 'mean'
        
    # Fallback to theme if semantics are ambiguous
    if theme == 'Sales':
        return 'sum'
    elif theme in ['HR', 'Education']:
        return 'mean'
    
    return 'mean' # Safe default

def generate_kpis(df, profile):
    """
    Generates dynamic KPIs based on the primary metrics and dataset theme.
    """
    kpis = []
    kpis.append({"label": "Total Records", "value": profile['total_rows']})
    
    primary_metrics = profile['primary_metrics']
    theme = profile['theme']
    
    if not primary_metrics:
        return kpis
        
    # Take up to 2 primary metrics for KPIs
    for col in primary_metrics[:2]:
        agg_func = get_agg_func(col, theme)
        
        if agg_func == 'sum':
            total_val = df[col].sum()
            avg_val = df[col].mean()
            # Format nicely
            if total_val > 1000:
                kpis.append({"label": f"Total {col}", "value": f"{total_val/1000:.1f}k"})
            else:
                kpis.append({"label": f"Total {col}", "value": f"{total_val:.2f}"})
                
            kpis.append({"label": f"Avg {col}", "value": f"{avg_val:.2f}"})
        else:
            avg_val = df[col].mean()
            max_val = df[col].max()
            kpis.append({"label": f"Avg {col}", "value": f"{avg_val:.2f}"})
            kpis.append({"label": f"Highest {col}", "value": f"{max_val:.2f}"})
            
    return kpis[:4]

def generate_insights(df, profile):
    """
    Generates text-based insights based on statistical observations.
    """
    insights = []
    
    primary_metrics = profile['primary_metrics']
    categorical_entities = profile['roles']['categorical_entity']
    theme = profile['theme']
    
    if not primary_metrics:
        return ["Not enough numerical data to generate deep insights."]
        
    # 1. Insight: Categorical group with highest aggregate for a primary metric
    if categorical_entities and primary_metrics:
        cat_col = categorical_entities[0]
        num_col = primary_metrics[0]
        
        agg_func = get_agg_func(num_col, theme)
        
        if agg_func == 'sum':
            agg_by_cat = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
            agg_word = "total"
        else:
            agg_by_cat = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
            agg_word = "average"
            
        if len(agg_by_cat) > 1:
            top_cat = agg_by_cat.index[0]
            insights.append(f"**{top_cat}** has the highest {agg_word} **{num_col}** among all {cat_col}s.")
            
    # 2. Insight: Correlation
    measures = profile['roles']['measure']
    if len(measures) >= 2:
        # Take top 2 metrics
        col1 = measures[0] if len(primary_metrics) < 1 else primary_metrics[0]
        col2 = measures[1] if len(primary_metrics) < 2 else primary_metrics[1]
            
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
