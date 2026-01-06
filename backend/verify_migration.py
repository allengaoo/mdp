#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify migration - check project and object type relationships.
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
    print("Verifying Migration Results")
    print("=" * 60)
    
    # Check projects
    print("\n[Projects]")
    cursor.execute("SELECT id, name, description FROM meta_project;")
    projects = cursor.fetchall()
    for project in projects:
        print(f"  - {project[1]} (ID: {project[0]})")
        if project[2]:
            print(f"    Description: {project[2]}")
    
    # Check object types with project_id
    print("\n[Object Types with Project]")
    cursor.execute("""
        SELECT ot.api_name, ot.display_name, p.name as project_name
        FROM meta_object_type ot
        LEFT JOIN meta_project p ON ot.project_id = p.id
        ORDER BY ot.api_name;
    """)
    object_types = cursor.fetchall()
    print(f"  Total object types: {len(object_types)}")
    for ot in object_types:
        project_name = ot[2] if ot[2] else "NULL"
        print(f"  - {ot[0]} ({ot[1]}) -> Project: {project_name}")
    
    # Count by project
    print("\n[Statistics]")
    cursor.execute("""
        SELECT p.name, COUNT(ot.id) as count
        FROM meta_project p
        LEFT JOIN meta_object_type ot ON ot.project_id = p.id
        GROUP BY p.id, p.name;
    """)
    stats = cursor.fetchall()
    for stat in stats:
        print(f"  - {stat[0]}: {stat[1]} object types")
    
    cursor.execute("SELECT COUNT(*) FROM meta_object_type WHERE project_id IS NULL;")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        print(f"  - Unassigned object types: {null_count}")
    
    print("\n" + "=" * 60)
    print("Verification completed!")
    print("=" * 60)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    raise

