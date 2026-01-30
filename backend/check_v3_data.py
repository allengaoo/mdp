"""检查并修复V3数据"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology_meta_new',
    'charset': 'utf8mb4'
}

def check_and_fix():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=== 检查数据状态 ===\n")
    
    # 检查各表数据量
    tables = [
        'sys_project',
        'meta_shared_property_def', 
        'meta_object_type_def',
        'meta_object_type_ver',
        'rel_object_ver_property',
        'meta_link_type_def',
        'meta_link_type_ver',
        'ctx_project_object_binding'
    ]
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} rows')
    
    print("\n=== 项目列表 ===")
    cursor.execute('SELECT id, name FROM sys_project')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    print("\n=== 共享属性列表 (前10条) ===")
    cursor.execute('SELECT id, api_name, data_type FROM meta_shared_property_def LIMIT 10')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} ({row[2]})')
    
    # 检查是否需要插入共享属性
    cursor.execute("SELECT COUNT(*) FROM meta_shared_property_def WHERE id LIKE 'sp-%'")
    sp_count = cursor.fetchone()[0]
    
    if sp_count == 0:
        print("\n=== 正在插入共享属性... ===")
        
        properties = [
            ('sp-name', 'name', '名称', 'STRING', '通用名称字段'),
            ('sp-desc', 'description', '描述', 'STRING', '描述信息'),
            ('sp-status', 'status', '状态', 'STRING', '状态字段'),
            ('sp-type', 'type', '类型', 'STRING', '分类类型'),
            ('sp-position', 'position', '位置', 'GEO_POINT', '地理位置坐标'),
            ('sp-created-at', 'created_at', '创建时间', 'DATETIME', '创建时间戳'),
            ('sp-callsign', 'callsign', '呼号', 'STRING', '战斗单元呼号'),
            ('sp-model', 'model', '机型', 'STRING', '飞机型号'),
            ('sp-fuel', 'fuel', '燃油(%)', 'INT', '燃油百分比'),
            ('sp-threat-level', 'threat_level', '威胁等级', 'INT', '1-5级威胁评估'),
            ('sp-is-destroyed', 'is_destroyed', '已摧毁', 'BOOLEAN', '是否已摧毁'),
            ('sp-priority', 'priority', '优先级', 'INT', '任务优先级'),
            ('sp-start-time', 'start_time', '开始时间', 'DATETIME', '任务开始时间'),
            ('sp-source', 'source', '来源', 'STRING', '情报来源'),
            ('sp-confidence', 'confidence', '置信度', 'INT', '情报置信度百分比'),
            ('sp-content', 'content', '内容', 'STRING', '内容摘要'),
            ('sp-timestamp', 'timestamp', '获取时间', 'DATETIME', '情报获取时间'),
            ('sp-platform', 'platform', '平台', 'STRING', '拍摄/采集平台'),
            ('sp-url', 'url', '链接', 'STRING', '资源URL'),
            ('sp-resolution', 'resolution', '分辨率', 'STRING', '图像分辨率'),
            ('sp-risk-level', 'risk_level', '风险等级', 'STRING', '方案风险等级'),
            ('sp-estimated-cost', 'estimated_cost', '预估成本', 'INT', '方案预估成本'),
            ('sp-location', 'location', '位置', 'STRING', '地点名称'),
            ('sp-capacity', 'capacity', '容量', 'INT', '存储/处理容量'),
            ('sp-utilization', 'utilization', '利用率', 'DOUBLE', '容量利用率'),
            ('sp-sku', 'sku', 'SKU', 'STRING', '库存单位编码'),
            ('sp-quantity', 'quantity', '数量', 'INT', '库存数量'),
            ('sp-unit-price', 'unit_price', '单价', 'DOUBLE', '商品单价'),
            ('sp-handling-capacity', 'handling_capacity', '吞吐能力', 'INT', '货运站吞吐能力(TEU)'),
            ('sp-output-daily', 'output_daily', '日产量', 'INT', '工厂日产量'),
            ('sp-icd-code', 'icd_code', 'ICD编码', 'STRING', '国际疾病分类编码'),
            ('sp-category', 'category', '分类', 'STRING', '疾病分类'),
            ('sp-severity', 'severity', '严重程度', 'STRING', '病情严重程度'),
            ('sp-body-part', 'body_part', '部位', 'STRING', '身体部位'),
            ('sp-age', 'age', '年龄', 'INT', '患者年龄'),
            ('sp-gender', 'gender', '性别', 'STRING', '患者性别'),
            ('sp-drug-class', 'drug_class', '药物类别', 'STRING', '药物分类'),
            ('sp-dosage', 'dosage', '规格', 'STRING', '药物规格'),
        ]
        
        insert_sql = '''INSERT INTO meta_shared_property_def 
            (id, api_name, display_name, data_type, description, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())'''
        
        for prop in properties:
            try:
                cursor.execute(insert_sql, prop)
            except pymysql.IntegrityError as e:
                if 'Duplicate' in str(e):
                    print(f'  [SKIP] {prop[0]} already exists')
                else:
                    print(f'  [ERROR] {prop[0]}: {e}')
        
        conn.commit()
        print(f"  插入了 {len(properties)} 条共享属性")
    
    # 清理旧的测试数据
    print("\n=== 清理旧测试数据 ===")
    cursor.execute("DELETE FROM sys_project WHERE name = '' OR id NOT LIKE 'proj-%'")
    deleted = cursor.rowcount
    conn.commit()
    print(f"  删除了 {deleted} 条旧项目数据")
    
    print("\n=== 最终数据状态 ===")
    cursor.execute('SELECT id, name FROM sys_project ORDER BY id')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_and_fix()
