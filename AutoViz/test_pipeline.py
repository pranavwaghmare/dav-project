import pandas as pd
from utils import load_data
from analyzer import profile_dataset
from insights import generate_kpis, generate_insights
from visualization_engine import generate_visualizations
import os

datasets = [
    'sample_data/students.xlsx',
    'sample_data/sales_data.xlsx',
    'sample_data/hr_data.csv',
    'sample_data/messy_data.csv'
]

# Create a dummy class to mock uploaded_file for load_data
class DummyFile:
    def __init__(self, path):
        self.name = path
        with open(path, 'rb') as f:
            self.content = f.read()
    def read(self):
         return self.content
         
    def seek(self, pos):
         pass

for ds in datasets:
    if not os.path.exists(ds):
         print(f"Skipping {ds} (not found)")
         continue
         
    print(f"\n{'='*50}\nTesting {ds}\n{'='*50}")
    
    # Load
    if ds.endswith('.csv'):
        df = pd.read_csv(ds)
    else:
        df = pd.read_excel(ds)
        
    from utils import attempt_date_parsing
    df = attempt_date_parsing(df)
    
    profile = profile_dataset(df)
    print("Theme:", profile['theme'])
    print("Primary Metrics:", profile['primary_metrics'])
    for role, cols in profile['roles'].items():
         print(f"  {role}: {cols}")
         
    kpis = generate_kpis(df, profile)
    print("\nKPIs:")
    for kpi in kpis:
         print(f"  {kpi['label']}: {kpi['value']}")
         
    insights = generate_insights(df, profile)
    print("\nInsights:")
    for ins in insights:
         print(f"  {ins}")
         
    charts = generate_visualizations(df, profile)
    print("\nCharts Generated:")
    for chart in charts:
         print(f"  [{chart['type'].upper()}] {chart['title']} (x={chart.get('x')}, y={chart.get('y')}) | Score: {chart['score']}")
