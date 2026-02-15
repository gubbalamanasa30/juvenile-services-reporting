import pandas as pd
import sqlite3
import os

def etl_process():
    print("Starting ETL Pipeline...")
    
    # 1. Extract
    print("Extracting data...")
    raw_referrals = pd.read_csv('TJJD_-_County_Level_Referral_Data__FY_2013-2021.csv')
    
    # Check if metadata exists, if not, generate it on the fly (handling the race condition from previous step)
    if not os.path.exists('data/County_Metadata.csv'):
        print("Metadata file not found, generating...")
        import generate_metadata
        generate_metadata.generate_metadata()
        
    county_meta = pd.read_csv('data/County_Metadata.csv')
    
    # 2. Transform
    print("Transforming data...")
    
    # Clean Column Names
    # "Calendar Year","County","Juvenile Population","Violent Felony","Other Felony","Misd.","VOP","Status","Other CINS","Referrals","Referral Rate/1,000","Youth Referred"
    raw_referrals.columns = [
        'Year', 'County', 'Juv_Pop', 'Violent_Felony', 'Other_Felony', 
        'Misd', 'VOP', 'Status_Offense', 'CINS', 'Total_Referrals', 
        'Referral_Rate', 'Unique_Youth'
    ]
    
    # Create Dim_Time
    dim_time = pd.DataFrame({'Year': raw_referrals['Year'].unique()})
    dim_time = dim_time.sort_values('Year').reset_index(drop=True)
    dim_time['YearID'] = dim_time.index + 1
    
    # Create Dim_County
    # Merge with metadata to get Region
    dim_county = raw_referrals[['County']].drop_duplicates().sort_values('County').reset_index(drop=True)
    dim_county = dim_county.merge(county_meta, on='County', how='left')
    dim_county['Region'] = dim_county['Region'].fillna('Unknown') # Handle missing regions
    dim_county['CountyID'] = dim_county.index + 1
    
    # Join Keys back to Fact Table
    fact_table = raw_referrals.merge(dim_time, on='Year', how='left')
    fact_table = fact_table.merge(dim_county, on='County', how='left')
    
    # Select final Fact columns
    fact_referrals = fact_table[[
        'CountyID', 'YearID', 'Juv_Pop', 
        'Violent_Felony', 'Other_Felony', 'Misd', 'VOP', 'Status_Offense', 'CINS',
        'Total_Referrals', 'Referral_Rate', 'Unique_Youth'
    ]]
    
    # 3. Load
    print("Loading into SQLite...")
    db_path = 'juvenile_justice.db'
    # if os.path.exists(db_path):
    #     os.remove(db_path) # Full refresh - COMMENTED OUT TO PRESERVE EXISTING TABLES
        
    conn = sqlite3.connect(db_path)
    
    dim_time.to_sql('Dim_Time', conn, if_exists='replace', index=False)
    dim_county.to_sql('Dim_County', conn, if_exists='replace', index=False)
    fact_referrals.to_sql('Fact_Referrals', conn, if_exists='replace', index=False)
    
    # Create Indexes for performance (overkill for this size, but good practice)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_fact_county ON Fact_Referrals(CountyID)")
    cursor.execute("CREATE INDEX idx_fact_year ON Fact_Referrals(YearID)")
    
    conn.commit()
    conn.close()
    
    print(f"ETL Complete. Database created at {db_path}")
    print(f"Loaded {len(fact_referrals)} facts, {len(dim_county)} counties, {len(dim_time)} years.")

if __name__ == "__main__":
    etl_process()
