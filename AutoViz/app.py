import streamlit as st
import pandas as pd
from utils import load_data
from analyzer import profile_dataset
from insights import generate_kpis, generate_insights
from visualization_engine import generate_visualizations

st.set_page_config(page_title="AutoViz", layout="wide", page_icon="📊")

# Header
st.title("📊 AutoViz")
st.subheader("Automatic Excel Analytics & Dashboard Generator")
st.markdown("Upload your college dataset (Excel or CSV), and AutoViz will automatically analyze it and generate an interactive dashboard.")
st.divider()

# Upload Section
st.header("1. Upload Dataset")
uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['csv', 'xls', 'xlsx'])

if uploaded_file is not None:
    # Load Data
    with st.spinner("Loading and analyzing data..."):
        df, error = load_data(uploaded_file)
        
    if error:
        st.error(error)
    else:
        st.success(f"File **{uploaded_file.name}** uploaded successfully!")
        
        # Profile Data
        profile = profile_dataset(df)
        
        # Dataset Overview
        st.header("2. Dataset Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", profile['total_rows'])
        col2.metric("Total Columns", profile['total_columns'])
        col3.metric("Missing Values", profile['missing_values'])
        col4.metric("Duplicate Rows", profile['duplicate_rows'])
        
        st.markdown(f"**Detected Theme:** {profile['theme']}")
        st.markdown(f"**Detected Primary Metrics:** {', '.join(profile['primary_metrics']) if profile['primary_metrics'] else 'None'}")
        st.markdown(f"**Detected Secondary Metrics:** {', '.join(profile['secondary_metrics']) if profile['secondary_metrics'] else 'None'}")
        
        st.markdown(f"**Semantic Column Roles:**")
        st.write(f"- Temporal (Dates/Times): {', '.join(profile['roles']['temporal']) if profile['roles']['temporal'] else 'None'}")
        st.write(f"- Measures (Continuous/Count): {', '.join(profile['roles']['measure']) if profile['roles']['measure'] else 'None'}")
        st.write(f"- Categorical Entities: {', '.join(profile['roles']['categorical_entity']) if profile['roles']['categorical_entity'] else 'None'}")
        st.write(f"- Binary Categories: {', '.join(profile['roles']['categorical_binary']) if profile['roles']['categorical_binary'] else 'None'}")
        st.write(f"- Identifiers/Text: {', '.join(profile['roles']['identifier']) if profile['roles']['identifier'] else 'None'}")
        st.divider()
        
        # KPIs
        st.header("3. Key Performance Indicators")
        kpis = generate_kpis(df, profile)
        if kpis:
            kpi_cols = st.columns(len(kpis))
            for i, kpi in enumerate(kpis):
                kpi_cols[i].metric(label=kpi['label'], value=kpi['value'])
        else:
            st.info("Not enough numerical data to generate KPIs.")
        st.divider()
            
        # Insights
        st.header("4. Key Insights")
        insights = generate_insights(df, profile)
        for insight in insights:
            st.markdown(f"- {insight}")
        st.divider()
            
        # Visualizations
        st.header("5. Automatically Generated Visualizations")
        with st.spinner("Generating recommended visualizations..."):
            charts = generate_visualizations(df, profile)
            
            if not charts:
                st.warning("Could not generate any meaningful visualizations based on the provided data types.")
            else:
                # Display charts in pairs (2 per row)
                for i in range(0, len(charts), 2):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader(charts[i]['title'])
                        st.caption(charts[i]['desc'])
                        st.plotly_chart(charts[i]['fig'], use_container_width=True)
                        
                    if i + 1 < len(charts):
                        with col2:
                            st.subheader(charts[i+1]['title'])
                            st.caption(charts[i+1]['desc'])
                            st.plotly_chart(charts[i+1]['fig'], use_container_width=True)
        st.divider()
        
        # Data Preview
        st.header("6. Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
