#!/usr/bin/env python3
"""
修复脚本：将 meta_function_def 中 project_id 为 NULL 的函数
更新为指定项目（默认 proj-integration-test-001），
使其在本体场景库的函数列表中可见。

用法: python fix_function_project.py [project_id]
建议在虚拟环境中运行: .venv\\Scripts\\python.exe fix_function_project.py
"""
import os
import sys
import pymysql

DEFAULT_PROJECT_ID = "proj-integration-test-001"

db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology_meta_new"
)


def parse_db_url(url):
    if "://" in url:
        url = url.split("://", 1)[1]
    user_pass, rest = url.split("@", 1)
    user, password = user_pass.split(":", 1)
    host_port, database = rest.split("/", 1)
    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 3306
    return {"host": host, "port": port, "user": user, "password": password, "database": database}


def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROJECT_ID

    cfg = parse_db_url(db_url)
    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
    )

    cur = conn.cursor()

    # 校验项目存在
    cur.execute("SELECT id FROM meta_project WHERE id = %s", (project_id,))
    if not cur.fetchone():
        print(f"Error: Project '{project_id}' not found in meta_project.")
        conn.close()
        sys.exit(1)

    # 更新 project_id 为 NULL 的函数
    cur.execute(
        "UPDATE meta_function_def SET project_id = %s WHERE project_id IS NULL",
        (project_id,)
    )
    updated = cur.rowcount
    conn.commit()
    conn.close()

    print(f"Fixed: Updated {updated} function(s) with project_id = '{project_id}'")
    if updated > 0:
        print("Ontology scenario library (Studio) function list should now show these functions.")


if __name__ == "__main__":
    main()
