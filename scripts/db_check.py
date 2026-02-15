import sqlite3
import pandas as pd
import os

db_path = 'juvenile_justice.db'
if not os.path.exists(db_path):
    print("DB file not found.")
    exit()

conn = sqlite3.connect(db_path)
tables = ['Programs', 'Clients', 'Events']

print(f"Checking DB: {db_path}", flush=True)

for t in tables:
    try:
        df = pd.read_sql(f"SELECT * FROM {t}", conn)
        print(f"Table '{t}': {len(df)} rows", flush=True)
        if len(df) > 0:
            print(f"  Columns: {list(df.columns)}", flush=True)
            print(f"  Sample: {df.iloc[0].to_dict()}", flush=True)
    except Exception as e:
        print(f"Error reading {t}: {e}", flush=True)

conn.close()
