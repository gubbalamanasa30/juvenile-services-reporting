import sqlite3
import pandas as pd
import os
import traceback

def create_database():
    print("Creating SQLite database (DEBUG VERSION)...")
    
    db_path = 'juvenile_justice.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create Tables
        cursor.execute("CREATE TABLE Programs (ProgramID TEXT PRIMARY KEY, ProgramName TEXT, ProgramType TEXT, Capacity INTEGER)")
        cursor.execute("CREATE TABLE Clients (ClientID TEXT, LastName TEXT, FirstName TEXT, Gender TEXT, Race TEXT, DOB TEXT)")
        cursor.execute("CREATE TABLE Events (EventID TEXT PRIMARY KEY, ClientID TEXT, ProgramID TEXT, StartDate TEXT, Status TEXT, EndDate TEXT)")
        
        print("Tables created.")
        
        data_dir = 'data'
        
        # Programs
        try:
            programs_df = pd.read_csv(os.path.join(data_dir, 'programs.csv'))
            programs_df.to_sql('Programs', conn, if_exists='append', index=False)
            print(f"Programs: Imported {len(programs_df)}")
        except Exception as e:
            print(f"FAILED to import Programs: {e}")
            traceback.print_exc()

        # Clients
        try:
            clients_df = pd.read_csv(os.path.join(data_dir, 'clients.csv'))
            clients_df.to_sql('Clients', conn, if_exists='append', index=False)
            print(f"Clients: Imported {len(clients_df)}")
        except Exception as e:
            print(f"FAILED to import Clients: {e}")
            traceback.print_exc()

        # Events
        try:
            events_df = pd.read_csv(os.path.join(data_dir, 'events.csv'))
            # Force EndDate to string to avoid mixed type issues if any, or NaN issues?
            # Pandas handles NaNs as NULLs in SQL usually.
            events_df.to_sql('Events', conn, if_exists='append', index=False)
            print(f"Events: Imported {len(events_df)}")
        except Exception as e:
            print(f"FAILED to import Events: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        conn.commit()
        conn.close()
        print(f"Database closed. Path: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    create_database()
