# AutoViz – Automatic Excel Analytics & Dashboard Generator

## Problem Statement
Many students and professionals need to quickly visualize datasets, but manually setting up dashboards and selecting the right charts requires significant time and data visualization expertise. 

## Objective
AutoViz is a Data Analytics and Visualization Lab mini-project that automates this process. You simply upload a dataset (Excel/CSV), and the application automatically profiles the data, calculates Key Performance Indicators (KPIs), generates text insights, and renders an interactive dashboard with the most appropriate charts—all without requiring any manual configuration.

## Features
- **Upload Support:** Works with `.csv`, `.xls`, and `.xlsx` files.
- **Automatic Data Profiling:** Automatically detects numerical, categorical, and identifier columns.
- **Dynamic KPIs:** Extracts and calculates key metrics automatically (e.g., Average CGPA, Highest Package).
- **Key Insights:** Generates text-based statistical insights based on your data.
- **Rule-Based Visualization Engine:** Intelligently recommends and renders interactive Plotly charts based on column types and names.
- **Data Preview:** View the raw dataset directly in the dashboard.

## Technologies Used
- **Python:** Core programming language.
- **Pandas:** For data processing and analysis.
- **OpenPyXL:** For reading Excel files.
- **Plotly:** For interactive data visualization.
- **Streamlit:** For the web interface.

## System Workflow
1. **Excel/CSV Upload:** User uploads the dataset.
2. **Data Cleaning & Type Detection:** The system parses columns and identifies datatypes.
3. **Statistical Analysis:** Calculates aggregations and metrics for KPIs.
4. **Visualization Recommendation:** The Rule-based engine decides which charts are useful.
5. **Automatic Chart Generation:** Plotly charts are dynamically generated.
6. **Interactive Dashboard:** The Streamlit dashboard is displayed to the user.

## How the Visualization Recommendation Engine Works
The core of AutoViz is its rule-based engine that examines detected columns and automatically decides which visualizations are useful. It follows these rules:

1. **Numerical column:** Generates a Distribution/Histogram to show the spread of data (e.g., CGPA Distribution).
2. **Categorical + Numerical column:** Generates a Bar Chart showing an aggregate (e.g., Average CGPA by Branch).
3. **Categorical column (small unique count):** Generates a Pie/Donut Chart (e.g., Gender distribution, Placement Status).
4. **Two Numerical columns:** Generates a Scatter Plot to show correlation (e.g., Attendance vs. CGPA).
5. **Multiple related numerical columns:** Generates a Bar Chart to compare them (e.g., Subject-wise Average Marks).

The engine also intentionally ignores identifier columns (like Student_ID or Roll_Number) as they don't provide meaningful analytical dimensions.

## Installation & Setup

1. **Clone or Download the Repository**
2. **Install Requirements:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Sample Input / Expected Output
A sample dataset `sample_data/students.xlsx` is provided in the repository.
- **Input:** Upload `students.xlsx`.
- **Output:** The app will detect columns like `Branch`, `CGPA`, `Attendance`, and `Maths`, generate KPIs (like Average CGPA), print insights, and display 4-6 interactive Plotly charts comparing subjects, branches, and distributions.

## Future Scope
- Support for more advanced machine learning based insights.
- Ability to export the generated dashboard as a PDF report.
- More chart types (like Box plots, Heatmaps).
