#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database setup script for MDP Platform Demo.
Creates the database, applies schema, and loads seed data.
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

# SQL file paths
BASE_DIR = Path(__file__).parent
INIT_SQL_FILE = BASE_DIR / 'init.sql'
SEED_SQL_FILE = BASE_DIR / 'seed_data.sql'


def execute_sql_statements(cursor, sql_content: str, description: str):
    """Execute SQL statements from a string, splitting by semicolon."""
    # Remove comments (lines starting with --) but keep SQL
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip comment-only lines
        if line.strip().startswith('--'):
            continue
        # Remove inline comments (but keep the SQL part)
        if '--' in line:
            line = line.split('--')[0]
        cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Split by semicolon and filter out empty statements
    statements = []
    for part in cleaned_content.split(';'):
        part = part.strip()
        if part:
            # Skip SET FOREIGN_KEY_CHECKS as it's handled by pymysql automatically
            if 'FOREIGN_KEY_CHECKS' in part.upper() or 'SET NAMES' in part.upper():
                continue
            statements.append(part)
    
    executed = 0
    for statement in statements:
        if not statement or statement.isspace():
            continue
            
        try:
            cursor.execute(statement)
            executed += 1
        except Exception as e:
            print(f"  Warning: Error executing statement: {e}")
            # Print first 200 chars for debugging
            preview = statement[:200].replace('\n', ' ')
            print(f"  Statement preview: {preview}...")
            # Continue with next statement
    
    print(f"  [OK] Executed {executed} statements")
    return executed


def main():
    """Main setup workflow."""
    print("=" * 60)
    print("MDP Platform Demo - Database Setup")
    print("=" * 60)
    
    connection = None
    
    try:
        # Step 1: Connect without database to create it
        print("\n[Step 1] Connecting to MySQL server...")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = connection.cursor()
        print("  [OK] Connected to MySQL server")
        
        # Step 2: Create database
        print(f"\n[Step 2] Creating database '{DB_NAME}'...")
        create_db_sql = f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        cursor.execute(create_db_sql)
        print(f"  [OK] Database '{DB_NAME}' created or already exists")
        
        # Step 3: Connect to the new database
        print(f"\n[Step 3] Connecting to database '{DB_NAME}'...")
        cursor.close()
        connection.close()
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
        
        # Step 4: Execute schema (init.sql)
        print(f"\n[Step 4] Applying schema from {INIT_SQL_FILE.name}...")
        if not INIT_SQL_FILE.exists():
            raise FileNotFoundError(f"Schema file not found: {INIT_SQL_FILE}")
        
        with open(INIT_SQL_FILE, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        execute_sql_statements(cursor, schema_content, "Schema")
        connection.commit()
        print("  [OK] Schema applied successfully")
        
        # Step 5: Execute seed data (seed_data.sql)
        print(f"\n[Step 5] Loading seed data from {SEED_SQL_FILE.name}...")
        if not SEED_SQL_FILE.exists():
            print(f"  [WARN] Warning: Seed file not found: {SEED_SQL_FILE}")
            print("  Skipping seed data step...")
        else:
            with open(SEED_SQL_FILE, 'r', encoding='utf-8') as f:
                seed_content = f.read()
            
            execute_sql_statements(cursor, seed_content, "Seed Data")
            connection.commit()
            print("  [OK] Seed data loaded successfully")
        
        print("\n" + "=" * 60)
        print("Database setup completed successfully!")
        print("=" * 60)
        print(f"Database: {DB_NAME}")
        print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"Connection string: mysql+pymysql://{DB_CONFIG['user']}:***@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_NAME}")
        
    except pymysql.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        if connection:
            connection.rollback()
        raise
    except FileNotFoundError as e:
        print(f"\n[ERROR] File error: {e}")
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

