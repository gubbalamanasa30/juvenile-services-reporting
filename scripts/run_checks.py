import pandas as pd
import sqlite3
import os

def run_checks():
    print("Running Data Integrity Checks...")
    
    conn = sqlite3.connect('juvenile_justice.db')
    
    # Load Fact Table with Dimensions
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
    
    issues = []
    
    # 1. Completeness Check
    # ---------------------
    if df['Total_Referrals'].isnull().any():
        count = df['Total_Referrals'].isnull().sum()
        issues.append({
            'Category': 'Completeness',
            'Rule': 'Total_Referrals must not be NULL',
            'Failed_Rows': count,
            'Severity': 'Critical',
            'Details': f"{count} rows have missing referral counts."
        })

    # 2. Uniqueness Check
    # -------------------
    duplicates = df.duplicated(subset=['CountyID', 'YearID'])
    if duplicates.any():
        count = duplicates.sum()
        issues.append({
            'Category': 'Uniqueness',
            'Rule': 'County + Year must be unique',
            'Failed_Rows': count,
            'Severity': 'Critical',
            'Details': f"Found {count} duplicate records for County/Year combinations."
        })

    # 3. Logic: Math Consistency
    # --------------------------
    # Does sum of offenses match total?
    # Note: Dataset says "Status" and "Other CINS" are separate. 
    # Formula: Violent + Other_Felony + Misd + VOP + Status_Offense + CINS == Total?
    # Let's verify if this holds true.
    
    df['Calc_Total'] = (
        df['Violent_Felony'] + 
        df['Other_Felony'] + 
        df['Misd'] + 
        df['VOP'] + 
        df['Status_Offense'] + 
        df['CINS']
    )
    
    math_mismatch = df[df['Calc_Total'] != df['Total_Referrals']]
    if not math_mismatch.empty:
        count = len(math_mismatch)
        # In real datasets, there's often a small "Other" category missing or data entry errors.
        issues.append({
            'Category': 'Logic',
            'Rule': 'Sum of Offenses == Total Referrals',
            'Failed_Rows': count,
            'Severity': 'Medium',
            'Details': f"{count} rows have mismatch between offense sum and Total Referrals. (Potential data entry error)"
        })
        
    # 4. Logic: Unique Youth
    # ----------------------
    # Unique Youth Referred cannot be > Total Referrals
    youth_logic_fail = df[df['Unique_Youth'] > df['Total_Referrals']]
    if not youth_logic_fail.empty:
        count = len(youth_logic_fail)
        issues.append({
            'Category': 'Logic',
            'Rule': 'Unique Youth <= Total Referrals',
            'Failed_Rows': count,
            'Severity': 'High',
            'Details': f"{count} rows have more Unique Youth than Referrals (impossible)."
        })

    # 5. Outliers: YoY Change
    # -----------------------
    # Sort by County and Year
    df.sort_values(['County', 'Year'], inplace=True)
    df['Prev_Year_Ref'] = df.groupby('County')['Total_Referrals'].shift(1)
    
    # Calculate % Change
    # Avoid division by zero
    df['YoY_Change_Pct'] = ((df['Total_Referrals'] - df['Prev_Year_Ref']) / df['Prev_Year_Ref']).fillna(0)
    
    # Flag > 50% change (arbitrary threshold for "investigate")
    # Only consider significant volume (e.g., > 10 referrals) to avoid noise from small counties going 1 -> 2 (100%)
    outliers = df[(abs(df['YoY_Change_Pct']) > 0.5) & (df['Prev_Year_Ref'] > 10)]
    
    if not outliers.empty:
        count = len(outliers)
        issues.append({
            'Category': 'Outlier',
            'Rule': 'YoY Change > 50%',
            'Failed_Rows': count,
            'Severity': 'Low',
            'Details': f"{count} county-years show >50% change in volume vs previous year."
        })

    # Save Report
    output_dir = 'docs'
    os.makedirs(output_dir, exist_ok=True)
    
    report_df = pd.DataFrame(issues)
    if not report_df.empty:
        report_df.to_csv(os.path.join(output_dir, 'data_quality_report.csv'), index=False)
        print("Issues Found:")
        print(report_df.to_string())
    else:
        # Create empty report with headers to avoid errors
        pd.DataFrame(columns=['Category','Rule','Failed_Rows','Severity','Details']).to_csv(os.path.join(output_dir, 'data_quality_report.csv'), index=False)
        print("No Data Quality Issues Found!")
        
    print(f"\nReport saved to {output_dir}/data_quality_report.csv")

if __name__ == "__main__":
    run_checks()
