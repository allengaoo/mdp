"""
Run migration script for observability tables.
MDP Platform V3.1 - Index Health Module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Execute the migration SQL script."""
    
    migration_file = Path(__file__).parent / "migrations" / "create_observability_tables.sql"
    
    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False
    
    sql_content = migration_file.read_text(encoding="utf-8")
    
    # Extract CREATE TABLE statements
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('--'):
            continue
            
        current_statement.append(line)
        
        if stripped.endswith(';'):
            stmt = '\n'.join(current_statement)
            if 'CREATE TABLE' in stmt.upper():
                statements.append(stmt)
            current_statement = []
    
    if not statements:
        print("WARNING: No executable statements found")
        return False
    
    print(f"Connecting to database...")
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            for i, stmt in enumerate(statements, 1):
                print(f"Executing statement {i}/{len(statements)}...")
                conn.execute(text(stmt))
                conn.commit()
            
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False
    finally:
        engine.dispose()


def verify_tables():
    """Verify tables were created."""
    engine = create_engine(settings.database_url)
    
    tables = ["sys_index_job_run", "sys_index_error_sample"]
    
    try:
        with engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{table}'
                """))
                exists = result.scalar() > 0
                
                if exists:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} NOT FOUND")
            
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("MDP Platform - Observability Tables Migration")
    print("=" * 50)
    
    success = run_migration()
    
    if success:
        print("\nVerifying tables...")
        verify_tables()
    
    print("\nDone.")
