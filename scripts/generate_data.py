import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_data():
    print("Generating synthetic data...")
    
    # 1. Programs Data
    # ----------------
    programs_data = {
        'ProgramID': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'ProgramName': ['Aggression Replacement Training', 'Functional Family Therapy', 'Mentoring 101', 'Substance Abuse Education', 'Vocational Skills'],
        'ProgramType': ['CBT', 'Family Therapy', 'Mentoring', 'Education', 'Vocational'],
        'Capacity': [20, 15, 50, 30, 25]
    }
    df_programs = pd.DataFrame(programs_data)
    
    # 2. Clients Data
    # ---------------
    # Generate 500 clients
    n_clients = 500
    client_ids = [f'C{str(i).zfill(5)}' for i in range(1, n_clients + 1)]
    
    # Intentional Flaw: Duplicate Client IDs (approx 5 duplicates)
    client_ids_flawed = client_ids.copy()
    for _ in range(5):
        client_ids_flawed.append(random.choice(client_ids[:50])) # Add duplicates
    
    n_total_clients = len(client_ids_flawed)
    
    genders = ['M', 'F', 'M', 'M', 'F'] # Slight male bias common in JJ data
    races = ['White', 'Black', 'Hispanic', 'Asian', 'Other']
    
    clients_data = {
        'ClientID': client_ids_flawed,
        'LastName': [f"Last{i}" for i in range(n_total_clients)],
        'FirstName': [f"First{i}" for i in range(n_total_clients)],
        'Gender': [random.choice(genders) for _ in range(n_total_clients)],
        'Race': [random.choice(races) for _ in range(n_total_clients)],
        'DOB': [datetime(2005, 1, 1) + timedelta(days=random.randint(0, 365*6)) for _ in range(n_total_clients)] # Ages ~15-21 roughly
    }
    
    df_clients = pd.DataFrame(clients_data)
    
    # Intentional Flaw: Missing DOBs (approx 10 missing)
    df_clients.loc[np.random.choice(df_clients.index, 10, replace=False), 'DOB'] = pd.NaT
    
    # 3. Events / Enrollments Data
    # ----------------------------
    # Generate 800 events
    n_events = 800
    event_ids = [f'E{str(i).zfill(6)}' for i in range(1, n_events + 1)]
    
    events_data = {
        'EventID': event_ids,
        'ClientID': [random.choice(client_ids) for _ in range(n_events)], # Valid client IDs initially
        'ProgramID': [random.choice(programs_data['ProgramID']) for _ in range(n_events)],
        'StartDate': [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365)) for _ in range(n_events)],
        'Status': [random.choice(['Completed', 'Active', 'Dropped', 'Transferred']) for _ in range(n_events)]
    }
    
    df_events = pd.DataFrame(events_data)
    
    # Add EndDate based on StartDate and Status
    end_dates = []
    for idx, row in df_events.iterrows():
        if row['Status'] == 'Active':
            end_dates.append(pd.NaT)
        else:
            days_in = random.randint(1, 180)
            end_dates.append(row['StartDate'] + timedelta(days=days_in))
    
    df_events['EndDate'] = end_dates

    # Intentional Flaw: EndDate before StartDate (approx 5 records)
    flawed_indices = np.random.choice(df_events[df_events['Status'] != 'Active'].index, 5, replace=False)
    for idx in flawed_indices:
        df_events.at[idx, 'EndDate'] = df_events.at[idx, 'StartDate'] - timedelta(days=random.randint(1, 10))

    # Intentional Flaw: Events with ClientIDs that don't exist in Clients table (Orphaned events)
    orphan_indices = np.random.choice(df_events.index, 10, replace=False)
    for idx in orphan_indices:
        df_events.at[idx, 'ClientID'] = f"C9999{random.randint(0,9)}"

    # Intentional Flaw: Invalid ProgramIDs
    invalid_program_indices = np.random.choice(df_events.index, 5, replace=False)
    for idx in invalid_program_indices:
        df_events.at[idx, 'ProgramID'] = "P999"

    # Save to CSV
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    df_programs.to_csv(os.path.join(output_dir, 'programs.csv'), index=False)
    df_clients.to_csv(os.path.join(output_dir, 'clients.csv'), index=False)
    df_events.to_csv(os.path.join(output_dir, 'events.csv'), index=False)

    print(f"Data generation complete. Files saved to {output_dir}/")
    print(f"  - programs.csv: {len(df_programs)} records")
    print(f"  - clients.csv: {len(df_clients)} records (with duplicates and missing DOBs)")
    print(f"  - events.csv: {len(df_events)} records (with date logic errors and orphan records)")

if __name__ == "__main__":
    generate_data()
