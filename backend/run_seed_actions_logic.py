"""
Run seed_actions_logic.sql to populate Actions and Functions for Maritime scenario.
"""
import os
import re
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection config."""
    # Format: mysql+pymysql://user:password@host:port/database
    pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, url)
    if match:
        return {
            "user": match.group(1),
            "password": match.group(2),
            "host": match.group(3),
            "port": int(match.group(4)),
            "database": match.group(5),
            "charset": "utf8mb4",
        }
    raise ValueError(f"Invalid DATABASE_URL format: {url}")

# Database configuration
database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/ontology_meta_new")
DB_CONFIG = parse_database_url(database_url)


def run_seed():
    """Execute the seed SQL file."""
    sql_file = os.path.join(os.path.dirname(__file__), "seed_actions_logic.sql")
    
    if not os.path.exists(sql_file):
        print(f"ERROR: SQL file not found: {sql_file}")
        return False
    
    print("=" * 60)
    print("Seed Actions & Logic Data")
    print("=" * 60)
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"SQL File: {sql_file}")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n[Step 1] Connecting to database...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("  [OK] Connected successfully")
        
        # Read SQL file
        print("\n[Step 2] Reading SQL file...")
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
        print(f"  [OK] Read {len(sql_content)} characters")
        
        # Split into statements (handle multi-line statements)
        print("\n[Step 3] Executing SQL statements...")
        statements = []
        current_stmt = []
        
        for line in sql_content.split('\n'):
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue
            
            current_stmt.append(line)
            
            # Check if statement ends with semicolon (not inside string)
            if stripped.endswith(';'):
                statements.append('\n'.join(current_stmt))
                current_stmt = []
        
        # Execute each statement
        success_count = 0
        error_count = 0
        
        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
                conn.commit()
                
                # Determine statement type
                stmt_type = stmt.strip().split()[0].upper() if stmt.strip() else "UNKNOWN"
                if "meta_function_def" in stmt:
                    print(f"  [{i}] INSERT Function: OK")
                elif "meta_action_def" in stmt:
                    print(f"  [{i}] INSERT Action: OK")
                else:
                    print(f"  [{i}] {stmt_type}: OK")
                    
                success_count += 1
            except Exception as e:
                error_msg = str(e)
                if "Duplicate entry" in error_msg:
                    print(f"  [{i}] Skipped (already exists)")
                    success_count += 1
                else:
                    print(f"  [{i}] ERROR: {error_msg[:100]}")
                    error_count += 1
        
        print(f"\n  Executed: {success_count} successful, {error_count} failed")
        
        # Verify data
        print("\n[Step 4] Verifying data...")
        
        cursor.execute("SELECT COUNT(*) FROM meta_function_def")
        func_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM meta_action_def")
        action_count = cursor.fetchone()[0]
        
        print(f"  Functions in DB: {func_count}")
        print(f"  Actions in DB: {action_count}")
        
        # Show seeded data
        print("\n[Step 5] Seeded Actions & Functions:")
        cursor.execute("""
            SELECT 
                a.id, a.api_name as action_name, a.display_name,
                f.api_name as function_name
            FROM meta_action_def a
            LEFT JOIN meta_function_def f ON a.backing_function_id = f.id
            WHERE a.id IN ('act_intel_verify_01', 'act_mission_assign_01', 'act_ai_recon_01')
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row[2]} ({row[1]}) -> {row[3]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Seed completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False


if __name__ == "__main__":
    run_seed()
