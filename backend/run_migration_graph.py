"""
Migration Script: Create Graph Tables
MDP Platform V3.1 - Graph Analysis Module

Creates sys_link_instance table for storing link instances.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection parameters."""
    import re
    pattern = r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid DATABASE_URL format: {url}")
    return {
        "user": match.group(1),
        "password": match.group(2),
        "host": match.group(3),
        "port": int(match.group(4)),
        "database": match.group(5),
    }


def run_migration():
    """Execute the graph tables migration."""
    import pymysql
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    db_params = parse_database_url(database_url)
    print(f"Connecting to {db_params['host']}:{db_params['port']}/{db_params['database']}...")
    
    connection = pymysql.connect(
        host=db_params["host"],
        port=db_params["port"],
        user=db_params["user"],
        password=db_params["password"],
        database=db_params["database"],
        charset="utf8mb4",
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if table already exists
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'sys_link_instance'
            """, (db_params["database"],))
            
            if cursor.fetchone()[0] > 0:
                print("Table sys_link_instance already exists. Migration skipped.")
                return
            
            print("Creating sys_link_instance table...")
            
            # Read and execute migration SQL
            migration_path = Path(__file__).parent / "migrations" / "create_link_instance.sql"
            
            with open(migration_path, "r", encoding="utf-8") as f:
                sql = f.read()
            
            # Split and execute statements
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("--"):
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            print(f"Warning: {e}")
            
            connection.commit()
            print("Migration completed successfully!")
            
            # Verify
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'sys_link_instance'
                ORDER BY ORDINAL_POSITION
            """, (db_params["database"],))
            
            print("\nTable structure:")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]}")
                
    finally:
        connection.close()


if __name__ == "__main__":
    run_migration()
