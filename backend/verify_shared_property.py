#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify shared property migration - check data.
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
    print("Verifying Shared Property Data")
    print("=" * 60)
    
    # Check shared properties
    print("\n[Shared Properties]")
    cursor.execute("""
        SELECT sp.id, sp.api_name, sp.display_name, sp.data_type, p.name as project_name
        FROM meta_shared_property sp
        LEFT JOIN meta_project p ON sp.project_id = p.id
        ORDER BY sp.api_name;
    """)
    properties = cursor.fetchall()
    print(f"  Total shared properties: {len(properties)}")
    for prop in properties:
        print(f"  - {prop[1]} ({prop[2]}) - Type: {prop[3]} - Project: {prop[4]}")
    
    # Count by project
    print("\n[Statistics]")
    cursor.execute("""
        SELECT p.name, COUNT(sp.id) as count
        FROM meta_project p
        LEFT JOIN meta_shared_property sp ON sp.project_id = p.id
        GROUP BY p.id, p.name;
    """)
    stats = cursor.fetchall()
    for stat in stats:
        print(f"  - {stat[0]}: {stat[1]} shared properties")
    
    print("\n" + "=" * 60)
    print("Verification completed!")
    print("=" * 60)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    raise

