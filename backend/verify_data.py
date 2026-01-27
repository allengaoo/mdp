import pymysql
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='localhost', 
    user='root', 
    password='Ga0binGB', 
    database='ontology_meta_new', 
    charset='utf8mb4'
)
cur = conn.cursor()

print("=== 项目数据 (sys_project) ===")
cur.execute("SELECT id, name FROM sys_project WHERE id LIKE 'proj-%'")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\n=== 对象类型统计 ===")
cur.execute("""
    SELECT p.name, COUNT(b.object_def_id) as count
    FROM sys_project p 
    LEFT JOIN ctx_project_object_binding b ON p.id = b.project_id
    WHERE p.id LIKE 'proj-%'
    GROUP BY p.id, p.name
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} 个对象类型")

print("\n=== 对象类型详情 ===")
cur.execute("""
    SELECT d.api_name, v.display_name, d.stereotype 
    FROM meta_object_type_def d
    JOIN meta_object_type_ver v ON d.current_version_id = v.id
    WHERE d.id LIKE 'ot-%'
    ORDER BY d.api_name
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} ({r[2]})")

conn.close()
