"""
Run seed_function_test_examples.sql to add test functions for function execution verification.
Usage: python run_seed_function_test_examples.py (from backend dir, with venv)
"""
import os
import re
import pymysql
from dotenv import load_dotenv

load_dotenv()


def parse_database_url(url: str) -> dict:
    pattern = r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, url)
    if match:
        return {
            "user": match.group(1),
            "password": match.group(2),
            "host": match.group(3),
            "port": int(match.group(4)),
            "database": match.group(5),
            "charset": "utf8mb4",
        }
    raise ValueError(f"Invalid DATABASE_URL format: {url}")


def run_seed():
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/ontology_meta_new")
    db_config = parse_database_url(database_url)
    sql_file = os.path.join(os.path.dirname(__file__), "seed_function_test_examples.sql")

    if not os.path.exists(sql_file):
        print(f"ERROR: SQL file not found: {sql_file}")
        return False

    print("=" * 60)
    print("Seed Function Test Examples")
    print("=" * 60)

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split by statement end (line ending with ;)
        statements = []
        current = []
        for line in sql_content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            current.append(line)
            if stripped.endswith(";"):
                statements.append("\n".join(current))
                current = []

        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
                conn.commit()
                print(f"  [{i}] INSERT: OK")
            except Exception as e:
                if "Duplicate entry" in str(e):
                    print(f"  [{i}] Skipped (already exists)")
                    conn.rollback()
                else:
                    print(f"  [{i}] ERROR: {e}")
                    conn.rollback()

        cursor.execute(
            "SELECT id, api_name, display_name FROM meta_function_def WHERE id LIKE 'fn_test_%'"
        )
        rows = cursor.fetchall()
        print("\nTest functions:")
        for r in rows:
            print(f"  - {r[2]} ({r[1]})")

        cursor.close()
        conn.close()
        print("\nDone.")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    run_seed()
