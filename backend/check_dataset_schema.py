import sys
sys.path.insert(0, '.')
from app.core.db import engine
from sqlmodel import Session, text

def check_dataset_schema():
    with Session(engine) as s:
        print("--- Checking sys_dataset columns ---")
        try:
            r = s.exec(text("DESCRIBE sys_dataset"))
            rows = r.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error describing sys_dataset: {e}")

if __name__ == "__main__":
    check_dataset_schema()
