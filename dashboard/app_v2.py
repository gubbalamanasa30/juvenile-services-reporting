import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression

# Page Config
st.set_page_config(
    page_title="TJJD Analytics Suite", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Professional" Look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    div.stMetric {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Data Loading
# --------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect('juvenile_justice.db')
    query = """
    SELECT 
        f.*, 
        c.County, c.Region,
        t.Year
    FROM Fact_Referrals f
    JOIN Dim_County c ON f.CountyID = c.CountyID
    JOIN Dim_Time t ON f.YearID = t.YearID
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def load_dq_report():
    try:
        return pd.read_csv('docs/data_quality_report.csv')
    except:
        return pd.DataFrame()

df = load_data()
dq_df = load_dq_report()

# --------------------------
# Sidebar Controls
# --------------------------
st.sidebar.title("⚖️ Agency Analytics")
page = st.sidebar.radio("Module", ["Executive Dashboard", "Risk & Hotspots", "Data Quality Audit", "Forecast Model", "County Comparisons"])

st.sidebar.markdown("---")
st.sidebar.info(f"**Data Source:** Texas Juvenile Justice Dept.\n\n**Range:** FY 2013 - {df['Year'].max()}\n\n**Records:** {len(df):,}")

# --------------------------
# Page 1: Executive Dashboard
# --------------------------
if page == "Executive Dashboard":
    st.title("📊 Executive Dashboard: State of Juvenile Justice")
    st.markdown("High-level overview of referral trends, offense severity, and regional performance.")
    
    # KPIs
    # Latest Year vs Previous
    latest_year = df['Year'].max()
    curr_df = df[df['Year'] == latest_year]
    prev_df = df[df['Year'] == (latest_year - 1)]
    
    col1, col2, col3, col4 = st.columns(4)
    
    curr_vol = curr_df['Total_Referrals'].sum()
    prev_vol = prev_df['Total_Referrals'].sum()
    vol_delta = calc_delta = ((curr_vol - prev_vol) / prev_vol) * 100
    
    curr_rate = curr_df['Referral_Rate'].mean()
    prev_rate = prev_df['Referral_Rate'].mean()
    rate_delta = ((curr_rate - prev_rate) / prev_rate) * 100
    
    violent_share = (curr_df['Violent_Felony'].sum() / curr_vol) * 100
    prev_violent_share = (prev_df['Violent_Felony'].sum() / prev_vol) * 100
    violent_delta = violent_share - prev_violent_share
    
    col1.metric("Total Referrals (FY21)", f"{curr_vol:,.0f}", f"{vol_delta:.1f}%", delta_color="inverse")
    col2.metric("Avg Referral Rate (per 1k)", f"{curr_rate:.2f}", f"{rate_delta:.1f}%", delta_color="inverse")
    col3.metric("Violent Felony Share", f"{violent_share:.1f}%", f"{violent_delta:.1f} pts", delta_color="inverse")
    col4.metric("Unique Youth Served", f"{curr_df['Unique_Youth'].sum():,.0f}", "Active Population")
    
    st.markdown("---")
    
    # Row 2: Trends and Composition
    c1, c2 = st.columns((2, 1))
    
    with c1:
        st.subheader("Offense Severity Evolution")
        # Pre-aggregate by year and type
        trend_agg = df.groupby('Year')[['Violent_Felony', 'Other_Felony', 'Misd', 'VOP', 'Status_Offense']].sum().reset_index()
        # melt for stacked area
        trend_melt = trend_agg.melt(id_vars='Year', var_name='Offense Type', value_name='Count')
        
        fig_area = px.area(trend_melt, x='Year', y='Count', color='Offense Type',
                           color_discrete_sequence=px.colors.qualitative.Safe,
                           title="Volume by Offense Category (Stacked)")
        fig_area.update_layout(xaxis=dict(tickmode='linear'), hovermode="x unified")
        st.plotly_chart(fig_area, use_container_width=True)
        
    with c2:
        st.subheader("Regional Distribution")
        reg_agg = curr_df.groupby('Region')['Total_Referrals'].sum().reset_index()
        fig_pie = px.pie(reg_agg, values='Total_Referrals', names='Region', hole=0.4,
                           title=f"Referrals by Region (FY {latest_year})")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 3: County Leaderboard
    st.subheader(f"Top 10 Counties by Volume (FY {latest_year})")
    top_counties = curr_df.nlargest(10, 'Total_Referrals')
    fig_bar = px.bar(top_counties, x='County', y='Total_Referrals', color='Referral_Rate',
                     color_continuous_scale='Reds',
                     text='Total_Referrals',
                     labels={'Referral_Rate': 'Rate/1k'},
                     title="Volume vs Intensity (Color)")
    fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------
# Page 2: Risk & Hotspots
# --------------------------
elif page == "Risk & Hotspots":
    st.title("🚨 Strategic Risk Analysis")
    st.markdown("Identify counties that are statistically anomalous or trending negatively.")
    
    # 1. Bubble Chart: volume vs Rate vs Population
    st.subheader("Outlier Detection: Volume vs. Intensity")
    year_select = st.select_slider("Select Year", options=sorted(df['Year'].unique()))
    
    bubble_df = df[df['Year'] == year_select].copy()
    # Log scale for pop to make it readable
    
    fig_scatter = px.scatter(bubble_df, x="Juv_Pop", y="Referral_Rate",
                             size="Total_Referrals", color="Region",
                             hover_name="County", log_x=True,
                             size_max=60, template="plotly_white",
                             title=f"Referral Rate vs. Population Size ({year_select})")
    
    # Add reference lines
    avg_rate_yr = bubble_df['Referral_Rate'].mean()
    fig_scatter.add_hline(y=avg_rate_yr, line_dash="dash", annotation_text="State Avg Rate")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 2. Volatility Analysis
    st.subheader("High Volatility Counties")
    st.markdown("Counties with the most drastic year-over-year changes (Potential Stability Issues).")
    
    # Calculate volatility (Std Dev of % Change)
    # We already have YoY change in the ETL/Validation logic, let's re-derive simply
    pivot = df.pivot(index='County', columns='Year', values='Total_Referrals')
    pct_change = pivot.pct_change(axis=1)
    volatility = pct_change.std(axis=1).reset_index()
    volatility.columns = ['County', 'Volatility_Score']
    
    top_volatile = volatility.nlargest(10, 'Volatility_Score')
    
    # Join back to get Region
    top_volatile = top_volatile.merge(df[['County', 'Region']].drop_duplicates(), on='County')
    
    fig_vol = px.bar(top_volatile, x='Volatility_Score', y='County', orientation='h', color='Region',
                     title="Top 10 Most Volatile Counties (Std Dev of YoY Change)")
    st.plotly_chart(fig_vol, use_container_width=True)

# --------------------------
# Page 3: Data Quality Audit
# --------------------------
elif page == "Data Quality Audit":
    st.title("🛡️ Data Integrity Hub")
    
    # Summary Cards
    col1, col2, col3 = st.columns(3)
    
    total_checks = 4 # Completeness, Uniqueness, Logic, Outliers
    failed_rows = dq_df['Failed_Rows'].sum() if not dq_df.empty else 0
    risk_score = 100 - min(100, (failed_rows / 100)) # Arbitrary gaming score
    
    col1.metric("Health Score", f"{risk_score:.0f}/100")
    col2.metric("Total Issues Found", f"{failed_rows}")
    col3.metric("Critical Failures", f"{len(dq_df[dq_df['Severity']=='Critical']) if not dq_df.empty else 0}")
    
    st.markdown("### Audit Report")
    if not dq_df.empty:
        st.dataframe(dq_df.style.applymap(lambda v: 'color: red;' if v == 'Critical' else None, subset=['Severity']), use_container_width=True)
    else:
        st.success("No issues found in the latest audit run.")
        
    # Deep dive into "Logic"
    with st.expander("Inspection Tool: Math Mismatches"):
        # Re-calc
        df['Calc_Total'] = (df['Violent_Felony'] + df['Other_Felony'] + df['Misd'] + df['VOP'] + df['Status_Offense'] + df['CINS'])
        mismatches = df[df['Calc_Total'] != df['Total_Referrals']]
        
        if not mismatches.empty:
            st.warning(f"{len(mismatches)} rows have discrepancies between Total Referrals and Offense Sum.")
            st.dataframe(mismatches[['Year', 'County', 'Total_Referrals', 'Calc_Total', 'Violent_Felony', 'Misd']])
        else:
            st.success("✅ All rows passed Summation Logic Check.")

# --------------------------
# Page 4: Forecast Model
# --------------------------
elif page == "Forecast Model":
    st.title("🔮 Predictive Modeling")
    st.markdown("Simple Linear Projection of Statewide Referrals.")
    
    # Aggregate to State Level
    state_df = df.groupby('Year')['Total_Referrals'].sum().reset_index()
    
    # Model
    X = state_df[['Year']]
    y = state_df['Total_Referrals']
    model = LinearRegression()
    model.fit(X, y)
    
    # Future Years
    future_years = np.array([2022, 2023, 2024, 2025]).reshape(-1, 1)
    predictions = model.predict(future_years)
    
    future_df = pd.DataFrame({'Year': future_years.flatten(), 'Total_Referrals': predictions, 'Type': 'Forecast'})
    
    # --- FIX: Connect the lines ---
    # Append the last historical point to the start of the Forecast dataframe
    last_hist_year = state_df['Year'].max()
    last_hist_val = state_df.loc[state_df['Year'] == last_hist_year, 'Total_Referrals'].values[0]
    
    # Create a bridge row
    bridge_row = pd.DataFrame({'Year': [last_hist_year], 'Total_Referrals': [last_hist_val], 'Type': 'Forecast'})
    
    # Combine: Bridge -> Forecast
    future_df = pd.concat([bridge_row, future_df], ignore_index=True)
    # ------------------------------

    state_df['Type'] = 'Historical'
    
    combined = pd.concat([state_df, future_df])
    
    fig_proj = px.line(combined, x='Year', y='Total_Referrals', color='Type', 
                       markers=True, line_dash='Type',
                       title="Statewide Referral Volume Forecast (2013-2025)")
    fig_proj.update_layout(showlegend=True)
    st.plotly_chart(fig_proj, use_container_width=True)
    
    st.info(f"**Model Insight:** The model projects a continued trend of roughly {model.coef_[0]:.0f} fewer referrals per year statewide.")

    st.markdown("### 📉 Why is the forecast trending down?")
    with st.expander("Show Model explanation"):
        st.write("""
        The forecast is based on a **linear regression** of historical data from 2013 to 2021. 
        The specific factors driving this decrease according to the model are:
        """)
        
        # Calculate simple stats for explanation
        start_vol = state_df.iloc[0]['Total_Referrals']
        end_vol = state_df[state_df['Type']=='Historical'].iloc[-1]['Total_Referrals']
        pct_drop = ((end_vol - start_vol) / start_vol) * 100
        
        st.metric("Historical Decline (2013-2021)", f"{pct_drop:.1f}%", delta_color="inverse")
        
        st.write(f"""
        - **Consistent Historical Decline:** From 2013 to 2021, the total referrals dropped by **{abs(pct_drop):.1f}%**.
        - **Negative Correlation:** There is a strong negative correlation between `Year` and `Referrals`. As time goes on, volume consistently decreases.
        - **Model Logic:** The linear model detects this downward slope (`{model.coef_[0]:.1f}` per year) and projects it forward.
        """)
        
        st.warning("Note: This simple model assumes past trends will continue indefinitely and does not account for external factors like policy changes or population growth.")


# --------------------------
# Page 5: County Comparisons
# --------------------------
elif page == "County Comparisons":
    st.title("County Comparisons")
    st.markdown("### 1. Top Counties by Referral Rate")
    
    # Year Selection
    years = sorted(df['Year'].unique(), reverse=True)
    selected_year = st.selectbox("Select Year for Ranking", years)
    
    # Filter Data
    ranked_df = df[df['Year'] == selected_year].nlargest(10, 'Referral_Rate')
    
    # Create Bar Chart
    fig = px.bar(
        ranked_df,
        x='County',
        y='Referral_Rate',
        color='Referral_Rate',
        color_continuous_scale='Reds',
        title=f"Top 10 Counties by Referral Rate ({selected_year})",
        labels={'Referral_Rate': 'Rate per 1,000'},
        text='Referral_Rate'
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(xaxis_title="County", yaxis_title="Rate per 1,000")
    
    st.plotly_chart(fig, use_container_width=True)


