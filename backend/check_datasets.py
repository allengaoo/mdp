import sys
sys.path.insert(0, '.')
from app.core.db import engine
from sqlmodel import Session, text

def check_datasets():
    with Session(engine) as s:
        print("--- Checking sys_dataset ---")
        try:
            r = s.exec(text("SELECT * FROM sys_dataset"))
            rows = r.fetchall()
            print(f"Found {len(rows)} datasets:")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error querying sys_dataset: {e}")

        print("\n--- Checking sys_datasource_table (View or Table) ---")
        try:
            r = s.exec(text("SELECT * FROM sys_datasource_table"))
            rows = r.fetchall()
            print(f"Found {len(rows)} datasource tables:")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error querying sys_datasource_table: {e}")

if __name__ == "__main__":
    check_datasets()
