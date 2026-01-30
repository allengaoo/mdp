-- ============================================================
-- MDP Platform V3 架构测试数据导入脚本
-- 目标数据库: ontology_meta_new
-- ============================================================

-- 使用数据库
USE ontology_meta_new;

-- ============================================================
-- 第0步：清理现有测试数据（谨慎执行）
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

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

-- 清理共享属性
DELETE FROM meta_shared_property_def WHERE id LIKE 'prop-%';

-- 清理项目
DELETE FROM sys_project WHERE id LIKE 'proj-%';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 第1步：插入项目数据 (sys_project)
-- ============================================================

INSERT INTO sys_project (id, name, description, created_at, updated_at) VALUES
('proj-001', '战场态势感知系统', '基于本体的战场态势感知与决策支持系统，支持多源情报融合与行动方案规划', NOW(), NOW()),
('proj-002', '智能供应链管理', '供应链全流程本体建模与优化系统，支持多式联运路径优化', NOW(), NOW()),
('proj-003', '医疗知识图谱', '医疗领域知识图谱构建与推理系统，支持用药安全校验', NOW(), NOW());

-- ============================================================
-- 第2步：插入共享属性定义 (meta_shared_property_def)
-- ============================================================

INSERT INTO meta_shared_property_def (id, api_name, display_name, data_type, description, created_at) VALUES
-- 通用属性
('prop-name', 'name', '名称', 'STRING', '通用名称属性', NOW()),
('prop-desc', 'description', '描述', 'STRING', '详细描述', NOW()),
('prop-status', 'status', '状态', 'STRING', '运行状态', NOW()),
('prop-type', 'type', '类型', 'STRING', '分类类型', NOW()),

-- 地理位置属性
('prop-position', 'position', '位置', 'GEO_POINT', '地理坐标(lat, lng)', NOW()),
('prop-location', 'location', '地点', 'STRING', '位置描述', NOW()),

-- 数值属性
('prop-int-value', 'int_value', '整数值', 'INT', '通用整数', NOW()),
('prop-double-value', 'double_value', '浮点值', 'DOUBLE', '通用浮点数', NOW()),
('prop-bool-value', 'bool_value', '布尔值', 'BOOLEAN', '是/否标志', NOW()),

-- 战场态势专用属性
('prop-callsign', 'callsign', '呼号', 'STRING', '无线电呼号', NOW()),
('prop-model', 'model', '型号', 'STRING', '装备型号', NOW()),
('prop-fuel', 'fuel', '燃油(%)', 'INT', '燃油百分比', NOW()),
('prop-threat-level', 'threat_level', '威胁等级', 'INT', '1-5级威胁', NOW()),
('prop-is-destroyed', 'is_destroyed', '已摧毁', 'BOOLEAN', '目标是否被摧毁', NOW()),
('prop-priority', 'priority', '优先级', 'INT', '任务优先级', NOW()),
('prop-start-time', 'start_time', '开始时间', 'DATETIME', '计划开始时间', NOW()),
('prop-confidence', 'confidence', '置信度(%)', 'INT', '情报置信度', NOW()),
('prop-source', 'source', '来源', 'STRING', '情报来源', NOW()),
('prop-content', 'content', '内容', 'STRING', '内容摘要', NOW()),
('prop-timestamp', 'timestamp', '时间戳', 'DATETIME', '数据获取时间', NOW()),
('prop-platform', 'platform', '平台', 'STRING', '采集平台', NOW()),
('prop-url', 'url', '链接', 'STRING', 'URL地址', NOW()),
('prop-resolution', 'resolution', '分辨率', 'STRING', '图像分辨率', NOW()),
('prop-risk-level', 'risk_level', '风险等级', 'STRING', '风险评估', NOW()),
('prop-estimated-cost', 'estimated_cost', '预估成本', 'INT', '成本估算', NOW()),

-- 供应链专用属性
('prop-capacity', 'capacity', '容量', 'INT', '存储/处理容量', NOW()),
('prop-utilization', 'utilization', '利用率', 'DOUBLE', '使用率百分比', NOW()),
('prop-sku', 'sku', 'SKU', 'STRING', '库存单位编号', NOW()),
('prop-quantity', 'quantity', '数量', 'INT', '库存数量', NOW()),
('prop-unit-price', 'unit_price', '单价', 'DOUBLE', '商品单价', NOW()),
('prop-handling-capacity', 'handling_capacity', '吞吐能力', 'INT', 'TEU吞吐量', NOW()),
('prop-output-daily', 'output_daily', '日产量', 'INT', '每日产出', NOW()),

-- 医疗专用属性
('prop-icd-code', 'icd_code', 'ICD编码', 'STRING', '国际疾病分类编码', NOW()),
('prop-category', 'category', '分类', 'STRING', '疾病/药物分类', NOW()),
('prop-severity', 'severity', '严重程度', 'STRING', '病情严重程度', NOW()),
('prop-body-part', 'body_part', '部位', 'STRING', '身体部位', NOW()),
('prop-age', 'age', '年龄', 'INT', '患者年龄', NOW()),
('prop-gender', 'gender', '性别', 'STRING', '性别', NOW()),
('prop-drug-class', 'drug_class', '药物类别', 'STRING', '药理分类', NOW()),
('prop-dosage', 'dosage', '剂量', 'STRING', '用药剂量', NOW());

-- ============================================================
-- 第3步：插入对象类型定义 (meta_object_type_def)
-- ============================================================

INSERT INTO meta_object_type_def (id, api_name, stereotype, created_at) VALUES
-- 战场态势感知系统 (proj-001)
('ot-fighter', 'fighter', 'ENTITY', NOW()),
('ot-target', 'target', 'ENTITY', NOW()),
('ot-mission', 'mission', 'EVENT', NOW()),
('ot-intel', 'intel_report', 'DOCUMENT', NOW()),
('ot-image', 'surveillance_image', 'MEDIA', NOW()),
('ot-coa', 'course_of_action', 'ENTITY', NOW()),

-- 智能供应链管理 (proj-002)
('ot-warehouse', 'warehouse', 'ENTITY', NOW()),
('ot-product', 'product', 'ENTITY', NOW()),
('ot-rail-station', 'rail_station', 'ENTITY', NOW()),
('ot-factory', 'factory', 'ENTITY', NOW()),

-- 医疗知识图谱 (proj-003)
('ot-disease', 'disease', 'ENTITY', NOW()),
('ot-symptom', 'symptom', 'ENTITY', NOW()),
('ot-patient', 'patient', 'ENTITY', NOW()),
('ot-drug', 'drug', 'ENTITY', NOW());

-- ============================================================
-- 第4步：插入对象类型版本 (meta_object_type_ver)
-- ============================================================

INSERT INTO meta_object_type_ver (id, def_id, version_number, display_name, description, status, created_at) VALUES
-- 战场态势感知系统
('ver-ot-fighter', 'ot-fighter', '1.0', '战斗机', '空中作战单元', 'PUBLISHED', NOW()),
('ver-ot-target', 'ot-target', '1.0', '目标', '打击目标', 'PUBLISHED', NOW()),
('ver-ot-mission', 'ot-mission', '1.0', '任务', '作战任务', 'PUBLISHED', NOW()),
('ver-ot-intel', 'ot-intel', '1.0', '情报报告', '来自SIGINT/ELINT的原始情报', 'PUBLISHED', NOW()),
('ver-ot-image', 'ot-image', '1.0', '侦察图像', 'IMINT图像数据', 'PUBLISHED', NOW()),
('ver-ot-coa', 'ot-coa', '1.0', '行动方案', '针对目标的应对计划', 'PUBLISHED', NOW()),

-- 智能供应链管理
('ver-ot-warehouse', 'ot-warehouse', '1.0', '仓库', '存储设施', 'PUBLISHED', NOW()),
('ver-ot-product', 'ot-product', '1.0', '产品', '库存产品', 'PUBLISHED', NOW()),
('ver-ot-rail-station', 'ot-rail-station', '1.0', '铁路货运站', '铁路物流节点', 'PUBLISHED', NOW()),
('ver-ot-factory', 'ot-factory', '1.0', '制造工厂', '生产源头', 'PUBLISHED', NOW()),

-- 医疗知识图谱
('ver-ot-disease', 'ot-disease', '1.0', '疾病', '疾病实体', 'PUBLISHED', NOW()),
('ver-ot-symptom', 'ot-symptom', '1.0', '症状', '症状表现', 'PUBLISHED', NOW()),
('ver-ot-patient', 'ot-patient', '1.0', '患者', '就诊人员', 'PUBLISHED', NOW()),
('ver-ot-drug', 'ot-drug', '1.0', '药物', '治疗药品', 'PUBLISHED', NOW());

-- 更新定义表的 current_version_id
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-fighter' WHERE id = 'ot-fighter';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-target' WHERE id = 'ot-target';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-mission' WHERE id = 'ot-mission';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-intel' WHERE id = 'ot-intel';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-image' WHERE id = 'ot-image';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-coa' WHERE id = 'ot-coa';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-warehouse' WHERE id = 'ot-warehouse';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-product' WHERE id = 'ot-product';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-rail-station' WHERE id = 'ot-rail-station';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-factory' WHERE id = 'ot-factory';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-disease' WHERE id = 'ot-disease';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-symptom' WHERE id = 'ot-symptom';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-patient' WHERE id = 'ot-patient';
UPDATE meta_object_type_def SET current_version_id = 'ver-ot-drug' WHERE id = 'ot-drug';

-- ============================================================
-- 第5步：插入对象版本-属性绑定 (rel_object_ver_property)
-- ============================================================

INSERT INTO rel_object_ver_property (object_ver_id, property_def_id, is_primary_key, is_required, is_title) VALUES
-- 战斗机属性
('ver-ot-fighter', 'prop-callsign', FALSE, TRUE, TRUE),
('ver-ot-fighter', 'prop-model', FALSE, TRUE, FALSE),
('ver-ot-fighter', 'prop-fuel', FALSE, TRUE, FALSE),
('ver-ot-fighter', 'prop-status', FALSE, TRUE, FALSE),
('ver-ot-fighter', 'prop-position', FALSE, FALSE, FALSE),

-- 目标属性
('ver-ot-target', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-target', 'prop-type', FALSE, TRUE, FALSE),
('ver-ot-target', 'prop-threat-level', FALSE, TRUE, FALSE),
('ver-ot-target', 'prop-position', FALSE, FALSE, FALSE),
('ver-ot-target', 'prop-is-destroyed', FALSE, FALSE, FALSE),

-- 任务属性
('ver-ot-mission', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-mission', 'prop-type', FALSE, TRUE, FALSE),
('ver-ot-mission', 'prop-priority', FALSE, TRUE, FALSE),
('ver-ot-mission', 'prop-status', FALSE, TRUE, FALSE),
('ver-ot-mission', 'prop-start-time', FALSE, FALSE, FALSE),

-- 情报报告属性
('ver-ot-intel', 'prop-source', FALSE, TRUE, FALSE),
('ver-ot-intel', 'prop-confidence', FALSE, TRUE, FALSE),
('ver-ot-intel', 'prop-content', FALSE, TRUE, TRUE),
('ver-ot-intel', 'prop-timestamp', FALSE, FALSE, FALSE),

-- 侦察图像属性
('ver-ot-image', 'prop-platform', FALSE, TRUE, FALSE),
('ver-ot-image', 'prop-url', FALSE, TRUE, TRUE),
('ver-ot-image', 'prop-resolution', FALSE, FALSE, FALSE),

-- 行动方案属性
('ver-ot-coa', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-coa', 'prop-type', FALSE, TRUE, FALSE),
('ver-ot-coa', 'prop-risk-level', FALSE, TRUE, FALSE),
('ver-ot-coa', 'prop-estimated-cost', FALSE, FALSE, FALSE),

-- 仓库属性
('ver-ot-warehouse', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-warehouse', 'prop-location', FALSE, TRUE, FALSE),
('ver-ot-warehouse', 'prop-capacity', FALSE, TRUE, FALSE),
('ver-ot-warehouse', 'prop-utilization', FALSE, FALSE, FALSE),

-- 产品属性
('ver-ot-product', 'prop-sku', FALSE, TRUE, FALSE),
('ver-ot-product', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-product', 'prop-quantity', FALSE, TRUE, FALSE),
('ver-ot-product', 'prop-unit-price', FALSE, FALSE, FALSE),

-- 铁路货运站属性
('ver-ot-rail-station', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-rail-station', 'prop-handling-capacity', FALSE, TRUE, FALSE),
('ver-ot-rail-station', 'prop-position', FALSE, FALSE, FALSE),

-- 制造工厂属性
('ver-ot-factory', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-factory', 'prop-output-daily', FALSE, TRUE, FALSE),

-- 疾病属性
('ver-ot-disease', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-disease', 'prop-icd-code', FALSE, TRUE, FALSE),
('ver-ot-disease', 'prop-category', FALSE, TRUE, FALSE),
('ver-ot-disease', 'prop-desc', FALSE, FALSE, FALSE),

-- 症状属性
('ver-ot-symptom', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-symptom', 'prop-severity', FALSE, TRUE, FALSE),
('ver-ot-symptom', 'prop-body-part', FALSE, FALSE, FALSE),

-- 患者属性
('ver-ot-patient', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-patient', 'prop-age', FALSE, TRUE, FALSE),
('ver-ot-patient', 'prop-gender', FALSE, TRUE, FALSE),

-- 药物属性
('ver-ot-drug', 'prop-name', FALSE, TRUE, TRUE),
('ver-ot-drug', 'prop-drug-class', FALSE, TRUE, FALSE),
('ver-ot-drug', 'prop-dosage', FALSE, TRUE, FALSE);

-- ============================================================
-- 第6步：插入链接类型定义 (meta_link_type_def)
-- ============================================================

INSERT INTO meta_link_type_def (id, api_name, created_at) VALUES
-- 战场态势感知系统
('lt-assigned-to', 'assigned_to', NOW()),
('lt-targets', 'targets', NOW()),
('lt-escorts', 'escorts', NOW()),
('lt-corroborates', 'corroborates', NOW()),
('lt-depicts', 'depicts', NOW()),
('lt-plan-target', 'plans_against', NOW()),

-- 智能供应链管理
('lt-stored-in', 'stored_in', NOW()),
('lt-road-link', 'road_connection', NOW()),
('lt-road-feeder', 'road_feeder', NOW()),
('lt-rail-link', 'rail_connection', NOW()),
('lt-last-mile', 'last_mile', NOW()),

-- 医疗知识图谱
('lt-has-symptom', 'has_symptom', NOW()),
('lt-diagnosed-with', 'diagnosed_with', NOW()),
('lt-treats', 'treats', NOW()),
('lt-contra', 'contraindication', NOW());

-- ============================================================
-- 第7步：插入链接类型版本 (meta_link_type_ver)
-- ============================================================

INSERT INTO meta_link_type_ver (id, def_id, version_number, display_name, source_object_def_id, target_object_def_id, cardinality, status, created_at) VALUES
-- 战场态势感知系统
('ver-lt-assigned-to', 'lt-assigned-to', '1.0', '分配到', 'ot-fighter', 'ot-mission', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-targets', 'lt-targets', '1.0', '打击目标', 'ot-mission', 'ot-target', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-escorts', 'lt-escorts', '1.0', '护航', 'ot-fighter', 'ot-fighter', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-corroborates', 'lt-corroborates', '1.0', '佐证', 'ot-intel', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-depicts', 'lt-depicts', '1.0', '描绘', 'ot-image', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-plan-target', 'lt-plan-target', '1.0', '针对', 'ot-coa', 'ot-target', 'MANY_TO_ONE', 'PUBLISHED', NOW()),

-- 智能供应链管理
('ver-lt-stored-in', 'lt-stored-in', '1.0', '存储于', 'ot-product', 'ot-warehouse', 'MANY_TO_ONE', 'PUBLISHED', NOW()),
('ver-lt-road-link', 'lt-road-link', '1.0', '公路运输线', 'ot-factory', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-road-feeder', 'lt-road-feeder', '1.0', '短驳运输', 'ot-factory', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-rail-link', 'lt-rail-link', '1.0', '铁路干线', 'ot-rail-station', 'ot-rail-station', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-last-mile', 'lt-last-mile', '1.0', '最后一公里', 'ot-rail-station', 'ot-warehouse', 'MANY_TO_MANY', 'PUBLISHED', NOW()),

-- 医疗知识图谱
('ver-lt-has-symptom', 'lt-has-symptom', '1.0', '伴有症状', 'ot-disease', 'ot-symptom', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-diagnosed-with', 'lt-diagnosed-with', '1.0', '确诊', 'ot-patient', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-treats', 'lt-treats', '1.0', '治疗', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW()),
('ver-lt-contra', 'lt-contra', '1.0', '禁忌', 'ot-drug', 'ot-disease', 'MANY_TO_MANY', 'PUBLISHED', NOW());

-- 更新定义表的 current_version_id
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-assigned-to' WHERE id = 'lt-assigned-to';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-targets' WHERE id = 'lt-targets';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-escorts' WHERE id = 'lt-escorts';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-corroborates' WHERE id = 'lt-corroborates';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-depicts' WHERE id = 'lt-depicts';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-plan-target' WHERE id = 'lt-plan-target';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-stored-in' WHERE id = 'lt-stored-in';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-road-link' WHERE id = 'lt-road-link';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-road-feeder' WHERE id = 'lt-road-feeder';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-rail-link' WHERE id = 'lt-rail-link';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-last-mile' WHERE id = 'lt-last-mile';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-has-symptom' WHERE id = 'lt-has-symptom';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-diagnosed-with' WHERE id = 'lt-diagnosed-with';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-treats' WHERE id = 'lt-treats';
UPDATE meta_link_type_def SET current_version_id = 'ver-lt-contra' WHERE id = 'lt-contra';

-- ============================================================
-- 第8步：插入项目-对象类型绑定 (ctx_project_object_binding)
-- ============================================================

INSERT INTO ctx_project_object_binding (project_id, object_def_id, used_version_id, project_display_alias, is_visible) VALUES
-- 战场态势感知系统 (proj-001)
('proj-001', 'ot-fighter', 'ver-ot-fighter', '战斗机', TRUE),
('proj-001', 'ot-target', 'ver-ot-target', '打击目标', TRUE),
('proj-001', 'ot-mission', 'ver-ot-mission', '作战任务', TRUE),
('proj-001', 'ot-intel', 'ver-ot-intel', '情报报告', TRUE),
('proj-001', 'ot-image', 'ver-ot-image', '侦察图像', TRUE),
('proj-001', 'ot-coa', 'ver-ot-coa', '行动方案', TRUE),

-- 智能供应链管理 (proj-002)
('proj-002', 'ot-warehouse', 'ver-ot-warehouse', '配送中心', TRUE),
('proj-002', 'ot-product', 'ver-ot-product', '库存产品', TRUE),
('proj-002', 'ot-rail-station', 'ver-ot-rail-station', '铁路站点', TRUE),
('proj-002', 'ot-factory', 'ver-ot-factory', '生产工厂', TRUE),

-- 医疗知识图谱 (proj-003)
('proj-003', 'ot-disease', 'ver-ot-disease', '疾病', TRUE),
('proj-003', 'ot-symptom', 'ver-ot-symptom', '症状', TRUE),
('proj-003', 'ot-patient', 'ver-ot-patient', '患者', TRUE),
('proj-003', 'ot-drug', 'ver-ot-drug', '药物', TRUE);

-- ============================================================
-- 验证数据
-- ============================================================

SELECT '=== V3 测试数据导入完成 ===' AS message;

SELECT 'sys_project 项目数量' AS metric, COUNT(*) AS count FROM sys_project WHERE id LIKE 'proj-%';
SELECT 'meta_shared_property_def 共享属性数量' AS metric, COUNT(*) AS count FROM meta_shared_property_def WHERE id LIKE 'prop-%';
SELECT 'meta_object_type_def 对象类型定义数量' AS metric, COUNT(*) AS count FROM meta_object_type_def WHERE id LIKE 'ot-%';
SELECT 'meta_object_type_ver 对象类型版本数量' AS metric, COUNT(*) AS count FROM meta_object_type_ver WHERE id LIKE 'ver-ot-%';
SELECT 'rel_object_ver_property 属性绑定数量' AS metric, COUNT(*) AS count FROM rel_object_ver_property WHERE object_ver_id LIKE 'ver-ot-%';
SELECT 'meta_link_type_def 链接类型定义数量' AS metric, COUNT(*) AS count FROM meta_link_type_def WHERE id LIKE 'lt-%';
SELECT 'meta_link_type_ver 链接类型版本数量' AS metric, COUNT(*) AS count FROM meta_link_type_ver WHERE id LIKE 'ver-lt-%';
SELECT 'ctx_project_object_binding 项目绑定数量' AS metric, COUNT(*) AS count FROM ctx_project_object_binding WHERE project_id LIKE 'proj-%';

-- 按项目显示对象类型
SELECT 
    p.name AS '项目名称',
    COUNT(b.object_def_id) AS '对象类型数量'
FROM sys_project p
LEFT JOIN ctx_project_object_binding b ON p.id = b.project_id
WHERE p.id LIKE 'proj-%'
GROUP BY p.id, p.name;
