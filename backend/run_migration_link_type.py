"""
Migration script to add link_type_id column to meta_action_def table.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the migration to add link_type_id column."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False
    
    engine = create_engine(database_url)
    
    migration_sql = Path(__file__).parent / "migrations" / "alter_action_def_link_type.sql"
    
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'meta_action_def' 
                AND COLUMN_NAME = 'link_type_id'
            """))
            
            if result.fetchone():
                print("Column 'link_type_id' already exists in meta_action_def")
                return True
            
            # Read and execute migration SQL
            sql_content = migration_sql.read_text()
            
            # Execute each statement separately
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    print(f"Executing: {statement[:50]}...")
                    conn.execute(text(statement))
            
            conn.commit()
            print("Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
            return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
