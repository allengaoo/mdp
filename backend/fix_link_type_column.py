"""
Fix script to add link_type_id column to meta_action_def table.
"""
import pymysql

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology_meta_new',
    'charset': 'utf8mb4'
}

def run_fix():
    """Add link_type_id column if it doesn't exist."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'ontology_meta_new' 
            AND TABLE_NAME = 'meta_action_def' 
            AND COLUMN_NAME = 'link_type_id'
        """)
        
        if cursor.fetchone():
            print("Column 'link_type_id' already exists in meta_action_def")
            return True
        
        # Add the column
        print("Adding link_type_id column...")
        cursor.execute("""
            ALTER TABLE meta_action_def
            ADD COLUMN link_type_id VARCHAR(64) NULL 
            COMMENT 'Link Type ID for link_objects/unlink_objects operations'
        """)
        conn.commit()
        print("Column added successfully!")
        
        # Verify
        cursor.execute("DESCRIBE meta_action_def")
        columns = cursor.fetchall()
        print("\nCurrent columns in meta_action_def:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_fix()
