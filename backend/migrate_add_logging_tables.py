#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to add action logging and test scenario tables.
Adds sys_action_log and meta_test_scenario tables with seed data.
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
    print("MDP Platform Demo - Logging & Testing Tables Migration")
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
        
        # Step 2: Create sys_action_log table
        print("\n[Step 2] Creating sys_action_log table...")
        create_action_log_table = """
        CREATE TABLE IF NOT EXISTS `sys_action_log` (
          `id` varchar(36) NOT NULL,
          `project_id` varchar(36) NOT NULL,
          `action_def_id` varchar(36) NOT NULL,
          `trigger_user_id` varchar(36) COMMENT '触发用户',
          `input_params` json COMMENT '执行入参',
          `execution_status` varchar(20) COMMENT 'SUCCESS, FAILED',
          `error_message` text,
          `duration_ms` int COMMENT '执行耗时',
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          KEY `ix_sys_action_log_project_id` (`project_id`),
          KEY `ix_sys_action_log_action_def_id` (`action_def_id`),
          KEY `ix_sys_action_log_created_at` (`created_at`),
          CONSTRAINT `fk_action_log_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE,
          CONSTRAINT `fk_action_log_action_def` FOREIGN KEY (`action_def_id`) REFERENCES `meta_action_def` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_action_log_table)
        connection.commit()
        print("  [OK] sys_action_log table created or already exists")
        
        # Step 3: Create meta_test_scenario table
        print("\n[Step 3] Creating meta_test_scenario table...")
        create_test_scenario_table = """
        CREATE TABLE IF NOT EXISTS `meta_test_scenario` (
          `id` varchar(36) NOT NULL,
          `project_id` varchar(36) NOT NULL,
          `name` varchar(100),
          `steps_config` json COMMENT '存储编排的动作序列，例如 [{"actionId": "...", "params": "..."}]',
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          KEY `ix_meta_test_scenario_project_id` (`project_id`),
          CONSTRAINT `fk_test_scenario_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_test_scenario_table)
        connection.commit()
        print("  [OK] meta_test_scenario table created or already exists")
        
        # Step 4: Insert action log seed data
        print("\n[Step 4] Inserting action log seed data...")
        battlefield_project_id = '00000000-0000-0000-0000-000000000001'
        
        action_logs = [
            ('80000000-0000-0000-0000-000000000001', battlefield_project_id, '40000000-0000-0000-0000-000000000001', 'user-001', '{"source_id": "51000000-0000-0000-0000-000000000001", "params": {"weapon_type": "missile"}}', 'SUCCESS', None, 125, '2024-01-15 10:30:00'),
            ('80000000-0000-0000-0000-000000000002', battlefield_project_id, '40000000-0000-0000-0000-000000000002', 'user-001', '{"source_id": "50000000-0000-0000-0000-000000000001", "params": {"fuel_amount": 50}}', 'SUCCESS', None, 89, '2024-01-15 10:35:00'),
            ('80000000-0000-0000-0000-000000000003', battlefield_project_id, '40000000-0000-0000-0000-000000000001', 'user-002', '{"source_id": "51000000-0000-0000-0000-000000000002", "params": {"weapon_type": "bomb"}}', 'SUCCESS', None, 142, '2024-01-15 11:00:00'),
            ('80000000-0000-0000-0000-000000000004', battlefield_project_id, '40000000-0000-0000-0000-000000000003', 'user-001', '{"source_id": "54000000-0000-0000-0000-000000000001", "params": {"count": 4}}', 'SUCCESS', None, 203, '2024-01-15 11:15:00'),
            ('80000000-0000-0000-0000-000000000005', battlefield_project_id, '40000000-0000-0000-0000-000000000001', 'user-003', '{"source_id": "51000000-0000-0000-0000-000000000003", "params": {"weapon_type": "missile"}}', 'FAILED', 'Target not in range', 45, '2024-01-15 11:30:00'),
            ('80000000-0000-0000-0000-000000000006', battlefield_project_id, '40000000-0000-0000-0000-000000000004', 'user-002', '{"source_id": "53000000-0000-0000-0000-000000000001", "params": {"new_data": "Updated intelligence report"}}', 'SUCCESS', None, 67, '2024-01-15 12:00:00'),
            ('80000000-0000-0000-0000-000000000007', battlefield_project_id, '40000000-0000-0000-0000-000000000005', 'user-001', '{"source_id": "52000000-0000-0000-0000-000000000001", "params": {"fighter_id": "50000000-0000-0000-0000-000000000001"}}', 'SUCCESS', None, 98, '2024-01-15 12:15:00'),
            ('80000000-0000-0000-0000-000000000008', battlefield_project_id, '40000000-0000-0000-0000-000000000001', 'user-003', '{"source_id": "51000000-0000-0000-0000-000000000004", "params": {"weapon_type": "cannon"}}', 'SUCCESS', None, 156, '2024-01-15 12:30:00'),
        ]
        
        inserted_logs = 0
        for log_id, proj_id, action_id, user_id, params, status, error, duration, created_at in action_logs:
            check_sql = "SELECT COUNT(*) FROM `sys_action_log` WHERE `id` = %s;"
            cursor.execute(check_sql, (log_id,))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                insert_sql = """
                INSERT INTO `sys_action_log` (`id`, `project_id`, `action_def_id`, `trigger_user_id`, `input_params`, `execution_status`, `error_message`, `duration_ms`, `created_at`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_sql, (log_id, proj_id, action_id, user_id, params, status, error, duration, created_at))
                inserted_logs += 1
        
        connection.commit()
        print(f"  [OK] Inserted {inserted_logs} action logs")
        
        # Step 5: Insert test scenario seed data
        print("\n[Step 5] Inserting test scenario seed data...")
        test_scenarios = [
            ('90000000-0000-0000-0000-000000000001', battlefield_project_id, 'Standard Strike Sequence', '[{"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "missile"}, "sourceId": "51000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000002", "actionName": "refuel", "params": {"fuel_amount": 50}, "sourceId": "50000000-0000-0000-0000-000000000001"}]', '2024-01-15 10:00:00'),
            ('90000000-0000-0000-0000-000000000002', battlefield_project_id, 'Mission Assignment Flow', '[{"actionId": "40000000-0000-0000-0000-000000000005", "actionName": "assign_to_mission", "params": {}, "sourceId": "52000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000008", "actionName": "check_mission", "params": {}, "sourceId": "52000000-0000-0000-0000-000000000001"}]', '2024-01-15 10:30:00'),
            ('90000000-0000-0000-0000-000000000003', battlefield_project_id, 'Intelligence Update Sequence', '[{"actionId": "40000000-0000-0000-0000-000000000004", "actionName": "update_intel", "params": {"new_data": "Target coordinates verified"}, "sourceId": "53000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "bomb"}, "sourceId": "51000000-0000-0000-0000-000000000002"}]', '2024-01-15 11:00:00'),
            ('90000000-0000-0000-0000-000000000004', battlefield_project_id, 'Quick Reaction Alert', '[{"actionId": "40000000-0000-0000-0000-000000000003", "actionName": "scramble", "params": {"count": 4}, "sourceId": "54000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "missile"}, "sourceId": "51000000-0000-0000-0000-000000000001"}]', '2024-01-15 11:30:00'),
        ]
        
        inserted_scenarios = 0
        for scenario_id, proj_id, name, steps_config, created_at in test_scenarios:
            check_sql = "SELECT COUNT(*) FROM `meta_test_scenario` WHERE `id` = %s;"
            cursor.execute(check_sql, (scenario_id,))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                insert_sql = """
                INSERT INTO `meta_test_scenario` (`id`, `project_id`, `name`, `steps_config`, `created_at`) 
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(insert_sql, (scenario_id, proj_id, name, steps_config, created_at))
                inserted_scenarios += 1
        
        connection.commit()
        print(f"  [OK] Inserted {inserted_scenarios} test scenarios")
        
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

