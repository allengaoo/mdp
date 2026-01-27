"""
Migration script for Connector Management module.
Creates/updates tables: sys_connection, sys_sync_job_def, sys_sync_run_log

Run: python migrate_connector_tables.py
"""
import pymysql
from app.core.config import settings

def get_connection():
    """Get database connection from settings."""
    # Parse connection string
    # Format: mysql+pymysql://user:password@host:port/database
    url = settings.database_url
    url = url.replace("mysql+pymysql://", "")
    
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, database = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 3306
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )


def run_migration():
    """Run the migration."""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Connector Management - Database Migration")
    print("=" * 60)
    
    try:
        # ==========================================
        # Step 1: Check if sys_connection exists
        # ==========================================
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'sys_connection'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            print("\n[1/3] Updating sys_connection table...")
            
            # Check which columns exist
            cursor.execute("""
                SELECT COLUMN_NAME FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = 'sys_connection'
            """)
            existing_columns = {row[0] for row in cursor.fetchall()}
            print(f"  Existing columns: {existing_columns}")
            
            # Add missing columns
            columns_to_add = []
            
            if 'conn_type' not in existing_columns:
                columns_to_add.append(
                    "ADD COLUMN `conn_type` VARCHAR(50) NOT NULL DEFAULT 'MYSQL' AFTER `name`"
                )
            
            if 'status' not in existing_columns:
                columns_to_add.append(
                    "ADD COLUMN `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' AFTER `config_json`"
                )
            
            if 'error_message' not in existing_columns:
                columns_to_add.append(
                    "ADD COLUMN `error_message` VARCHAR(500) NULL AFTER `status`"
                )
            
            if 'last_tested_at' not in existing_columns:
                columns_to_add.append(
                    "ADD COLUMN `last_tested_at` DATETIME NULL AFTER `error_message`"
                )
            
            if 'updated_at' not in existing_columns:
                columns_to_add.append(
                    "ADD COLUMN `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP AFTER `created_at`"
                )
            
            if columns_to_add:
                alter_sql = f"ALTER TABLE `sys_connection` {', '.join(columns_to_add)}"
                print(f"  Executing: {alter_sql[:100]}...")
                cursor.execute(alter_sql)
                print(f"  Added {len(columns_to_add)} column(s)")
            else:
                print("  All columns already exist")
        else:
            print("\n[1/3] Creating sys_connection table...")
            cursor.execute("""
                CREATE TABLE `sys_connection` (
                    `id` VARCHAR(36) NOT NULL,
                    `name` VARCHAR(100) NOT NULL,
                    `conn_type` VARCHAR(50) NOT NULL DEFAULT 'MYSQL',
                    `config_json` JSON NOT NULL,
                    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    `error_message` VARCHAR(500) NULL,
                    `last_tested_at` DATETIME NULL,
                    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print("  Created sys_connection table")
        
        # ==========================================
        # Step 2: Create sys_sync_job_def
        # ==========================================
        print("\n[2/3] Creating sys_sync_job_def table...")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'sys_sync_job_def'
        """)
        if cursor.fetchone()[0] > 0:
            print("  Table already exists, skipping")
        else:
            cursor.execute("""
                CREATE TABLE `sys_sync_job_def` (
                    `id` VARCHAR(36) NOT NULL,
                    `connection_id` VARCHAR(36) NOT NULL,
                    `name` VARCHAR(100) NOT NULL,
                    `source_config` JSON NOT NULL,
                    `target_table` VARCHAR(100) NOT NULL,
                    `sync_mode` VARCHAR(50) NOT NULL DEFAULT 'FULL_OVERWRITE',
                    `schedule_cron` VARCHAR(100) NULL,
                    `is_enabled` TINYINT(1) NOT NULL DEFAULT 1,
                    `last_run_status` VARCHAR(20) NULL,
                    `last_run_at` DATETIME NULL,
                    `rows_synced` INT NULL,
                    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    INDEX `idx_connection_id` (`connection_id`),
                    CONSTRAINT `fk_sync_job_connection` 
                        FOREIGN KEY (`connection_id`) REFERENCES `sys_connection` (`id`) 
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print("  Created sys_sync_job_def table")
        
        # ==========================================
        # Step 3: Create sys_sync_run_log
        # ==========================================
        print("\n[3/3] Creating sys_sync_run_log table...")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'sys_sync_run_log'
        """)
        if cursor.fetchone()[0] > 0:
            print("  Table already exists, skipping")
        else:
            cursor.execute("""
                CREATE TABLE `sys_sync_run_log` (
                    `id` VARCHAR(36) NOT NULL,
                    `job_id` VARCHAR(36) NOT NULL,
                    `start_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `end_time` DATETIME NULL,
                    `duration_ms` INT NULL,
                    `rows_affected` INT NULL,
                    `status` VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
                    `message` TEXT NULL,
                    `triggered_by` VARCHAR(50) NOT NULL DEFAULT 'MANUAL',
                    PRIMARY KEY (`id`),
                    INDEX `idx_job_id` (`job_id`),
                    CONSTRAINT `fk_run_log_job` 
                        FOREIGN KEY (`job_id`) REFERENCES `sys_sync_job_def` (`id`) 
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print("  Created sys_sync_run_log table")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
        # Show table info
        print("\nTable summary:")
        for table in ['sys_connection', 'sys_sync_job_def', 'sys_sync_run_log']:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} rows")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
