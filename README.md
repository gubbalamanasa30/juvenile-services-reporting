# 📊 Texas Juvenile Justice Analytics Suite

A comprehensive data analytics dashboard designed to monitor, analyze, and forecast juvenile justice referral trends across Texas counties.

---

## 🚀 Project Overview


**Live Demo:** [Click here to view dashboard](https://juvenile-services-reporting-e8a2jhdurikekf4rafs7b6.streamlit.app/)

![Executive Dashboard Preview](data/DASH.png)



The **TJJD Analytics Suite** processes over **9 years of historical referral data (FY 2013 - 2021)** to provide actionable insights for agency administrators and policymakers. 

The system integrates:
1.  **ETL Pipeline**: Transforms raw CSV data into a star-schema SQLite database.
2.  **Data Quality Engine**: Automated audit system checking for 4 types of data integrity issues.
3.  **Interactive Dashboard**: A Streamlit-based UI for exploring trends, hotspots, and forecasts.
4.  **Predictive Modeling**: Linear regression forecasting projections through 2025.

---

## 📈 Key Insights & Results

### 1. Statewide Referral Decline
Our analysis reveals a significant and consistent downward trend in juvenile referrals:
*   **Historical Decline**: From 2013 to 2021, total statewide referrals decreased by approximately **54%**.
*   **Forecast**: The predictive model projects this trend to continue, estimating a reduction of roughly **~4,000 referrals per year** assuming current conditions persist.
*   **Driver**: A strong negative correlation between `Year` and `Total_Referrals` suggests systemic shifts in juvenile justice engagement rather than isolated anomalies.

### 2. Regional Hotspots
While the state average referral rate is declining, specific counties remain statistical outliers:
*   **High Intensity**: Counties like **Nolan** and **Kleberg** consistently show referral rates significantly above the state average per 1,000 youth.
*   **Volatility**: Certain regions exhibit high year-over-year variance, flagging them for potential resource stability reviews.

### 3. Data Integrity
The built-in audit system monitors data health:
*   **Completeness**: Tracked 100% population of critical fields.
*   **Logic**: Verified that `Offense Type` sums match `Total Referrals` for >99% of records.
*   **Uniqueness**: Ensured no duplicate County/Year records exist in the fact table.

---

## 🛠️ Dashboard Modules

| Module | Description |
| :--- | :--- |
| **Executive Dashboard** | High-level KPIs, offense severity breakdown (Violent vs. Non-Violent), and regional distribution. |
| **Risk & Hotspots** | Volatility analysis and outlier detection using population-adjusted referral rates. |
| **County Comparisons** | **[NEW]** Direct comparison of top counties by volume and intensity (Rate/1k). |
| **Forecast Model** | Linear regression projections (2022-2025) with integrated historical context. |
| **Data Quality Audit** | Transparency hub showing the results of automated data validation checks. |

---

## 💻 Tech Stack

*   **Language**: Python 3.9+
*   **Framework**: Streamlit
*   **Database**: SQLite (Star Schema)
*   **Analysis/ML**: Pandas, Scikit-Learn (Linear Regression)
*   **Visualization**: Plotly Express

---

## ⚙️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher installed.

### 1. Clone & Install
```bash
git clone <repository-url>
cd juvenile-services-reporting
pip install -r requirements.txt
```

### 2. Initialize Database
The system builds its own database from raw data.
```bash
# Create base tables
python scripts/create_db.py

# Run ETL pipeline to populate analytics tables
python scripts/etl_pipeline.py
```

### 3. Launch Dashboard
```bash
streamlit run dashboard/app_v2.py
```

---

## 🌐 Deployment (Public Link)

To make this dashboard accessible to everyone, you can deploy it for free on **Streamlit Cloud**:

1.  Push this code to your GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Click **"New app"**.
4.  Select your repository (`gubbalamanasa30/juvenile-services-reporting`).
5.  Set the **Main file path** to `dashboard/app_v2.py`.
6.  Click **Deploy**.

Once deployed, replacing the "Live Demo" link at the top of this README with your new app URL:
`https://juvenile-services-reporting-e8a2jhdurikekf4rafs7b6.streamlit.app/`

---

## 📁 Project Structure

```text
├── dashboard/
│   └── app_v2.py          # Main Streamlit application
├── data/
│   └── ...csv             # Raw data files
├── scripts/
│   ├── create_db.py       # Database schema initialization
│   ├── etl_pipeline.py    # Data extraction and transformation logic
│   ├── run_checks.py      # Data quality verification script
│   └── db_check.py        # Database connectivity test
├── docs/                  # Generated reports and analysis results
└── requirements.txt       # Project dependencies
```
