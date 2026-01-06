"""
Migration script to add new fields to meta_function_def table.
Adds: description, input_params_schema, output_type
"""
import pymysql
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Database configuration (matching setup_db.py)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology',
    'charset': 'utf8mb4',
}

def migrate():
    """Apply migration to add new fields to meta_function_def table."""
    connection = None
    try:
        print("Connecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Applying migration: Adding new fields to meta_function_def...")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'meta_function_def' 
            AND COLUMN_NAME = 'description'
        """, (DB_CONFIG['database'],))
        
        if cursor.fetchone()[0] > 0:
            print("Columns already exist. Skipping migration.")
            return
        
        # Add new columns
        alter_sql = """
        ALTER TABLE `meta_function_def` 
        ADD COLUMN `description` varchar(500) COMMENT '函数描述',
        ADD COLUMN `input_params_schema` json COMMENT '输入参数定义 [{"name":"a", "type":"int", "required":true}]',
        ADD COLUMN `output_type` varchar(50) DEFAULT 'VOID' COMMENT '返回值类型: STRING, INTEGER, OBJECT, VOID等';
        """
        
        cursor.execute(alter_sql)
        connection.commit()
        
        print("Migration applied successfully!")
        print("  - Added 'description' column")
        print("  - Added 'input_params_schema' column (JSON)")
        print("  - Added 'output_type' column (default: 'VOID')")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    migrate()

