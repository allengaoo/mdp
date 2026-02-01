import sys
sys.path.insert(0, '.')
from app.core.db import engine
from sqlmodel import Session, text

def check_view_def():
    with Session(engine) as s:
        print("--- Checking sys_datasource_table definition ---")
        try:
            r = s.exec(text("SHOW CREATE VIEW sys_datasource_table"))
            row = r.first()
            print(row)
        except Exception as e:
            print(f"Error showing create view: {e}")

if __name__ == "__main__":
    check_view_def()
