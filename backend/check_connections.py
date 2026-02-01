import sys
sys.path.insert(0, '.')
from app.core.db import engine
from sqlmodel import Session, text

def check_connections():
    with Session(engine) as session:
        print("--- Checking Connections ---")
        connections = session.exec(text("SELECT id, name, conn_type FROM sys_connection")).all()
        for conn in connections:
            print(conn)

if __name__ == "__main__":
    check_connections()
