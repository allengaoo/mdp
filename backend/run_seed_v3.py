"""
执行 seed_v3.sql 脚本导入测试数据到 V3 架构
"""
import pymysql
from pathlib import Path

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology_meta_new',
    'charset': 'utf8mb4'
}

def execute_sql_file(filepath: str):
    """执行SQL文件"""
    sql_content = Path(filepath).read_text(encoding='utf-8')
    
    # 分割SQL语句（按分号分割，但要处理字符串中的分号）
    statements = []
    current_stmt = []
    in_string = False
    string_char = None
    
    for line in sql_content.split('\n'):
        # 跳过注释行
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('#'):
            continue
        if not stripped:
            continue
            
        current_stmt.append(line)
        
        # 简单分割：遇到分号结束语句
        if ';' in line and not stripped.startswith('--'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_stmt = []
    
    # 添加最后一个语句（如果有）
    if current_stmt:
        stmt = '\n'.join(current_stmt).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
    
    # 连接数据库并执行
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        for i, stmt in enumerate(statements):
            # 跳过空语句
            if not stmt.strip() or stmt.strip() == ';':
                continue
            
            # 跳过纯注释语句
            if stmt.strip().startswith('--') or stmt.strip().startswith('/*'):
                continue
                
            try:
                cursor.execute(stmt)
                conn.commit()
                success_count += 1
                
                # 如果是SELECT语句，显示结果
                if stmt.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        # 获取列名
                        columns = [desc[0] for desc in cursor.description]
                        print(f"\n{' | '.join(columns)}")
                        print('-' * 60)
                        for row in results:
                            print(' | '.join(str(v) for v in row))
                            
            except pymysql.Error as e:
                error_count += 1
                error_msg = str(e)
                # 忽略一些预期的错误
                if 'Unknown table' in error_msg or 'doesn\'t exist' in error_msg:
                    print(f"[SKIP] 表不存在: {stmt[:50]}...")
                elif 'Duplicate entry' in error_msg:
                    print(f"[SKIP] 数据已存在: {stmt[:50]}...")
                else:
                    print(f"[ERROR] 执行失败: {error_msg}")
                    print(f"  语句: {stmt[:100]}...")
    finally:
        cursor.close()
        conn.close()
    
    print(f"\n==============================")
    print(f"执行完成: 成功 {success_count} 条, 错误 {error_count} 条")
    print(f"==============================")

if __name__ == '__main__':
    sql_file = Path(__file__).parent / 'seed_v3.sql'
    print(f"执行SQL文件: {sql_file}")
    print("=" * 60)
    execute_sql_file(str(sql_file))
