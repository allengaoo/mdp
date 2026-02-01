#!/usr/bin/env python3
"""
诊断脚本：检查 meta_function_def 表中函数的 project_id 分布。
用于分析本体场景库函数列表为空的问题。
"""
import os
import pymysql

# 从环境变量或默认值获取连接
db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology_meta_new"
)

def parse_db_url(url):
    """mysql+pymysql://user:pass@host:port/database -> dict"""
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

print("=" * 60)
print("meta_function_def 诊断报告")
print("=" * 60)

# 1. 项目列表
cur.execute("SELECT id, name FROM meta_project WHERE id LIKE 'proj-%' OR id IS NOT NULL ORDER BY id LIMIT 20")
projects = cur.fetchall()
print("\n[1] 项目列表 (meta_project):")
for r in projects:
    print(f"  {r[0]}: {r[1]}")

# 2. 函数列表及 project_id
cur.execute("""
    SELECT id, api_name, display_name, project_id
    FROM meta_function_def
    ORDER BY api_name
""")
funcs = cur.fetchall()
print("\n[2] 函数列表及 project_id (meta_function_def):")
if not funcs:
    print("  (无记录)")
else:
    for r in funcs:
        pid = r[3] if r[3] else "(NULL)"
        print(f"  id={r[0]} api_name={r[1]} display_name={r[2]} project_id={pid}")

# 3. 按 project_id 统计
cur.execute("""
    SELECT project_id, COUNT(*) as cnt
    FROM meta_function_def
    GROUP BY project_id
""")
stats = cur.fetchall()
print("\n[3] 按 project_id 统计:")
for r in stats:
    pid = r[0] if r[0] else "(NULL)"
    print(f"  project_id={pid}: {r[1]} 个函数")

# 4. 结论
print("\n" + "=" * 60)
print("分析结论:")
print("=" * 60)
null_count = sum(r[1] for r in stats if r[0] is None)
if null_count > 0:
    print(f"  - 共有 {null_count} 个函数的 project_id 为 NULL (全局函数)")
    print("  - 本体管理 (OMA) 调用 GET /functions 无 project_id -> 返回全部函数")
    print("  - 本体场景库 (Studio) 调用 GET /functions?project_id=proj-xxx -> 只返回 project_id 匹配的函数")
    print("  - project_id 为 NULL 的函数不会出现在项目级函数列表中")
    print("\n  建议修复: 将需在项目中展示的函数更新 project_id，例如:")
    print("    UPDATE meta_function_def SET project_id = 'proj-integration-test-001'")
    print("    WHERE project_id IS NULL;")
else:
    print("  - 所有函数均有 project_id，请检查 project_id 是否与目标项目一致")

conn.close()
