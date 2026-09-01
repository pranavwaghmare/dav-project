import plotly.express as px
import pandas as pd
from insights import get_agg_func

def generate_visualizations(df, profile):
    """
    Candidate generation & scoring engine.
    Generates potential charts based on semantic roles, scores them,
    filters redundancies, and returns the top charts.
    """
    candidates = []
    
    temporal_cols = profile['roles']['temporal']
    categorical_entities = profile['roles']['categorical_entity']
    categorical_binaries = profile['roles']['categorical_binary']
    measures = profile['roles']['measure']
    primary_metrics = profile['primary_metrics']
    theme = profile['theme']
    
    # 1. Time Series
    if temporal_cols and primary_metrics:
        for t_col in temporal_cols[:2]:
            for m_col in primary_metrics[:2]:
                agg_func = get_agg_func(m_col, theme)
                score = 10 # High priority
                
                # We need to aggregate by time in case there are multiple entries per timestamp
                # For simplicity, we just sort and plot, Plotly handles it relatively well, 
                # but an aggregation is better. Let's do a simple group by.
                try:
                    if agg_func == 'sum':
                        agg_df = df.groupby(t_col)[m_col].sum().reset_index()
                    else:
                        agg_df = df.groupby(t_col)[m_col].mean().reset_index()
                        
                    agg_df = agg_df.sort_values(by=t_col)
                    
                    fig = px.line(agg_df, x=t_col, y=m_col, 
                                  title=f"{m_col} Trend Over Time",
                                  template="plotly_white")
                                  
                    candidates.append({
                        "id": f"time_{t_col}_{m_col}",
                        "title": f"Trend of {m_col}",
                        "desc": f"Shows how {m_col} changes over {t_col}.",
                        "fig": fig,
                        "score": score,
                        "type": "line",
                        "x": t_col,
                        "y": m_col
                    })
                except:
                    pass

    # 2. Aggregate Comparison (Bar Charts)
    if categorical_entities and primary_metrics:
        for cat_col in categorical_entities[:3]: # limit to top 3
            for m_col in primary_metrics[:3]:
                # Score based on cardinality (ideal is 3-15)
                cardinality = df[cat_col].nunique()
                if cardinality > 40:
                    continue # Too many bars
                    
                score = 8
                if 3 <= cardinality <= 15:
                    score += 2
                    
                agg_func = get_agg_func(m_col, theme)
                
                try:
                    if agg_func == 'sum':
                        agg_df = df.groupby(cat_col)[m_col].sum().reset_index()
                        title = f"Total {m_col} by {cat_col}"
                    else:
                        agg_df = df.groupby(cat_col)[m_col].mean().reset_index()
                        title = f"Average {m_col} by {cat_col}"
                        
                    # Sort for better visualization
                    agg_df = agg_df.sort_values(by=m_col, ascending=False).head(20)
                    
                    fig = px.bar(agg_df, x=cat_col, y=m_col, 
                                 title=title,
                                 template="plotly_white",
                                 color=cat_col if cardinality <= 10 else None)
                                 
                    candidates.append({
                        "id": f"bar_{cat_col}_{m_col}",
                        "title": f"{m_col} by {cat_col}",
                        "desc": f"Compares {m_col} across different {cat_col}s.",
                        "fig": fig,
                        "score": score,
                        "type": "bar",
                        "x": cat_col,
                        "y": m_col
                    })
                except:
                    pass

    # 3. Composition (Pie Charts)
    all_cats = categorical_entities + categorical_binaries
    if all_cats:
        for cat_col in all_cats:
            cardinality = df[cat_col].nunique()
            if cardinality <= 7:
                score = 5
                if cardinality == 2: score += 1 # Binaries are good for pies
                
                try:
                    fig = px.pie(df, names=cat_col, hole=0.4, 
                                 title=f"Distribution of {cat_col}",
                                 template="plotly_white")
                                 
                    candidates.append({
                        "id": f"pie_{cat_col}",
                        "title": f"{cat_col} Breakdown",
                        "desc": f"Shows the proportion of each {cat_col}.",
                        "fig": fig,
                        "score": score,
                        "type": "pie",
                        "x": cat_col,
                        "y": None
                    })
                except:
                    pass

    # 4. Correlation (Scatter Plot)
    if len(measures) >= 2:
        # Check pairs of top measures
        for i in range(min(3, len(measures))):
            for j in range(i+1, min(4, len(measures))):
                col1, col2 = measures[i], measures[j]
                
                try:
                    correlation = df[col1].corr(df[col2])
                    if pd.isna(correlation): continue
                    
                    # Score based on correlation strength
                    abs_corr = abs(correlation)
                    if abs_corr < 0.1:
                        score = 2
                    elif abs_corr < 0.3:
                        score = 4
                    elif abs_corr < 0.7:
                        score = 7
                    else:
                        score = 9
                        
                    # Cap sample size to avoid slow rendering
                    sample_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
                    
                    fig = px.scatter(sample_df, x=col1, y=col2, 
                                     title=f"{col1} vs {col2}",
                                     template="plotly_white",
                                     trendline="ols" if len(sample_df) > 5 else None,
                                     opacity=0.7)
                                     
                    candidates.append({
                        "id": f"scatter_{col1}_{col2}",
                        "title": f"Correlation: {col1} vs {col2}",
                        "desc": f"Visualizes the relationship between {col1} and {col2}.",
                        "fig": fig,
                        "score": score,
                        "type": "scatter",
                        "x": col1,
                        "y": col2
                    })
                except:
                    pass

    # 5. Distribution (Histogram)
    if primary_metrics:
        for m_col in primary_metrics[:2]:
            score = 6
            try:
                fig = px.histogram(df, x=m_col, marginal="box", 
                                   title=f"Distribution of {m_col}",
                                   template="plotly_white")
                                   
                candidates.append({
                    "id": f"dist_{m_col}",
                    "title": f"{m_col} Distribution",
                    "desc": f"Shows how {m_col} is distributed across all records.",
                    "fig": fig,
                    "score": score,
                    "type": "histogram",
                    "x": m_col,
                    "y": None
                })
            except:
                pass

    # Redundancy Filtering & Selection
    # Sort by score descending
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    selected_charts = []
    used_x = set()
    used_y = set()
    type_counts = {}
    
    for cand in candidates:
        if len(selected_charts) >= 6: # max 6 charts
            break
            
        c_type = cand['type']
        
        # Avoid too many of the same type (unless bar charts which are versatile)
        if type_counts.get(c_type, 0) >= 2 and c_type != 'bar':
            continue
        if type_counts.get(c_type, 0) >= 3 and c_type == 'bar':
            continue
            
        # Avoid exact same X and Y combination
        xy_combo = f"{cand['x']}_{cand['y']}"
        if cand['x'] and cand['y']:
             if xy_combo in used_x: # reusing used_x as a combo tracker for simplicity here
                 continue
                 
        selected_charts.append(cand)
        if cand['x'] and cand['y']:
            used_x.add(xy_combo)
            
        type_counts[c_type] = type_counts.get(c_type, 0) + 1
        
    return selected_charts
