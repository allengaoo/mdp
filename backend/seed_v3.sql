-- ============================================================
-- MDP Platform V3 架构测试数据导入脚本
-- 数据库: ontology_meta_new (MySQL)
-- ============================================================

-- 禁用外键检查（导入时）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 清理现有测试数据
-- ============================================================

-- 清理绑定关系表
DELETE FROM ctx_project_object_binding WHERE project_id LIKE 'proj-%';
DELETE FROM rel_object_ver_property WHERE object_ver_id LIKE 'ver-ot-%';
DELETE FROM rel_link_ver_property WHERE link_ver_id LIKE 'ver-lt-%';

-- 清理版本表
DELETE FROM meta_object_type_ver WHERE id LIKE 'ver-ot-%';
DELETE FROM meta_link_type_ver WHERE id LIKE 'ver-lt-%';

-- 清理定义表
DELETE FROM meta_object_type_def WHERE id LIKE 'ot-%';
DELETE FROM meta_link_type_def WHERE id LIKE 'lt-%';

-- 清理共享属性（保留以prop-开头的基础属性）
DELETE FROM meta_shared_property_def WHERE id LIKE 'sp-%';

-- 清理项目
DELETE FROM sys_project WHERE id LIKE 'proj-%';

-- ============================================================
-- 2. 项目数据 (sys_project)
-- ============================================================

INSERT INTO sys_project (id, name, description, created_at, updated_at) VALUES
('proj-001', '战场态势感知系统', '基于本体的战场态势感知与决策支持系统，支持多源情报融合与行动方案规划', NOW(), NOW()),
('proj-002', '智能供应链管理', '供应链全流程本体建模与优化系统，支持多式联运路径优化', NOW(), NOW()),
('proj-003', '医疗知识图谱', '医疗领域知识图谱构建与推理系统，支持用药安全校验', NOW(), NOW());

-- ============================================================
-- 3. 共享属性定义 (meta_shared_property_def)
-- ============================================================

INSERT INTO meta_shared_property_def (id, api_name, display_name, data_type, description, created_at) VALUES
-- 通用属性
('sp-name', 'name', '名称', 'STRING', '通用名称字段', NOW()),
('sp-desc', 'description', '描述', 'STRING', '描述信息', NOW()),
('sp-status', 'status', '状态', 'STRING', '状态字段', NOW()),
('sp-type', 'type', '类型', 'STRING', '分类类型', NOW()),
('sp-position', 'position', '位置', 'GEO_POINT', '地理位置坐标', NOW()),
('sp-created-at', 'created_at', '创建时间', 'DATETIME', '创建时间戳', NOW()),

-- 战场态势感知属性
('sp-callsign', 'callsign', '呼号', 'STRING', '战斗单元呼号', NOW()),
('sp-model', 'model', '机型', 'STRING', '飞机型号', NOW()),
('sp-fuel', 'fuel', '燃油(%)', 'INT', '燃油百分比', NOW()),
('sp-threat-level', 'threat_level', '威胁等级', 'INT', '1-5级威胁评估', NOW()),
('sp-is-destroyed', 'is_destroyed', '已摧毁', 'BOOLEAN', '是否已摧毁', NOW()),
('sp-priority', 'priority', '优先级', 'INT', '任务优先级', NOW()),
('sp-start-time', 'start_time', '开始时间', 'DATETIME', '任务开始时间', NOW()),
('sp-source', 'source', '来源', 'STRING', '情报来源', NOW()),
('sp-confidence', 'confidence', '置信度', 'INT', '情报置信度百分比', NOW()),
('sp-content', 'content', '内容', 'STRING', '内容摘要', NOW()),
('sp-timestamp', 'timestamp', '获取时间', 'DATETIME', '情报获取时间', NOW()),
('sp-platform', 'platform', '平台', 'STRING', '拍摄/采集平台', NOW()),
('sp-url', 'url', '链接', 'STRING', '资源URL', NOW()),
('sp-resolution', 'resolution', '分辨率', 'STRING', '图像分辨率', NOW()),
('sp-risk-level', 'risk_level', '风险等级', 'STRING', '方案风险等级', NOW()),
('sp-estimated-cost', 'estimated_cost', '预估成本', 'INT', '方案预估成本', NOW()),

-- 供应链属性
('sp-location', 'location', '位置', 'STRING', '地点名称', NOW()),
('sp-capacity', 'capacity', '容量', 'INT', '存储/处理容量', NOW()),
('sp-utilization', 'utilization', '利用率', 'DOUBLE', '容量利用率', NOW()),
('sp-sku', 'sku', 'SKU', 'STRING', '库存单位编码', NOW()),
('sp-quantity', 'quantity', '数量', 'INT', '库存数量', NOW()),
('sp-unit-price', 'unit_price', '单价', 'DOUBLE', '商品单价', NOW()),
('sp-handling-capacity', 'handling_capacity', '吞吐能力', 'INT', '货运站吞吐能力(TEU)', NOW()),
('sp-output-daily', 'output_daily', '日产量', 'INT', '工厂日产量', NOW()),

-- 医疗属性
('sp-icd-code', 'icd_code', 'ICD编码', 'STRING', '国际疾病分类编码', NOW()),
('sp-category', 'category', '分类', 'STRING', '疾病分类', NOW()),
('sp-severity', 'severity', '严重程度', 'STRING', '病情严重程度', NOW()),
('sp-body-part', 'body_part', '部位', 'STRING', '身体部位', NOW()),
('sp-age', 'age', '年龄', 'INT', '患者年龄', NOW()),
('sp-gender', 'gender', '性别', 'STRING', '患者性别', NOW()),
('sp-drug-class', 'drug_class', '药物类别', 'STRING', '药物分类', NOW()),
('sp-dosage', 'dosage', '规格', 'STRING', '药物规格', NOW());

-- ============================================================
-- 4. 对象类型定义 (meta_object_type_def)
-- ============================================================

INSERT INTO meta_object_type_def (id, api_name, stereotype, current_version_id, created_at) VALUES
-- 项目1：战场态势感知系统
('ot-fighter', 'fighter', 'ENTITY', 'ver-ot-fighter-v1', NOW()),
('ot-target', 'target', 'ENTITY', 'ver-ot-target-v1', NOW()),
('ot-mission', 'mission', 'EVENT', 'ver-ot-mission-v1', NOW()),
('ot-intel', 'intel_report', 'DOCUMENT', 'ver-ot-intel-v1', NOW()),
('ot-image', 'surveillance_image', 'MEDIA', 'ver-ot-image-v1', NOW()),
('ot-coa', 'course_of_action', 'DOCUMENT', 'ver-ot-coa-v1', NOW()),

-- 项目2：智能供应链管理
('ot-warehouse', 'warehouse', 'ENTITY', 'ver-ot-warehouse-v1', NOW()),
('ot-product', 'product', 'ENTITY', 'ver-ot-product-v1', NOW()),
('ot-rail-station', 'rail_station', 'ENTITY', 'ver-ot-rail-station-v1', NOW()),
('ot-factory', 'factory', 'ENTITY', 'ver-ot-factory-v1', NOW()),

-- 项目3：医疗知识图谱
('ot-disease', 'disease', 'ENTITY', 'ver-ot-disease-v1', NOW()),
('ot-symptom', 'symptom', 'ENTITY', 'ver-ot-symptom-v1', NOW()),
('ot-patient', 'patient', 'ENTITY', 'ver-ot-patient-v1', NOW()),
('ot-drug', 'drug', 'ENTITY', 'ver-ot-drug-v1', NOW());

-- ============================================================
-- 5. 对象类型版本 (meta_object_type_ver)
-- ============================================================

INSERT INTO meta_object_type_ver (id, def_id, version_number, display_name, description, icon, color, status, enable_global_search, enable_geo_index, enable_vector_index, cache_ttl_seconds, created_at) VALUES
-- 项目1：战场态势感知系统
('ver-ot-fighter-v1', 'ot-fighter', '1.0', '战斗机', '空中作战单元', 'fighter-jet', '#FF6B6B', 'PUBLISHED', true, true, false, 60, NOW()),
('ver-ot-target-v1', 'ot-target', '1.0', '目标', '打击目标', 'target', '#FFD93D', 'PUBLISHED', true, true, false, 30, NOW()),
('ver-ot-mission-v1', 'ot-mission', '1.0', '任务', '作战任务', 'mission', '#6BCB77', 'PUBLISHED', true, false, false, 120, NOW()),
('ver-ot-intel-v1', 'ot-intel', '1.0', '情报报告', '来自SIGINT/ELINT的原始情报', 'file-text', '#4D96FF', 'PUBLISHED', true, false, true, 300, NOW()),
('ver-ot-image-v1', 'ot-image', '1.0', '侦察图像', 'IMINT图像数据', 'image', '#9B59B6', 'PUBLISHED', true, true, true, 600, NOW()),
('ver-ot-coa-v1', 'ot-coa', '1.0', '行动方案', '针对目标的应对计划', 'file-document', '#E74C3C', 'PUBLISHED', true, false, false, 300, NOW()),

-- 项目2：智能供应链管理
('ver-ot-warehouse-v1', 'ot-warehouse', '1.0', '仓库', '存储设施', 'warehouse', '#3498DB', 'PUBLISHED', true, true, false, 300, NOW()),
('ver-ot-product-v1', 'ot-product', '1.0', '产品', '库存产品', 'box', '#2ECC71', 'PUBLISHED', true, false, false, 60, NOW()),
('ver-ot-rail-station-v1', 'ot-rail-station', '1.0', '铁路货运站', '铁路物流节点', 'train', '#9B59B6', 'PUBLISHED', true, true, false, 600, NOW()),
('ver-ot-factory-v1', 'ot-factory', '1.0', '制造工厂', '生产源头', 'factory', '#E67E22', 'PUBLISHED', true, true, false, 600, NOW()),

-- 项目3：医疗知识图谱
('ver-ot-disease-v1', 'ot-disease', '1.0', '疾病', '疾病实体', 'virus', '#E74C3C', 'PUBLISHED', true, false, true, 3600, NOW()),
('ver-ot-symptom-v1', 'ot-symptom', '1.0', '症状', '症状表现', 'heart-pulse', '#FF6B6B', 'PUBLISHED', true, false, false, 3600, NOW()),
('ver-ot-patient-v1', 'ot-patient', '1.0', '患者', '就诊人员', 'user', '#3498DB', 'PUBLISHED', false, false, false, 60, NOW()),
('ver-ot-drug-v1', 'ot-drug', '1.0', '药物', '治疗药品', 'pill', '#2ECC71', 'PUBLISHED', true, false, true, 3600, NOW());

-- ============================================================
-- 6. 对象版本属性绑定 (rel_object_ver_property)
-- ============================================================

INSERT INTO rel_object_ver_property (object_ver_id, property_def_id, local_api_name, is_primary_key, is_required, is_title, default_value, validation_rules) VALUES
-- 战斗机属性
('ver-ot-fighter-v1', 'sp-callsign', NULL, false, true, true, NULL, NULL),
('ver-ot-fighter-v1', 'sp-model', NULL, false, true, false, NULL, NULL),
('ver-ot-fighter-v1', 'sp-fuel', NULL, false, true, false, '100', '{"min": 0, "max": 100}'),
('ver-ot-fighter-v1', 'sp-status', NULL, false, true, false, 'Ready', '{"enum": ["Ready", "Active", "Maintenance", "Offline"]}'),
('ver-ot-fighter-v1', 'sp-position', NULL, false, false, false, NULL, NULL),

-- 目标属性
('ver-ot-target-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-target-v1', 'sp-type', NULL, false, true, false, NULL, NULL),
('ver-ot-target-v1', 'sp-threat-level', NULL, false, true, false, '1', '{"min": 1, "max": 5}'),
('ver-ot-target-v1', 'sp-position', NULL, false, false, false, NULL, NULL),
('ver-ot-target-v1', 'sp-is-destroyed', NULL, false, true, false, 'false', NULL),

-- 任务属性
('ver-ot-mission-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-mission-v1', 'sp-type', NULL, false, true, false, NULL, NULL),
('ver-ot-mission-v1', 'sp-priority', NULL, false, true, false, '1', '{"min": 1, "max": 5}'),
('ver-ot-mission-v1', 'sp-status', NULL, false, true, false, 'Planning', NULL),
('ver-ot-mission-v1', 'sp-start-time', NULL, false, false, false, NULL, NULL),

-- 情报报告属性
('ver-ot-intel-v1', 'sp-source', NULL, false, true, false, NULL, NULL),
('ver-ot-intel-v1', 'sp-confidence', NULL, false, true, false, '50', '{"min": 0, "max": 100}'),
('ver-ot-intel-v1', 'sp-content', NULL, false, true, true, NULL, NULL),
('ver-ot-intel-v1', 'sp-timestamp', NULL, false, true, false, NULL, NULL),

-- 侦察图像属性
('ver-ot-image-v1', 'sp-platform', NULL, false, true, false, NULL, NULL),
('ver-ot-image-v1', 'sp-url', NULL, false, true, true, NULL, NULL),
('ver-ot-image-v1', 'sp-resolution', NULL, false, false, false, NULL, NULL),

-- 行动方案属性
('ver-ot-coa-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-coa-v1', 'sp-type', NULL, false, true, false, NULL, NULL),
('ver-ot-coa-v1', 'sp-risk-level', NULL, false, true, false, 'Medium', '{"enum": ["Low", "Medium", "High"]}'),
('ver-ot-coa-v1', 'sp-estimated-cost', NULL, false, false, false, NULL, NULL),

-- 仓库属性
('ver-ot-warehouse-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-warehouse-v1', 'sp-location', NULL, false, true, false, NULL, NULL),
('ver-ot-warehouse-v1', 'sp-capacity', NULL, false, true, false, NULL, '{"min": 0}'),
('ver-ot-warehouse-v1', 'sp-utilization', NULL, false, false, false, '0', '{"min": 0, "max": 1}'),

-- 产品属性
('ver-ot-product-v1', 'sp-sku', NULL, false, true, false, NULL, NULL),
('ver-ot-product-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-product-v1', 'sp-quantity', NULL, false, true, false, '0', '{"min": 0}'),
('ver-ot-product-v1', 'sp-unit-price', NULL, false, true, false, NULL, '{"min": 0}'),

-- 铁路货运站属性
('ver-ot-rail-station-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-rail-station-v1', 'sp-handling-capacity', NULL, false, true, false, NULL, '{"min": 0}'),
('ver-ot-rail-station-v1', 'sp-position', NULL, false, false, false, NULL, NULL),

-- 工厂属性
('ver-ot-factory-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-factory-v1', 'sp-output-daily', NULL, false, true, false, NULL, '{"min": 0}'),

-- 疾病属性
('ver-ot-disease-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-disease-v1', 'sp-icd-code', NULL, false, true, false, NULL, '{"pattern": "^[A-Z][0-9]{2}(\\\\.[0-9]{1,2})?$"}'),
('ver-ot-disease-v1', 'sp-category', NULL, false, false, false, NULL, NULL),
('ver-ot-disease-v1', 'sp-desc', 'description', false, false, false, NULL, NULL),

-- 症状属性
('ver-ot-symptom-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-symptom-v1', 'sp-severity', NULL, false, true, false, NULL, '{"enum": ["轻度", "中度", "重度"]}'),
('ver-ot-symptom-v1', 'sp-body-part', NULL, false, false, false, NULL, NULL),

-- 患者属性
('ver-ot-patient-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-patient-v1', 'sp-age', NULL, false, true, false, NULL, '{"min": 0, "max": 150}'),
('ver-ot-patient-v1', 'sp-gender', NULL, false, true, false, NULL, '{"enum": ["男", "女"]}'),

-- 药物属性
('ver-ot-drug-v1', 'sp-name', NULL, false, true, true, NULL, NULL),
('ver-ot-drug-v1', 'sp-drug-class', 'class', false, true, false, NULL, NULL),
('ver-ot-drug-v1', 'sp-dosage', NULL, false, false, false, NULL, NULL);

-- ============================================================
-- 7. 链接类型定义 (meta_link_type_def)
-- ============================================================

INSERT INTO meta_link_type_def (id, api_name, current_version_id, created_at) VALUES
-- 项目1：战场态势感知系统
('lt-assigned-to', 'assigned_to', 'ver-lt-assigned-to-v1', NOW()),
('lt-targets', 'targets', 'ver-lt-targets-v1', NOW()),
('lt-escorts', 'escorts', 'ver-lt-escorts-v1', NOW()),
('lt-corroborates', 'corroborates', 'ver-lt-corroborates-v1', NOW()),
('lt-depicts', 'depicts', 'ver-lt-depicts-v1', NOW()),
('lt-plan-target', 'plans_against', 'ver-lt-plan-target-v1', NOW()),

-- 项目2：智能供应链管理
('lt-stored-in', 'stored_in', 'ver-lt-stored-in-v1', NOW()),
('lt-road-link', 'road_connection', 'ver-lt-road-link-v1', NOW()),
('lt-road-feeder', 'road_feeder', 'ver-lt-road-feeder-v1', NOW()),
('lt-rail-link', 'rail_connection', 'ver-lt-rail-link-v1', NOW()),
('lt-last-mile', 'last_mile', 'ver-lt-last-mile-v1', NOW()),

-- 项目3：医疗知识图谱
('lt-has-symptom', 'has_symptom', 'ver-lt-has-symptom-v1', NOW()),
('lt-diagnosed-with', 'diagnosed_with', 'ver-lt-diagnosed-with-v1', NOW()),
('lt-treats', 'treats', 'ver-lt-treats-v1', NOW()),
('lt-contra', 'contraindication', 'ver-lt-contra-v1', NOW());

-- ============================================================
-- 8. 链接类型版本 (meta_link_type_ver)
-- ============================================================

INSERT INTO meta_link_type_ver (id, def_id, version_number, display_name, source_object_def_id, target_object_def_id, cardinality, status, created_at) VALUES
-- 项目1：战场态势感知系统
('ver-lt-assigned-to-v1', 'lt-assigned-to', '1.0', '分配到', 'ot-fighter', 'ot-mission', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-targets-v1', 'lt-targets', '1.0', '打击目标', 'ot-mission', 'ot-target', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-escorts-v1', 'lt-escorts', '1.0', '护航', 'ot-fighter', 'ot-fighter', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-corroborates-v1', 'lt-corroborates', '1.0', '佐证', 'ot-intel', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-depicts-v1', 'lt-depicts', '1.0', '描绘', 'ot-image', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-plan-target-v1', 'lt-plan-target', '1.0', '针对', 'ot-coa', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),

-- 项目2：智能供应链管理
('ver-lt-stored-in-v1', 'lt-stored-in', '1.0', '存储于', 'ot-product', 'ot-warehouse', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-road-link-v1', 'lt-road-link', '1.0', '公路运输线', 'ot-factory', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-road-feeder-v1', 'lt-road-feeder', '1.0', '短驳运输', 'ot-factory', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-rail-link-v1', 'lt-rail-link', '1.0', '铁路干线', 'ot-rail-station', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-last-mile-v1', 'lt-last-mile', '1.0', '最后一公里', 'ot-rail-station', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED', NOW()),

-- 项目3：医疗知识图谱
('ver-lt-has-symptom-v1', 'lt-has-symptom', '1.0', '伴有症状', 'ot-disease', 'ot-symptom', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-diagnosed-with-v1', 'lt-diagnosed-with', '1.0', '确诊', 'ot-patient', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-treats-v1', 'lt-treats', '1.0', '治疗', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-contra-v1', 'lt-contra', '1.0', '禁忌', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW());

-- ============================================================
-- 9. 项目-对象类型绑定 (ctx_project_object_binding)
-- ============================================================

INSERT INTO ctx_project_object_binding (project_id, object_def_id, used_version_id, project_display_alias, is_visible) VALUES
-- 项目1：战场态势感知系统
('proj-001', 'ot-fighter', 'ver-ot-fighter-v1', NULL, true),
('proj-001', 'ot-target', 'ver-ot-target-v1', NULL, true),
('proj-001', 'ot-mission', 'ver-ot-mission-v1', NULL, true),
('proj-001', 'ot-intel', 'ver-ot-intel-v1', NULL, true),
('proj-001', 'ot-image', 'ver-ot-image-v1', NULL, true),
('proj-001', 'ot-coa', 'ver-ot-coa-v1', NULL, true),

-- 项目2：智能供应链管理
('proj-002', 'ot-warehouse', 'ver-ot-warehouse-v1', NULL, true),
('proj-002', 'ot-product', 'ver-ot-product-v1', NULL, true),
('proj-002', 'ot-rail-station', 'ver-ot-rail-station-v1', NULL, true),
('proj-002', 'ot-factory', 'ver-ot-factory-v1', NULL, true),

-- 项目3：医疗知识图谱
('proj-003', 'ot-disease', 'ver-ot-disease-v1', NULL, true),
('proj-003', 'ot-symptom', 'ver-ot-symptom-v1', NULL, true),
('proj-003', 'ot-patient', 'ver-ot-patient-v1', NULL, true),
('proj-003', 'ot-drug', 'ver-ot-drug-v1', NULL, true);

-- ============================================================
-- 10. 启用外键检查
-- ============================================================

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 验证数据导入
-- ============================================================

SELECT '=== 数据导入统计 ===' AS info;

SELECT 'sys_project' AS table_name, COUNT(*) AS count FROM sys_project WHERE id LIKE 'proj-%'
UNION ALL
SELECT 'meta_shared_property_def', COUNT(*) FROM meta_shared_property_def WHERE id LIKE 'sp-%'
UNION ALL
SELECT 'meta_object_type_def', COUNT(*) FROM meta_object_type_def WHERE id LIKE 'ot-%'
UNION ALL
SELECT 'meta_object_type_ver', COUNT(*) FROM meta_object_type_ver WHERE id LIKE 'ver-ot-%'
UNION ALL
SELECT 'rel_object_ver_property', COUNT(*) FROM rel_object_ver_property WHERE object_ver_id LIKE 'ver-ot-%'
UNION ALL
SELECT 'meta_link_type_def', COUNT(*) FROM meta_link_type_def WHERE id LIKE 'lt-%'
UNION ALL
SELECT 'meta_link_type_ver', COUNT(*) FROM meta_link_type_ver WHERE id LIKE 'ver-lt-%'
UNION ALL
SELECT 'ctx_project_object_binding', COUNT(*) FROM ctx_project_object_binding WHERE project_id LIKE 'proj-%';

SELECT '=== 项目列表 ===' AS info;
SELECT id, name, description FROM sys_project WHERE id LIKE 'proj-%';

SELECT '=== 对象类型列表 ===' AS info;
SELECT d.id, d.api_name, d.stereotype, v.display_name, v.status
FROM meta_object_type_def d
LEFT JOIN meta_object_type_ver v ON d.current_version_id = v.id
WHERE d.id LIKE 'ot-%';

SELECT '=== 链接类型列表 ===' AS info;
SELECT d.id, d.api_name, v.display_name, v.cardinality, v.status
FROM meta_link_type_def d
LEFT JOIN meta_link_type_ver v ON d.current_version_id = v.id
WHERE d.id LIKE 'lt-%';
