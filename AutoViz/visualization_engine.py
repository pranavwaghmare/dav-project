import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_visualizations(df, profile):
    """
    Rule-based engine to recommend and generate Plotly charts.
    Returns a list of dictionaries containing chart titles, descriptions, and plotly figure objects.
    """
    charts = []
    
    numerical_cols = profile['columns']['numerical']
    categorical_cols = profile['columns']['categorical']
    datetime_cols = profile['columns']['datetime']
    
    # Track used combinations to avoid very similar charts
    used_combinations = set()
    
    # 1. Distribution of a key numerical column
    if numerical_cols:
        target_col = numerical_cols[0]
        # Prefer important looking columns
        for col in numerical_cols:
            if any(k in str(col).lower() for k in ['cgpa', 'attendance', 'package', 'mark', 'score']):
                target_col = col
                break
                
        fig = px.histogram(df, x=target_col, marginal="box", 
                           title=f"Distribution of {target_col}",
                           template="plotly_white",
                           color_discrete_sequence=['#4C78A8'])
        charts.append({
            "title": f"{target_col} Distribution",
            "desc": f"Shows how {target_col} is distributed across all records.",
            "fig": fig
        })
        used_combinations.add(f"dist_{target_col}")

    # 2. Categorical vs Numerical (Bar Chart)
    if categorical_cols and numerical_cols:
        # Pick best category (e.g. Branch) and best numerical (e.g. CGPA)
        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]
        
        for col in categorical_cols:
            if df[col].nunique() <= 15: # Avoid too many bars
                 cat_col = col
                 if any(k in str(col).lower() for k in ['branch', 'dept', 'department']):
                     break
                     
        for col in numerical_cols:
             if any(k in str(col).lower() for k in ['cgpa', 'package', 'attendance']):
                 num_col = col
                 break
                 
        agg_df = df.groupby(cat_col)[num_col].mean().reset_index()
        fig = px.bar(agg_df, x=cat_col, y=num_col, 
                     title=f"Average {num_col} by {cat_col}",
                     template="plotly_white",
                     color=cat_col)
        charts.append({
            "title": f"{num_col} by {cat_col}",
            "desc": f"Compares the average {num_col} across different {cat_col}s.",
            "fig": fig
        })
        used_combinations.add(f"bar_{cat_col}_{num_col}")
        
    # 3. Categorical Distribution (Pie/Donut)
    if categorical_cols:
        for col in categorical_cols:
            if df[col].nunique() <= 5: # Perfect for pie charts
                fig = px.pie(df, names=col, hole=0.4, 
                             title=f"Distribution of {col}",
                             template="plotly_white")
                charts.append({
                    "title": f"{col} Breakdown",
                    "desc": f"Shows the proportion of each {col}.",
                    "fig": fig
                })
                used_combinations.add(f"pie_{col}")
                break # Just one pie chart is enough

    # 4. Scatter Plot for Two Numerical Columns
    if len(numerical_cols) >= 2:
        col1, col2 = numerical_cols[0], numerical_cols[1]
        
        # Try to find a good pair like Attendance vs CGPA
        found_pair = False
        for c1 in numerical_cols:
            if 'attendance' in str(c1).lower():
                col1 = c1
                for c2 in numerical_cols:
                     if 'cgpa' in str(c2).lower() or 'mark' in str(c2).lower():
                         col2 = c2
                         found_pair = True
                         break
            if found_pair: break
            
        if col1 != col2:
            fig = px.scatter(df, x=col1, y=col2, 
                             title=f"{col1} vs {col2}",
                             template="plotly_white",
                             trendline="ols" if len(df) > 5 else None,
                             opacity=0.7)
            charts.append({
                "title": f"Correlation: {col1} vs {col2}",
                "desc": f"Visualizes the relationship between {col1} and {col2}.",
                "fig": fig
            })
            used_combinations.add(f"scatter_{col1}_{col2}")
            
    # 5. Time Series (Line Chart)
    if datetime_cols and numerical_cols:
        date_col = datetime_cols[0]
        num_col = numerical_cols[0]
        
        # Aggregate by date if needed, or just plot if it's already a time series
        # Simple approach: just plot it
        sorted_df = df.sort_values(by=date_col)
        fig = px.line(sorted_df, x=date_col, y=num_col, 
                      title=f"{num_col} Over Time ({date_col})",
                      template="plotly_white")
        charts.append({
            "title": f"Trend of {num_col}",
            "desc": f"Shows how {num_col} changes over time.",
            "fig": fig
        })

    # 6. Multiple Related Numerical Columns (e.g., Subjects)
    subject_keywords = ['math', 'dsa', 'dbms', 'os', 'network', 'physics', 'chemistry', 'english']
    subject_cols = [c for c in numerical_cols if any(k in str(c).lower() for k in subject_keywords) or ('mark' in str(c).lower() and c not in [num_col for num_col in numerical_cols if 'total' in str(num_col).lower()])]
    
    # Alternatively, just pick columns with similar scales (e.g., max is around 100)
    if not subject_cols:
         similar_scale_cols = [c for c in numerical_cols if df[c].max() <= 100 and df[c].max() > 10 and 'attendance' not in str(c).lower() and 'pct' not in str(c).lower()]
         if len(similar_scale_cols) >= 3:
             subject_cols = similar_scale_cols
             
    if len(subject_cols) >= 2:
        avgs = df[subject_cols].mean().reset_index()
        avgs.columns = ['Subject', 'Average Score']
        fig = px.bar(avgs, x='Subject', y='Average Score',
                     title="Average Scores Across Subjects",
                     template="plotly_white",
                     color='Subject')
        charts.append({
             "title": "Subject-wise Performance",
             "desc": "Compares average performance across different subjects or metrics.",
             "fig": fig
        })
        
    return charts[:6] # Limit to 6 charts to avoid clutter
