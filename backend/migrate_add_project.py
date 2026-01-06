#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to add project support to existing database.
Adds meta_project table and project_id column to meta_object_type.
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
    print("MDP Platform Demo - Project Migration")
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
        
        # Step 2: Create meta_project table if not exists
        print("\n[Step 2] Creating meta_project table...")
        create_project_table = """
        CREATE TABLE IF NOT EXISTS `meta_project` (
          `id` varchar(36) NOT NULL COMMENT 'UUID',
          `name` varchar(100) NOT NULL COMMENT '项目名称，如 Battlefield Demo',
          `description` varchar(500) DEFAULT NULL,
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_project_table)
        connection.commit()
        print("  [OK] meta_project table created or already exists")
        
        # Step 3: Add project_id column to meta_object_type if not exists
        print("\n[Step 3] Adding project_id column to meta_object_type...")
        try:
            add_project_id_column = """
            ALTER TABLE `meta_object_type` 
            ADD COLUMN `project_id` varchar(36) DEFAULT NULL COMMENT 'Project ID';
            """
            cursor.execute(add_project_id_column)
            connection.commit()
            print("  [OK] project_id column added")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print("  [OK] project_id column already exists")
            else:
                raise
        
        # Step 4: Add foreign key constraint if not exists
        print("\n[Step 4] Adding foreign key constraint...")
        try:
            # First, check if constraint already exists
            check_constraint = """
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = %s 
            AND TABLE_NAME = 'meta_object_type' 
            AND CONSTRAINT_NAME = 'fk_obj_project';
            """
            cursor.execute(check_constraint, (DB_NAME,))
            exists = cursor.fetchone()[0]
            
            if not exists:
                add_foreign_key = """
                ALTER TABLE `meta_object_type`
                ADD CONSTRAINT `fk_obj_project` FOREIGN KEY (`project_id`) 
                REFERENCES `meta_project` (`id`) ON DELETE SET NULL;
                """
                cursor.execute(add_foreign_key)
                connection.commit()
                print("  [OK] Foreign key constraint added")
            else:
                print("  [OK] Foreign key constraint already exists")
        except pymysql.Error as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("  [OK] Foreign key constraint already exists")
            else:
                raise
        
        # Step 5: Add index if not exists
        print("\n[Step 5] Adding index on project_id...")
        try:
            add_index = """
            ALTER TABLE `meta_object_type`
            ADD INDEX `ix_meta_object_type_project_id` (`project_id`);
            """
            cursor.execute(add_index)
            connection.commit()
            print("  [OK] Index added")
        except pymysql.Error as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("  [OK] Index already exists")
            else:
                raise
        
        # Step 6: Create Battlefield project if not exists
        print("\n[Step 6] Creating Battlefield project...")
        battlefield_project_id = '00000000-0000-0000-0000-000000000001'
        check_project = "SELECT COUNT(*) FROM `meta_project` WHERE `id` = %s;"
        cursor.execute(check_project, (battlefield_project_id,))
        project_exists = cursor.fetchone()[0] > 0
        
        if not project_exists:
            insert_project = """
            INSERT INTO `meta_project` (`id`, `name`, `description`, `created_at`) 
            VALUES (%s, 'Battlefield', 'Battlefield Demo Project - Military operations simulation', NOW());
            """
            cursor.execute(insert_project, (battlefield_project_id,))
            connection.commit()
            print("  [OK] Battlefield project created")
        else:
            print("  [OK] Battlefield project already exists")
        
        # Step 7: Update existing object types to link to Battlefield project
        print("\n[Step 7] Linking existing object types to Battlefield project...")
        update_object_types = """
        UPDATE `meta_object_type` 
        SET `project_id` = %s 
        WHERE `project_id` IS NULL;
        """
        cursor.execute(update_object_types, (battlefield_project_id,))
        updated_count = cursor.rowcount
        connection.commit()
        print(f"  [OK] Updated {updated_count} object types to link to Battlefield project")
        
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

