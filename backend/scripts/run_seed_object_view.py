"""
Run Object 360 View Configuration Seed Script
MDP Platform V3.1
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")


def run_seed():
    """Execute the seed SQL script."""
    # Database connection parameters
    db_config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "Ga0binGB"),
        "database": os.getenv("MYSQL_DATABASE", "ontology_meta_new"),
        "charset": "utf8mb4",
    }
    
    print(f"Connecting to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # Read SQL file
    sql_file = Path(__file__).parent / "seed_object_view_config.sql"
    if not sql_file.exists():
        print(f"Error: SQL file not found: {sql_file}")
        return False
    
    sql_content = sql_file.read_text(encoding="utf-8")
    
    # Split into individual statements (simple split, ignoring comments)
    statements = []
    current_statement = []
    
    for line in sql_content.split("\n"):
        stripped = line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith("--"):
            continue
        current_statement.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current_statement))
            current_statement = []
    
    # Connect and execute
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, stmt in enumerate(statements):
            if stmt.strip():
                try:
                    cursor.execute(stmt)
                    if stmt.strip().upper().startswith("SELECT"):
                        rows = cursor.fetchall()
                        if rows:
                            print(f"  Query result: {len(rows)} rows")
                            for row in rows:
                                print(f"    {row}")
                except pymysql.Error as e:
                    print(f"  Warning: Statement {i+1} failed: {e}")
        
        conn.commit()
        print("\nSeed data inserted successfully!")
        
        # Verify data
        print("\n=== Verification ===")
        
        cursor.execute("SELECT COUNT(*) FROM app_definition WHERE id = 'app-target-360'")
        count = cursor.fetchone()[0]
        print(f"App Definition: {count} record(s)")
        
        cursor.execute("SELECT COUNT(*) FROM app_module WHERE app_id = 'app-target-360'")
        count = cursor.fetchone()[0]
        print(f"App Modules: {count} record(s)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM app_widget w
            JOIN app_module m ON w.module_id = m.id
            WHERE m.app_id = 'app-target-360'
        """)
        count = cursor.fetchone()[0]
        print(f"App Widgets: {count} record(s)")
        
        cursor.close()
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        return False


if __name__ == "__main__":
    success = run_seed()
    sys.exit(0 if success else 1)
