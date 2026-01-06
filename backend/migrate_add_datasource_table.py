"""
Migration script to add sys_datasource_table.
Run this after init.sql and seed_data.sql have been executed.
"""
import pymysql
import os

# Try to load .env, but don't fail if it has encoding issues
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Database configuration (matching setup_db.py)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'charset': 'utf8mb4'
}
DB_NAME = 'ontology'

def migrate():
    """Add sys_datasource_table and seed data."""
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_NAME,
        charset=DB_CONFIG['charset']
    )
    
    try:
        cur = conn.cursor()
        
        print("Creating sys_datasource_table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS `sys_datasource_table` (
              `id` varchar(36) NOT NULL COMMENT 'UUID',
              `table_name` varchar(100) NOT NULL COMMENT '原始数据表名',
              `db_type` varchar(20) DEFAULT 'MySQL' COMMENT '数据库类型',
              `columns_schema` json COMMENT '存储列定义 [{"name": "id", "type": "int"}, ...]',
              `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              UNIQUE KEY `ix_sys_datasource_table_name` (`table_name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        print("Inserting seed data...")
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM `sys_datasource_table`")
        count = cur.fetchone()[0]
        
        if count == 0:
            cur.execute("""
                INSERT INTO `sys_datasource_table` (`id`, `table_name`, `db_type`, `columns_schema`, `created_at`) VALUES
                ('d1000000-0000-0000-0000-000000000001', 'raw_fighter_data', 'MySQL', '[{"name": "f_id", "type": "varchar", "length": 36}, {"name": "f_model", "type": "varchar", "length": 50}, {"name": "current_fuel", "type": "int"}, {"name": "callsign", "type": "varchar", "length": 20}, {"name": "status", "type": "varchar", "length": 20}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "altitude", "type": "int"}, {"name": "weapons", "type": "json"}]', NOW()),
                ('d1000000-0000-0000-0000-000000000002', 'raw_target_data', 'MySQL', '[{"name": "t_id", "type": "varchar", "length": 36}, {"name": "name", "type": "varchar", "length": 100}, {"name": "threat_level", "type": "varchar", "length": 20}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "type", "type": "varchar", "length": 50}, {"name": "priority", "type": "int"}, {"name": "health", "type": "int"}]', NOW()),
                ('d1000000-0000-0000-0000-000000000003', 'raw_mission_log', 'MySQL', '[{"name": "m_code", "type": "varchar", "length": 50}, {"name": "name", "type": "varchar", "length": 100}, {"name": "type", "type": "varchar", "length": 50}, {"name": "status", "type": "varchar", "length": 20}, {"name": "priority", "type": "int"}, {"name": "start_time", "type": "datetime"}, {"name": "end_time", "type": "datetime"}]', NOW()),
                ('d1000000-0000-0000-0000-000000000004', 'raw_intelligence_data', 'MySQL', '[{"name": "i_id", "type": "varchar", "length": 36}, {"name": "source", "type": "varchar", "length": 50}, {"name": "classification", "type": "varchar", "length": 50}, {"name": "validity", "type": "datetime"}, {"name": "confidence", "type": "decimal", "precision": 3, "scale": 2}, {"name": "content", "type": "text"}]', NOW()),
                ('d1000000-0000-0000-0000-000000000005', 'raw_base_data', 'MySQL', '[{"name": "b_id", "type": "varchar", "length": 36}, {"name": "name", "type": "varchar", "length": 100}, {"name": "location", "type": "varchar", "length": 100}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "capacity", "type": "int"}, {"name": "status", "type": "varchar", "length": 20}]', NOW());
            """)
            print("Seed data inserted successfully.")
        else:
            print(f"Seed data already exists ({count} records). Skipping insert.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()

