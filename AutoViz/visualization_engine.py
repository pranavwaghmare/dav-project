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
    
    # Define our targets
    target_metrics = profile['primary_metrics']
    if not target_metrics:
        # Fallback to secondary if no primary exists
        target_metrics = profile['secondary_metrics']
        
    theme = profile['theme']
    
    # 1. Time Series (Highest Priority)
    if temporal_cols and target_metrics:
        for t_col in temporal_cols[:1]: # usually one primary time axis is enough
            for m_col in target_metrics[:2]:
                agg_func = get_agg_func(m_col, theme)
                score = 15 # Highest priority
                
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

    # 2. Aggregate Comparison (Bar Charts with Entities)
    if categorical_entities and target_metrics:
        for cat_col in categorical_entities[:3]:
            for m_col in target_metrics[:2]:
                cardinality = df[cat_col].nunique()
                if cardinality > 40:
                    continue 
                    
                score = 10
                if 3 <= cardinality <= 15:
                    score = 12 # Ideal cardinality
                    
                agg_func = get_agg_func(m_col, theme)
                
                try:
                    if agg_func == 'sum':
                        agg_df = df.groupby(cat_col)[m_col].sum().reset_index()
                        title = f"Total {m_col} by {cat_col}"
                    else:
                        agg_df = df.groupby(cat_col)[m_col].mean().reset_index()
                        title = f"Average {m_col} by {cat_col}"
                        
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

    # 3. Aggregate Comparison (Bar Charts with Binaries)
    if categorical_binaries and target_metrics:
        for cat_col in categorical_binaries[:2]:
            for m_col in target_metrics[:2]:
                score = 11
                agg_func = get_agg_func(m_col, theme)
                try:
                    if agg_func == 'sum':
                        agg_df = df.groupby(cat_col)[m_col].sum().reset_index()
                        title = f"Total {m_col} by {cat_col}"
                    else:
                        agg_df = df.groupby(cat_col)[m_col].mean().reset_index()
                        title = f"Average {m_col} by {cat_col}"
                        
                    fig = px.bar(agg_df, x=cat_col, y=m_col, 
                                 title=title,
                                 template="plotly_white",
                                 color=cat_col)
                                 
                    candidates.append({
                        "id": f"bar_{cat_col}_{m_col}",
                        "title": f"{m_col} by {cat_col}",
                        "desc": f"Compares {m_col} between {cat_col} groups.",
                        "fig": fig,
                        "score": score,
                        "type": "bar",
                        "x": cat_col,
                        "y": m_col
                    })
                except:
                    pass

    # 4. Correlation (Target-Aware Scatter Plot)
    if target_metrics and profile['secondary_metrics']:
        for m_col in target_metrics[:2]:
            for s_col in profile['secondary_metrics'][:3]:
                if m_col == s_col: continue
                try:
                    correlation = df[m_col].corr(df[s_col])
                    if pd.isna(correlation): continue
                    
                    abs_corr = abs(correlation)
                    if abs_corr < 0.2:
                        continue # Skip weak correlations entirely to reduce noise
                        
                    score = 5 + int(abs_corr * 4) # Scale up to 9
                    
                    sample_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df
                    
                    fig = px.scatter(sample_df, x=s_col, y=m_col, 
                                     title=f"{m_col} vs {s_col}",
                                     template="plotly_white",
                                     trendline="ols" if len(sample_df) > 5 else None,
                                     opacity=0.7)
                                     
                    candidates.append({
                        "id": f"scatter_{s_col}_{m_col}",
                        "title": f"Correlation: {m_col} vs {s_col}",
                        "desc": f"Visualizes the relationship between {m_col} and {s_col}.",
                        "fig": fig,
                        "score": score,
                        "type": "scatter",
                        "x": s_col,
                        "y": m_col
                    })
                except:
                    pass

    # 5. Distribution (Histogram)
    if target_metrics:
        for m_col in target_metrics[:2]:
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

    # 6. Fallback Composition (Pie Charts) - Only if no better charts
    all_cats = categorical_entities + categorical_binaries
    if all_cats:
        for cat_col in all_cats:
            cardinality = df[cat_col].nunique()
            if cardinality <= 5:
                score = 3 # Very low priority compared to target-aware charts
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

    # Redundancy Filtering & Selection
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    selected_charts = []
    used_x = set()
    used_y = set()
    type_counts = {}
    
    for cand in candidates:
        if len(selected_charts) >= 6: 
            break
            
        c_type = cand['type']
        
        # Don't strictly limit bar charts, they are usually the best
        if type_counts.get(c_type, 0) >= 1 and c_type in ['pie', 'histogram']:
            continue
        if type_counts.get(c_type, 0) >= 2 and c_type == 'scatter':
            continue
            
        xy_combo = f"{cand['x']}_{cand['y']}"
        if cand['x'] and cand['y']:
             if xy_combo in used_x: 
                 continue
                 
        selected_charts.append(cand)
        if cand['x'] and cand['y']:
            used_x.add(xy_combo)
            
        type_counts[c_type] = type_counts.get(c_type, 0) + 1
        
    return selected_charts
