"""
Migration script to extend meta_action_def table.
"""
import os
from pathlib import Path
from app.core.db import engine
from sqlalchemy import text

def run_migration():
    """Execute the migration SQL file."""
    migration_file = Path(__file__).parent / "migrations" / "alter_action_def.sql"
    
    if not migration_file.exists():
        print(f"Migration file not found: {migration_file}")
        return False
    
    sql_content = migration_file.read_text(encoding='utf-8')
    
    # Split by semicolon and filter empty statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    with engine.connect() as conn:
        for stmt in statements:
            if stmt:
                try:
                    print(f"Executing: {stmt[:80]}...")
                    conn.execute(text(stmt))
                    conn.commit()
                    print("  OK")
                except Exception as e:
                    error_msg = str(e)
                    # Ignore "duplicate column" errors (column already exists)
                    if "Duplicate column name" in error_msg:
                        print(f"  Skipped (column already exists)")
                    else:
                        print(f"  Error: {e}")
                        # Continue with other statements
    
    print("\nMigration completed!")
    return True

if __name__ == "__main__":
    run_migration()
