#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to add shared property support to existing database.
Adds meta_shared_property table and seed data.
"""
import sys
import io
import pymysql
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'charset': 'utf8mb4'
}

DB_NAME = 'ontology'


def main():
    """Migration workflow."""
    print("=" * 60)
    print("MDP Platform Demo - Shared Property Migration")
    print("=" * 60)
    
    connection = None
    
    try:
        # Connect to database
        print("\n[Step 1] Connecting to database...")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_NAME,
            charset=DB_CONFIG['charset']
        )
        cursor = connection.cursor()
        print(f"  [OK] Connected to database '{DB_NAME}'")
        
        # Step 2: Create meta_shared_property table if not exists
        print("\n[Step 2] Creating meta_shared_property table...")
        create_table = """
        CREATE TABLE IF NOT EXISTS `meta_shared_property` (
          `id` varchar(36) NOT NULL,
          `project_id` varchar(36) NOT NULL COMMENT '归属的项目',
          `api_name` varchar(100) NOT NULL,
          `display_name` varchar(200) NOT NULL,
          `data_type` varchar(50) NOT NULL COMMENT 'String, Integer, Date...',
          `formatter` varchar(500) DEFAULT NULL COMMENT '格式化规则',
          `description` varchar(500),
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          CONSTRAINT `fk_shared_prop_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table)
        connection.commit()
        print("  [OK] meta_shared_property table created or already exists")
        
        # Step 3: Insert seed data if not exists
        print("\n[Step 3] Inserting shared property seed data...")
        battlefield_project_id = '00000000-0000-0000-0000-000000000001'
        
        shared_properties = [
            ('70000000-0000-0000-0000-000000000001', battlefield_project_id, 'location_lat', 'Latitude', 'Number', 'decimal:6', 'Geographic latitude coordinate'),
            ('70000000-0000-0000-0000-000000000002', battlefield_project_id, 'location_lon', 'Longitude', 'Number', 'decimal:6', 'Geographic longitude coordinate'),
            ('70000000-0000-0000-0000-000000000003', battlefield_project_id, 'status', 'Status', 'String', None, 'Current operational status'),
            ('70000000-0000-0000-0000-000000000004', battlefield_project_id, 'name', 'Name', 'String', None, 'Display name or identifier'),
            ('70000000-0000-0000-0000-000000000005', battlefield_project_id, 'priority', 'Priority', 'Integer', None, 'Priority level (1-10)'),
            ('70000000-0000-0000-0000-000000000006', battlefield_project_id, 'created_time', 'Created Time', 'DateTime', 'iso8601', 'Creation timestamp'),
        ]
        
        inserted_count = 0
        for prop_id, proj_id, api_name, display_name, data_type, formatter, description in shared_properties:
            # Check if exists
            check_sql = "SELECT COUNT(*) FROM `meta_shared_property` WHERE `id` = %s;"
            cursor.execute(check_sql, (prop_id,))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                insert_sql = """
                INSERT INTO `meta_shared_property` (`id`, `project_id`, `api_name`, `display_name`, `data_type`, `formatter`, `description`, `created_at`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW());
                """
                cursor.execute(insert_sql, (prop_id, proj_id, api_name, display_name, data_type, formatter, description))
                inserted_count += 1
            else:
                print(f"  [SKIP] Shared property {api_name} already exists")
        
        connection.commit()
        print(f"  [OK] Inserted {inserted_count} shared properties")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except pymysql.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("\n[OK] Database connection closed")


if __name__ == '__main__':
    main()

