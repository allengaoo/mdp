"""
V3 Test Data Import Script
Run: python import_v3_data.py
"""
import pymysql
import sys
from datetime import datetime

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology_meta_new',
    'charset': 'utf8mb4'
}

def execute_sql(cursor, sql, description=""):
    """Execute SQL and print result"""
    try:
        cursor.execute(sql)
        if description:
            print(f"[OK] {description}")
        return True
    except Exception as e:
        print(f"[FAIL] {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("MDP Platform V3 架构测试数据导入")
    print("=" * 60)
    print(f"目标数据库: {DB_CONFIG['database']}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # ============================================================
        # 第0步：清理现有测试数据
        # ============================================================
        print("\n[1/8] 清理现有测试数据...")
        
        execute_sql(cursor, "DELETE FROM ctx_project_object_binding WHERE project_id LIKE 'proj-%'", "清理项目绑定")
        execute_sql(cursor, "DELETE FROM rel_object_ver_property WHERE object_ver_id LIKE 'ver-ot-%'", "清理属性绑定")
        execute_sql(cursor, "DELETE FROM rel_link_ver_property WHERE link_ver_id LIKE 'ver-lt-%'", "清理链接属性绑定")
        execute_sql(cursor, "DELETE FROM meta_object_type_ver WHERE id LIKE 'ver-ot-%'", "清理对象类型版本")
        execute_sql(cursor, "DELETE FROM meta_link_type_ver WHERE id LIKE 'ver-lt-%'", "清理链接类型版本")
        execute_sql(cursor, "DELETE FROM meta_object_type_def WHERE id LIKE 'ot-%'", "清理对象类型定义")
        execute_sql(cursor, "DELETE FROM meta_link_type_def WHERE id LIKE 'lt-%'", "清理链接类型定义")
        execute_sql(cursor, "DELETE FROM meta_shared_property_def WHERE id LIKE 'prop-%'", "清理共享属性")
        execute_sql(cursor, "DELETE FROM sys_project WHERE id LIKE 'proj-%'", "清理项目")
        
        conn.commit()
        
        # ============================================================
        # 第1步：插入项目数据
        # ============================================================
        print("\n[2/8] 插入项目数据 (sys_project)...")
        
        projects = [
            ('proj-001', '战场态势感知系统', '基于本体的战场态势感知与决策支持系统，支持多源情报融合与行动方案规划'),
            ('proj-002', '智能供应链管理', '供应链全流程本体建模与优化系统，支持多式联运路径优化'),
            ('proj-003', '医疗知识图谱', '医疗领域知识图谱构建与推理系统，支持用药安全校验'),
        ]
        
        for pid, name, desc in projects:
            cursor.execute(
                "INSERT INTO sys_project (id, name, description, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
                (pid, name, desc)
            )
            print(f"  [OK] {name}")
        
        conn.commit()
        
        # ============================================================
        # 第2步：插入共享属性定义
        # ============================================================
        print("\n[3/8] 插入共享属性定义 (meta_shared_property_def)...")
        
        properties = [
            # 通用属性
            ('prop-name', 'name', '名称', 'STRING', '通用名称属性'),
            ('prop-desc', 'description', '描述', 'STRING', '详细描述'),
            ('prop-status', 'status', '状态', 'STRING', '运行状态'),
            ('prop-type', 'type', '类型', 'STRING', '分类类型'),
            ('prop-position', 'position', '位置', 'GEO_POINT', '地理坐标'),
            ('prop-location', 'location', '地点', 'STRING', '位置描述'),
            ('prop-int-value', 'int_value', '整数值', 'INT', '通用整数'),
            ('prop-double-value', 'double_value', '浮点值', 'DOUBLE', '通用浮点数'),
            ('prop-bool-value', 'bool_value', '布尔值', 'BOOLEAN', '是/否标志'),
            # 战场态势专用
            ('prop-callsign', 'callsign', '呼号', 'STRING', '无线电呼号'),
            ('prop-model', 'model', '型号', 'STRING', '装备型号'),
            ('prop-fuel', 'fuel', '燃油(%)', 'INT', '燃油百分比'),
            ('prop-threat-level', 'threat_level', '威胁等级', 'INT', '1-5级威胁'),
            ('prop-is-destroyed', 'is_destroyed', '已摧毁', 'BOOLEAN', '目标是否被摧毁'),
            ('prop-priority', 'priority', '优先级', 'INT', '任务优先级'),
            ('prop-start-time', 'start_time', '开始时间', 'DATETIME', '计划开始时间'),
            ('prop-confidence', 'confidence', '置信度(%)', 'INT', '情报置信度'),
            ('prop-source', 'source', '来源', 'STRING', '情报来源'),
            ('prop-content', 'content', '内容', 'STRING', '内容摘要'),
            ('prop-timestamp', 'timestamp', '时间戳', 'DATETIME', '数据获取时间'),
            ('prop-platform', 'platform', '平台', 'STRING', '采集平台'),
            ('prop-url', 'url', '链接', 'STRING', 'URL地址'),
            ('prop-resolution', 'resolution', '分辨率', 'STRING', '图像分辨率'),
            ('prop-risk-level', 'risk_level', '风险等级', 'STRING', '风险评估'),
            ('prop-estimated-cost', 'estimated_cost', '预估成本', 'INT', '成本估算'),
            # 供应链专用
            ('prop-capacity', 'capacity', '容量', 'INT', '存储/处理容量'),
            ('prop-utilization', 'utilization', '利用率', 'DOUBLE', '使用率百分比'),
            ('prop-sku', 'sku', 'SKU', 'STRING', '库存单位编号'),
            ('prop-quantity', 'quantity', '数量', 'INT', '库存数量'),
            ('prop-unit-price', 'unit_price', '单价', 'DOUBLE', '商品单价'),
            ('prop-handling-capacity', 'handling_capacity', '吞吐能力', 'INT', 'TEU吞吐量'),
            ('prop-output-daily', 'output_daily', '日产量', 'INT', '每日产出'),
            # 医疗专用
            ('prop-icd-code', 'icd_code', 'ICD编码', 'STRING', '国际疾病分类编码'),
            ('prop-category', 'category', '分类', 'STRING', '疾病/药物分类'),
            ('prop-severity', 'severity', '严重程度', 'STRING', '病情严重程度'),
            ('prop-body-part', 'body_part', '部位', 'STRING', '身体部位'),
            ('prop-age', 'age', '年龄', 'INT', '患者年龄'),
            ('prop-gender', 'gender', '性别', 'STRING', '性别'),
            ('prop-drug-class', 'drug_class', '药物类别', 'STRING', '药理分类'),
            ('prop-dosage', 'dosage', '剂量', 'STRING', '用药剂量'),
        ]
        
        for prop in properties:
            cursor.execute(
                "INSERT INTO meta_shared_property_def (id, api_name, display_name, data_type, description, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                prop
            )
        print(f"  [OK] 已插入 {len(properties)} 个共享属性")
        
        conn.commit()
        
        # ============================================================
        # 第3步：插入对象类型定义
        # ============================================================
        print("\n[4/8] 插入对象类型定义 (meta_object_type_def)...")
        
        object_types = [
            # 战场态势
            ('ot-fighter', 'fighter', 'ENTITY'),
            ('ot-target', 'target', 'ENTITY'),
            ('ot-mission', 'mission', 'EVENT'),
            ('ot-intel', 'intel_report', 'DOCUMENT'),
            ('ot-image', 'surveillance_image', 'MEDIA'),
            ('ot-coa', 'course_of_action', 'ENTITY'),
            # 供应链
            ('ot-warehouse', 'warehouse', 'ENTITY'),
            ('ot-product', 'product', 'ENTITY'),
            ('ot-rail-station', 'rail_station', 'ENTITY'),
            ('ot-factory', 'factory', 'ENTITY'),
            # 医疗
            ('ot-disease', 'disease', 'ENTITY'),
            ('ot-symptom', 'symptom', 'ENTITY'),
            ('ot-patient', 'patient', 'ENTITY'),
            ('ot-drug', 'drug', 'ENTITY'),
        ]
        
        for ot in object_types:
            cursor.execute(
                "INSERT INTO meta_object_type_def (id, api_name, stereotype, created_at) VALUES (%s, %s, %s, NOW())",
                ot
            )
        print(f"  [OK] 已插入 {len(object_types)} 个对象类型定义")
        
        conn.commit()
        
        # ============================================================
        # 第4步：插入对象类型版本
        # ============================================================
        print("\n[5/8] 插入对象类型版本 (meta_object_type_ver)...")
        
        object_versions = [
            ('ver-ot-fighter', 'ot-fighter', '1.0', '战斗机', '空中作战单元', 'PUBLISHED'),
            ('ver-ot-target', 'ot-target', '1.0', '目标', '打击目标', 'PUBLISHED'),
            ('ver-ot-mission', 'ot-mission', '1.0', '任务', '作战任务', 'PUBLISHED'),
            ('ver-ot-intel', 'ot-intel', '1.0', '情报报告', '来自SIGINT/ELINT的原始情报', 'PUBLISHED'),
            ('ver-ot-image', 'ot-image', '1.0', '侦察图像', 'IMINT图像数据', 'PUBLISHED'),
            ('ver-ot-coa', 'ot-coa', '1.0', '行动方案', '针对目标的应对计划', 'PUBLISHED'),
            ('ver-ot-warehouse', 'ot-warehouse', '1.0', '仓库', '存储设施', 'PUBLISHED'),
            ('ver-ot-product', 'ot-product', '1.0', '产品', '库存产品', 'PUBLISHED'),
            ('ver-ot-rail-station', 'ot-rail-station', '1.0', '铁路货运站', '铁路物流节点', 'PUBLISHED'),
            ('ver-ot-factory', 'ot-factory', '1.0', '制造工厂', '生产源头', 'PUBLISHED'),
            ('ver-ot-disease', 'ot-disease', '1.0', '疾病', '疾病实体', 'PUBLISHED'),
            ('ver-ot-symptom', 'ot-symptom', '1.0', '症状', '症状表现', 'PUBLISHED'),
            ('ver-ot-patient', 'ot-patient', '1.0', '患者', '就诊人员', 'PUBLISHED'),
            ('ver-ot-drug', 'ot-drug', '1.0', '药物', '治疗药品', 'PUBLISHED'),
        ]
        
        for ver in object_versions:
            cursor.execute(
                "INSERT INTO meta_object_type_ver (id, def_id, version_number, display_name, description, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                ver
            )
        
        # 更新 current_version_id
        for ver in object_versions:
            cursor.execute(
                "UPDATE meta_object_type_def SET current_version_id = %s WHERE id = %s",
                (ver[0], ver[1])
            )
        
        print(f"  [OK] 已插入 {len(object_versions)} 个对象类型版本")
        
        conn.commit()
        
        # ============================================================
        # 第5步：插入对象版本-属性绑定
        # ============================================================
        print("\n[6/8] 插入属性绑定 (rel_object_ver_property)...")
        
        property_bindings = [
            # 战斗机属性
            ('ver-ot-fighter', 'prop-callsign', False, True, True),
            ('ver-ot-fighter', 'prop-model', False, True, False),
            ('ver-ot-fighter', 'prop-fuel', False, True, False),
            ('ver-ot-fighter', 'prop-status', False, True, False),
            ('ver-ot-fighter', 'prop-position', False, False, False),
            # 目标属性
            ('ver-ot-target', 'prop-name', False, True, True),
            ('ver-ot-target', 'prop-type', False, True, False),
            ('ver-ot-target', 'prop-threat-level', False, True, False),
            ('ver-ot-target', 'prop-position', False, False, False),
            ('ver-ot-target', 'prop-is-destroyed', False, False, False),
            # 任务属性
            ('ver-ot-mission', 'prop-name', False, True, True),
            ('ver-ot-mission', 'prop-type', False, True, False),
            ('ver-ot-mission', 'prop-priority', False, True, False),
            ('ver-ot-mission', 'prop-status', False, True, False),
            ('ver-ot-mission', 'prop-start-time', False, False, False),
            # 情报报告属性
            ('ver-ot-intel', 'prop-source', False, True, False),
            ('ver-ot-intel', 'prop-confidence', False, True, False),
            ('ver-ot-intel', 'prop-content', False, True, True),
            ('ver-ot-intel', 'prop-timestamp', False, False, False),
            # 侦察图像属性
            ('ver-ot-image', 'prop-platform', False, True, False),
            ('ver-ot-image', 'prop-url', False, True, True),
            ('ver-ot-image', 'prop-resolution', False, False, False),
            # 行动方案属性
            ('ver-ot-coa', 'prop-name', False, True, True),
            ('ver-ot-coa', 'prop-type', False, True, False),
            ('ver-ot-coa', 'prop-risk-level', False, True, False),
            ('ver-ot-coa', 'prop-estimated-cost', False, False, False),
            # 仓库属性
            ('ver-ot-warehouse', 'prop-name', False, True, True),
            ('ver-ot-warehouse', 'prop-location', False, True, False),
            ('ver-ot-warehouse', 'prop-capacity', False, True, False),
            ('ver-ot-warehouse', 'prop-utilization', False, False, False),
            # 产品属性
            ('ver-ot-product', 'prop-sku', False, True, False),
            ('ver-ot-product', 'prop-name', False, True, True),
            ('ver-ot-product', 'prop-quantity', False, True, False),
            ('ver-ot-product', 'prop-unit-price', False, False, False),
            # 铁路货运站属性
            ('ver-ot-rail-station', 'prop-name', False, True, True),
            ('ver-ot-rail-station', 'prop-handling-capacity', False, True, False),
            ('ver-ot-rail-station', 'prop-position', False, False, False),
            # 制造工厂属性
            ('ver-ot-factory', 'prop-name', False, True, True),
            ('ver-ot-factory', 'prop-output-daily', False, True, False),
            # 疾病属性
            ('ver-ot-disease', 'prop-name', False, True, True),
            ('ver-ot-disease', 'prop-icd-code', False, True, False),
            ('ver-ot-disease', 'prop-category', False, True, False),
            ('ver-ot-disease', 'prop-desc', False, False, False),
            # 症状属性
            ('ver-ot-symptom', 'prop-name', False, True, True),
            ('ver-ot-symptom', 'prop-severity', False, True, False),
            ('ver-ot-symptom', 'prop-body-part', False, False, False),
            # 患者属性
            ('ver-ot-patient', 'prop-name', False, True, True),
            ('ver-ot-patient', 'prop-age', False, True, False),
            ('ver-ot-patient', 'prop-gender', False, True, False),
            # 药物属性
            ('ver-ot-drug', 'prop-name', False, True, True),
            ('ver-ot-drug', 'prop-drug-class', False, True, False),
            ('ver-ot-drug', 'prop-dosage', False, True, False),
        ]
        
        for binding in property_bindings:
            cursor.execute(
                "INSERT INTO rel_object_ver_property (object_ver_id, property_def_id, is_primary_key, is_required, is_title) VALUES (%s, %s, %s, %s, %s)",
                binding
            )
        print(f"  [OK] 已插入 {len(property_bindings)} 个属性绑定")
        
        conn.commit()
        
        # ============================================================
        # 第6步：插入链接类型定义
        # ============================================================
        print("\n[7/8] 插入链接类型 (meta_link_type_def + meta_link_type_ver)...")
        
        link_types = [
            ('lt-assigned-to', 'assigned_to'),
            ('lt-targets', 'targets'),
            ('lt-escorts', 'escorts'),
            ('lt-corroborates', 'corroborates'),
            ('lt-depicts', 'depicts'),
            ('lt-plan-target', 'plans_against'),
            ('lt-stored-in', 'stored_in'),
            ('lt-road-link', 'road_connection'),
            ('lt-road-feeder', 'road_feeder'),
            ('lt-rail-link', 'rail_connection'),
            ('lt-last-mile', 'last_mile'),
            ('lt-has-symptom', 'has_symptom'),
            ('lt-diagnosed-with', 'diagnosed_with'),
            ('lt-treats', 'treats'),
            ('lt-contra', 'contraindication'),
        ]
        
        for lt in link_types:
            cursor.execute(
                "INSERT INTO meta_link_type_def (id, api_name, created_at) VALUES (%s, %s, NOW())",
                lt
            )
        
        link_versions = [
            ('ver-lt-assigned-to', 'lt-assigned-to', '1.0', '分配到', 'ot-fighter', 'ot-mission', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-targets', 'lt-targets', '1.0', '打击目标', 'ot-mission', 'ot-target', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-escorts', 'lt-escorts', '1.0', '护航', 'ot-fighter', 'ot-fighter', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-corroborates', 'lt-corroborates', '1.0', '佐证', 'ot-intel', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED'),
            ('ver-lt-depicts', 'lt-depicts', '1.0', '描绘', 'ot-image', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED'),
            ('ver-lt-plan-target', 'lt-plan-target', '1.0', '针对', 'ot-coa', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED'),
            ('ver-lt-stored-in', 'lt-stored-in', '1.0', '存储于', 'ot-product', 'ot-warehouse', 'MANY_TO_ONE', 'PUBLISHED'),
            ('ver-lt-road-link', 'lt-road-link', '1.0', '公路运输线', 'ot-factory', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-road-feeder', 'lt-road-feeder', '1.0', '短驳运输', 'ot-factory', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-rail-link', 'lt-rail-link', '1.0', '铁路干线', 'ot-rail-station', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-last-mile', 'lt-last-mile', '1.0', '最后一公里', 'ot-rail-station', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-has-symptom', 'lt-has-symptom', '1.0', '伴有症状', 'ot-disease', 'ot-symptom', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-diagnosed-with', 'lt-diagnosed-with', '1.0', '确诊', 'ot-patient', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-treats', 'lt-treats', '1.0', '治疗', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED'),
            ('ver-lt-contra', 'lt-contra', '1.0', '禁忌', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED'),
        ]
        
        for ver in link_versions:
            cursor.execute(
                "INSERT INTO meta_link_type_ver (id, def_id, version_number, display_name, source_object_def_id, target_object_def_id, cardinality, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                ver
            )
            cursor.execute(
                "UPDATE meta_link_type_def SET current_version_id = %s WHERE id = %s",
                (ver[0], ver[1])
            )
        
        print(f"  [OK] 已插入 {len(link_types)} 个链接类型定义和版本")
        
        conn.commit()
        
        # ============================================================
        # 第7步：插入项目-对象类型绑定
        # ============================================================
        print("\n[8/8] 插入项目绑定 (ctx_project_object_binding)...")
        
        bindings = [
            # 战场态势感知系统
            ('proj-001', 'ot-fighter', 'ver-ot-fighter', '战斗机', True),
            ('proj-001', 'ot-target', 'ver-ot-target', '打击目标', True),
            ('proj-001', 'ot-mission', 'ver-ot-mission', '作战任务', True),
            ('proj-001', 'ot-intel', 'ver-ot-intel', '情报报告', True),
            ('proj-001', 'ot-image', 'ver-ot-image', '侦察图像', True),
            ('proj-001', 'ot-coa', 'ver-ot-coa', '行动方案', True),
            # 智能供应链管理
            ('proj-002', 'ot-warehouse', 'ver-ot-warehouse', '配送中心', True),
            ('proj-002', 'ot-product', 'ver-ot-product', '库存产品', True),
            ('proj-002', 'ot-rail-station', 'ver-ot-rail-station', '铁路站点', True),
            ('proj-002', 'ot-factory', 'ver-ot-factory', '生产工厂', True),
            # 医疗知识图谱
            ('proj-003', 'ot-disease', 'ver-ot-disease', '疾病', True),
            ('proj-003', 'ot-symptom', 'ver-ot-symptom', '症状', True),
            ('proj-003', 'ot-patient', 'ver-ot-patient', '患者', True),
            ('proj-003', 'ot-drug', 'ver-ot-drug', '药物', True),
        ]
        
        for binding in bindings:
            cursor.execute(
                "INSERT INTO ctx_project_object_binding (project_id, object_def_id, used_version_id, project_display_alias, is_visible) VALUES (%s, %s, %s, %s, %s)",
                binding
            )
        print(f"  [OK] 已插入 {len(bindings)} 个项目绑定")
        
        conn.commit()
        
        # 启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # ============================================================
        # 验证数据
        # ============================================================
        print("\n" + "=" * 60)
        print("数据导入验证")
        print("=" * 60)
        
        verifications = [
            ("sys_project", "项目"),
            ("meta_shared_property_def", "共享属性"),
            ("meta_object_type_def", "对象类型定义"),
            ("meta_object_type_ver", "对象类型版本"),
            ("rel_object_ver_property", "属性绑定"),
            ("meta_link_type_def", "链接类型定义"),
            ("meta_link_type_ver", "链接类型版本"),
            ("ctx_project_object_binding", "项目绑定"),
        ]
        
        for table, label in verifications:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {label}: {count} 条记录")
        
        print("\n" + "=" * 60)
        print("[OK] V3 测试数据导入完成！")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n[FAIL] 导入失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
