import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="Juvenile Services Dashboard", layout="wide")

# Title and Intro
st.title("Juvenile Services Reporting & Data Integrity Dashboard")
st.markdown("""
This dashboard simulates an agency-style reporting system. It includes:
- **Program Metrics**: Enrollment trends and outcomes.
- **Data Integrity**: Automated validation checks highlighting data quality issues.
- **Statistical Analysis**: Insights from Chi-Square and Logistic Regression models.
""")

# Load Data
@st.cache_data
def load_data():
    db_path = 'juvenile_justice.db'
    if not os.path.exists(db_path):
        return None, None, None
    
    conn = sqlite3.connect(db_path)
    events = pd.read_sql("SELECT * FROM Events", conn)
    clients = pd.read_sql("SELECT * FROM Clients", conn)
    programs = pd.read_sql("SELECT * FROM Programs", conn)
    conn.close()
    
    # Pre-processing
    events['StartDate'] = pd.to_datetime(events['StartDate'])
    events['EndDate'] = pd.to_datetime(events['EndDate'])
    
    # Merge
    merged = events.merge(programs, on='ProgramID', how='left')
    merged = merged.merge(clients, on='ClientID', how='left')
    
    return events, clients, programs, merged

events_df, clients_df, programs_df, merged_df = load_data()

if events_df is None:
    st.error("Database not found. Please run the data generation and DB creation scripts first.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")
program_filter = st.sidebar.multiselect("Select Program", programs_df['ProgramName'].unique(), default=programs_df['ProgramName'].unique())
status_filter = st.sidebar.multiselect("Select Status", events_df['Status'].unique(), default=events_df['Status'].unique())

filtered_df = merged_df[merged_df['ProgramName'].isin(program_filter) & merged_df['Status'].isin(status_filter)]

# 1. KPI Cards
# ------------
st.header("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_clients = filtered_df['ClientID'].nunique()
total_enrollments = len(filtered_df)
completion_rate = len(filtered_df[filtered_df['Status'] == 'Completed']) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
avg_time_in_program = (filtered_df['EndDate'] - filtered_df['StartDate']).dt.days.mean()

col1.metric("Total Clients Served", total_clients)
col2.metric("Total Enrollments", total_enrollments)
col3.metric("Completion Rate", f"{completion_rate:.1f}%")
col4.metric("Avg Days in Program", f"{avg_time_in_program:.1f}")

# 2. Charts
# ---------
st.header("Program Analysis")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Enrollments by Program")
    prog_counts = filtered_df['ProgramName'].value_counts()
    st.bar_chart(prog_counts)

with c2:
    st.subheader("Enrollment Status Distribution")
    status_counts = filtered_df['Status'].value_counts()
    st.bar_chart(status_counts)

# Monthly Trend
st.subheader("Monthly Enrollment Trend")
events_df['Month'] = events_df['StartDate'].dt.to_period('M')
monthly_counts = events_df.groupby('Month').size()
st.line_chart(monthly_counts.astype(int)) # Streamlit handles Series index as x-axis

# 3. Data Integrity Report
# ------------------------
st.header("Data Integrity Audit")
st.markdown("Automated checks for data quality issues.")

report_path = 'docs/data_quality_report.csv'
if os.path.exists(report_path):
    report_df = pd.read_csv(report_path)
    st.dataframe(report_df, use_container_width=True)
    
    # Highlight severity
    critical_issues = report_df[report_df['Severity'] == 'Critical']
    if not critical_issues.empty:
        st.error(f"Found {len(critical_issues)} Critical Data Quality Issues!")
else:
    st.info("No Data Quality Report found. Run `scripts/check_integrity.py`.")

# 4. Statistical Analysis
# -----------------------
st.header("Statistical Analysis Results")
stats_path = 'docs/statistical_results.txt'
if os.path.exists(stats_path):
    with open(stats_path, 'r') as f:
        stats_text = f.read()
    st.text(stats_text)
else:
    st.info("No statistical results found. Run `scripts/statistical_analysis.py`.")
