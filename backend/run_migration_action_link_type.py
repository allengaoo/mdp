"""
Migration script to add link_type_id column to meta_action_def table.
Supports link_objects and unlink_objects operation types.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, text
from app.core.config import settings


def run_migration():
    """Execute the migration SQL."""
    engine = create_engine(str(settings.DATABASE_URL), echo=True)
    
    migration_sql = """
    ALTER TABLE meta_action_def
    ADD COLUMN IF NOT EXISTS link_type_id VARCHAR(64) NULL COMMENT 'Associated Link Type ID (used when operation_type is link_objects or unlink_objects)';
    """
    
    # Check if column already exists
    check_sql = """
    SELECT COUNT(*) as cnt 
    FROM information_schema.columns 
    WHERE table_schema = DATABASE()
    AND table_name = 'meta_action_def' 
    AND column_name = 'link_type_id';
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(check_sql))
        row = result.fetchone()
        
        if row and row[0] > 0:
            print("Column 'link_type_id' already exists in meta_action_def table. Skipping.")
            return
        
        # Add the column
        add_column_sql = """
        ALTER TABLE meta_action_def
        ADD COLUMN link_type_id VARCHAR(64) NULL COMMENT 'Associated Link Type ID (used when operation_type is link_objects or unlink_objects)';
        """
        conn.execute(text(add_column_sql))
        conn.commit()
        print("Successfully added 'link_type_id' column to meta_action_def table.")
        
        # Try to add index (may fail if already exists)
        try:
            index_sql = "CREATE INDEX idx_action_def_link_type ON meta_action_def(link_type_id);"
            conn.execute(text(index_sql))
            conn.commit()
            print("Successfully added index on link_type_id.")
        except Exception as e:
            print(f"Index creation skipped (may already exist): {e}")


if __name__ == "__main__":
    run_migration()
