"""
Migration Script: Add Search Configuration Flags
MDP Platform V3.1 - Global Search Module

Adds is_searchable, is_filterable, is_sortable columns to rel_object_ver_property table.
"""
import os
import sys
from pathlib import Path

# Add backend to path
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
    """Execute the search flags migration."""
    import pymysql
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Parse connection parameters
    db_params = parse_database_url(database_url)
    print(f"Connecting to {db_params['host']}:{db_params['port']}/{db_params['database']}...")
    
    # Connect to database
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
            # Check if columns already exist
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'rel_object_ver_property'
                AND COLUMN_NAME IN ('is_searchable', 'is_filterable', 'is_sortable')
            """, (db_params["database"],))
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            if len(existing_columns) == 3:
                print("All search flag columns already exist. Migration skipped.")
                return
            
            print(f"Existing columns: {existing_columns}")
            print("Running migration...")
            
            # Add columns if not exist
            if 'is_searchable' not in existing_columns:
                print("  Adding is_searchable column...")
                cursor.execute("""
                    ALTER TABLE rel_object_ver_property
                    ADD COLUMN is_searchable TINYINT(1) NOT NULL DEFAULT 0 
                    COMMENT 'Enable full-text search indexing'
                """)
            
            if 'is_filterable' not in existing_columns:
                print("  Adding is_filterable column...")
                cursor.execute("""
                    ALTER TABLE rel_object_ver_property
                    ADD COLUMN is_filterable TINYINT(1) NOT NULL DEFAULT 0 
                    COMMENT 'Enable facet/aggregation indexing'
                """)
            
            if 'is_sortable' not in existing_columns:
                print("  Adding is_sortable column...")
                cursor.execute("""
                    ALTER TABLE rel_object_ver_property
                    ADD COLUMN is_sortable TINYINT(1) NOT NULL DEFAULT 0 
                    COMMENT 'Enable sorting capability'
                """)
            
            # Check for existing indexes before creating
            cursor.execute("""
                SELECT INDEX_NAME 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'rel_object_ver_property'
                AND INDEX_NAME LIKE 'idx_property_%%'
            """, (db_params["database"],))
            
            existing_indexes = [row[0] for row in cursor.fetchall()]
            
            if 'idx_property_searchable' not in existing_indexes:
                print("  Creating idx_property_searchable index...")
                cursor.execute("""
                    CREATE INDEX idx_property_searchable 
                    ON rel_object_ver_property (is_searchable)
                """)
            
            if 'idx_property_filterable' not in existing_indexes:
                print("  Creating idx_property_filterable index...")
                cursor.execute("""
                    CREATE INDEX idx_property_filterable 
                    ON rel_object_ver_property (is_filterable)
                """)
            
            connection.commit()
            print("Migration completed successfully!")
            
            # Verify
            cursor.execute("""
                SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'rel_object_ver_property'
                AND COLUMN_NAME IN ('is_searchable', 'is_filterable', 'is_sortable')
            """, (db_params["database"],))
            
            print("\nVerification - New columns:")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} - {row[2]}")
                
    finally:
        connection.close()


if __name__ == "__main__":
    run_migration()
