"""
Migration script to add project_id column to meta_function_def table.
Supports project-scoped (Studio) vs global (OMA) function distinction.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Execute the migration."""
    engine = create_engine(str(settings.database_url), echo=True)

    check_sql = """
    SELECT COUNT(*) as cnt
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
    AND table_name = 'meta_function_def'
    AND column_name = 'project_id';
    """

    with engine.connect() as conn:
        result = conn.execute(text(check_sql))
        row = result.fetchone()

        if row and row[0] > 0:
            print("Column 'project_id' already exists in meta_function_def. Skipping.")
            return

        add_column_sql = """
        ALTER TABLE meta_function_def
        ADD COLUMN project_id VARCHAR(36) NULL COMMENT 'Project ID - NULL for global, non-null for project-scoped';
        """
        conn.execute(text(add_column_sql))
        conn.commit()
        print("Successfully added 'project_id' column to meta_function_def.")

        try:
            index_sql = "CREATE INDEX idx_function_def_project ON meta_function_def(project_id);"
            conn.execute(text(index_sql))
            conn.commit()
            print("Successfully added index on project_id.")
        except Exception as e:
            print(f"Index creation skipped: {e}")


if __name__ == "__main__":
    run_migration()
