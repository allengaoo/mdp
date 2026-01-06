#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify logging tables migration - check data.
"""
import sys
import io
import pymysql

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology',
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    print("=" * 60)
    print("Verifying Logging & Testing Tables")
    print("=" * 60)
    
    # Check action logs
    print("\n[Action Logs]")
    cursor.execute("""
        SELECT al.id, al.execution_status, al.duration_ms, ad.display_name as action_name, p.name as project_name
        FROM sys_action_log al
        LEFT JOIN meta_action_def ad ON al.action_def_id = ad.id
        LEFT JOIN meta_project p ON al.project_id = p.id
        ORDER BY al.created_at DESC
        LIMIT 10;
    """)
    logs = cursor.fetchall()
    print(f"  Total action logs (showing latest 10): {len(logs)}")
    for log in logs:
        status_color = "✓" if log[1] == 'SUCCESS' else "✗"
        print(f"  {status_color} {log[3]} - Status: {log[1]} - Duration: {log[2]}ms - Project: {log[4]}")
    
    # Check test scenarios
    print("\n[Test Scenarios]")
    cursor.execute("""
        SELECT ts.id, ts.name, p.name as project_name, JSON_LENGTH(ts.steps_config) as step_count
        FROM meta_test_scenario ts
        LEFT JOIN meta_project p ON ts.project_id = p.id
        ORDER BY ts.created_at DESC;
    """)
    scenarios = cursor.fetchall()
    print(f"  Total test scenarios: {len(scenarios)}")
    for scenario in scenarios:
        print(f"  - {scenario[1]} - Steps: {scenario[3]} - Project: {scenario[2]}")
    
    # Statistics
    print("\n[Statistics]")
    cursor.execute("SELECT COUNT(*) FROM sys_action_log WHERE execution_status = 'SUCCESS';")
    success_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sys_action_log WHERE execution_status = 'FAILED';")
    failed_count = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(duration_ms) FROM sys_action_log WHERE execution_status = 'SUCCESS';")
    avg_duration = cursor.fetchone()[0]
    
    print(f"  - Successful executions: {success_count}")
    print(f"  - Failed executions: {failed_count}")
    print(f"  - Average duration: {avg_duration:.2f}ms")
    
    print("\n" + "=" * 60)
    print("Verification completed!")
    print("=" * 60)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    raise

