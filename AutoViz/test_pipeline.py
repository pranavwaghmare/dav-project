import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs('sample_data', exist_ok=True)

# Generate Walmart_Sales.csv
if not os.path.exists('sample_data/Walmart_Sales.csv'):
    print("Generating Walmart_Sales.csv...")
    num_weeks = 52
    num_stores = 45
    
    dates = pd.date_range(start='2010-02-05', periods=num_weeks, freq='W-FRI')
    stores = np.arange(1, num_stores + 1)
    
    # Format date as DD-MM-YYYY to stress test date parser
    date_strs = [d.strftime('%d-%m-%Y') for d in dates]
    
    data = []
    for store in stores:
        for date_str in date_strs:
            weekly_sales = np.random.normal(1000000, 200000)
            holiday_flag = np.random.choice([0, 1], p=[0.9, 0.1])
            temperature = np.random.normal(60, 20)
            fuel_price = np.random.normal(3.5, 0.5)
            cpi = np.random.normal(200, 10)
            unemployment = np.random.normal(7, 1)
            
            data.append({
                'Store': store,
                'Date': date_str,
                'Weekly_Sales': weekly_sales,
                'Holiday_Flag': holiday_flag,
                'Temperature': temperature,
                'Fuel_Price': fuel_price,
                'CPI': cpi,
                'Unemployment': unemployment
            })
            
    pd.DataFrame(data).to_csv('sample_data/Walmart_Sales.csv', index=False)
    print("Generated Walmart_Sales.csv")

# Now run the test pipeline
from utils import load_data, attempt_date_parsing
from analyzer import profile_dataset
from insights import generate_kpis, generate_insights
from visualization_engine import generate_visualizations

datasets = [
    'sample_data/students.xlsx',
    'sample_data/sales_data.xlsx',
    'sample_data/Walmart_Sales.csv',
    'sample_data/hr_data.csv'
]

for ds in datasets:
    if not os.path.exists(ds):
         continue
         
    print(f"\n{'='*50}\nTesting {ds}\n{'='*50}")
    
    if ds.endswith('.csv'):
        df = pd.read_csv(ds)
    else:
        df = pd.read_excel(ds)
        
    df = attempt_date_parsing(df)
    
    profile = profile_dataset(df)
    print("Theme:", profile['theme'])
    print("Primary Metrics:", profile['primary_metrics'])
    print("Secondary Metrics:", profile['secondary_metrics'])
    for role, cols in profile['roles'].items():
         print(f"  {role}: {cols}")
         
    charts = generate_visualizations(df, profile)
    print("\nCharts Generated:")
    for chart in charts:
         print(f"  [{chart['type'].upper()}] {chart['title']} (x={chart.get('x')}, y={chart.get('y')}) | Score: {chart['score']}")
