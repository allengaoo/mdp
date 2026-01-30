"""
Run migration script for ctx_object_mapping_def table.
MDP Platform V3.1 - Multimodal Mapping Module
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.logger import logger


def run_migration():
    """Execute the migration SQL script."""
    
    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "create_mapping_table.sql"
    
    if not migration_file.exists():
        logger.error(f"Migration file not found: {migration_file}")
        return False
    
    sql_content = migration_file.read_text(encoding="utf-8")
    
    # Filter out comments and empty lines for execution
    # Split by semicolon to get individual statements
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('--') or stripped.startswith('/*'):
            continue
        if stripped.startswith('*/'):
            continue
            
        current_statement.append(line)
        
        if stripped.endswith(';'):
            stmt = '\n'.join(current_statement)
            # Only add CREATE TABLE statements
            if 'CREATE TABLE' in stmt.upper():
                statements.append(stmt)
            current_statement = []
    
    if not statements:
        logger.warning("No executable statements found in migration file")
        return False
    
    # Execute migration
    logger.info(f"Connecting to database: {settings.database_url}")
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            for stmt in statements:
                logger.info(f"Executing statement...")
                logger.debug(stmt[:200] + "..." if len(stmt) > 200 else stmt)
                conn.execute(text(stmt))
                conn.commit()
            
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        engine.dispose()


def verify_table():
    """Verify the table was created."""
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'ctx_object_mapping_def'
            """))
            exists = result.scalar() > 0
            
            if exists:
                logger.info("✓ Table ctx_object_mapping_def exists")
                
                # Show table structure
                result = conn.execute(text("DESCRIBE ctx_object_mapping_def"))
                logger.info("Table structure:")
                for row in result:
                    logger.info(f"  {row[0]}: {row[1]}")
            else:
                logger.warning("✗ Table ctx_object_mapping_def does not exist")
            
            return exists
            
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("MDP Platform - Mapping Table Migration")
    print("=" * 50)
    
    # Run migration
    success = run_migration()
    
    if success:
        # Verify
        print("\nVerifying table creation...")
        verify_table()
    
    print("\nDone.")
