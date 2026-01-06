#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update project name to Battlefield System"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("UPDATE meta_project SET name = 'Battlefield System' WHERE id = '00000000-0000-0000-0000-000000000001'")
    conn.commit()
    print('Project name updated to "Battlefield System"')
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')

