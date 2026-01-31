-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: ontology_meta_new
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `ontology_meta_new`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ontology_meta_new` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ontology_meta_new`;

--
-- Table structure for table `app_definition`
--

DROP TABLE IF EXISTS `app_definition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_definition` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `app_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'DASHBOARD, FORM, EXPLORER, WORKFLOW',
  `global_config` json DEFAULT NULL COMMENT '全局配置：主题、权限等',
  `created_by` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Workshop应用定义';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_definition`
--

LOCK TABLES `app_definition` WRITE;
/*!40000 ALTER TABLE `app_definition` DISABLE KEYS */;
INSERT INTO `app_definition` VALUES ('app-doc-explorer','proj-002','Document Explorer','EXPLORER','{\"theme\": \"light\", \"default_view\": \"grid\", \"enable_ai_search\": true}','system','2026-01-23 02:35:47','2026-01-23 02:35:47'),('app-geo-ops','proj-003','Operations Map','DASHBOARD','{\"theme\": \"light\", \"map_style\": \"satellite\", \"default_zoom\": 12}','system','2026-01-23 02:35:47','2026-01-23 02:35:47'),('app-iot-dashboard','proj-001','IoT Monitoring Dashboard','DASHBOARD','{\"theme\": \"dark\", \"refresh_interval\": 30, \"default_time_range\": \"24h\"}','system','2026-01-23 02:35:47','2026-01-23 02:35:47'),('app-target-360','default-project','Target 360 Profile','EXPLORER','{\"theme\": \"dark\", \"object_type\": \"Target\", \"refresh_interval\": 30000}','system','2026-01-26 10:05:52','2026-01-26 10:05:52');
/*!40000 ALTER TABLE `app_definition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_module`
--

DROP TABLE IF EXISTS `app_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_module` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `app_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `layout_config` json DEFAULT NULL COMMENT '布局配置：grid/flex等',
  `display_order` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用模块/页面';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_module`
--

LOCK TABLES `app_module` WRITE;
/*!40000 ALTER TABLE `app_module` DISABLE KEYS */;
INSERT INTO `app_module` VALUES ('mod-context','app-target-360','Context','{\"width\": 12, \"position\": \"center\", \"scrollable\": true}',2),('mod-doc-list','app-doc-explorer','Documents','{\"type\": \"main\"}',2),('mod-doc-preview','app-doc-explorer','Preview','{\"type\": \"detail\"}',3),('mod-doc-search','app-doc-explorer','Search','{\"type\": \"sidebar\"}',1),('mod-geo-list','app-geo-ops','Facility List','{\"type\": \"sidebar\"}',2),('mod-geo-map','app-geo-ops','Map View','{\"type\": \"full\"}',1),('mod-identity','app-target-360','Identity','{\"width\": 6, \"position\": \"left\", \"collapsible\": true}',1),('mod-intelligence','app-target-360','Intelligence','{\"width\": 6, \"position\": \"right\", \"collapsible\": true}',3),('mod-iot-alerts','app-iot-dashboard','Alerts','{\"type\": \"full\"}',3),('mod-iot-devices','app-iot-dashboard','Device List','{\"type\": \"full\"}',2),('mod-iot-overview','app-iot-dashboard','Overview','{\"type\": \"grid\", \"columns\": 4}',1);
/*!40000 ALTER TABLE `app_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_widget`
--

DROP TABLE IF EXISTS `app_widget`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_widget` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `module_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `widget_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'TABLE, CHART, MAP, FORM, TIMELINE, MEDIA_VIEWER',
  `data_binding` json NOT NULL COMMENT '数据绑定：对象类型、查询条件等',
  `view_config` json DEFAULT NULL COMMENT '视图配置：列定义、图表类型等',
  `position_config` json DEFAULT NULL COMMENT '位置配置：x,y,w,h',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用组件/部件';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_widget`
--

LOCK TABLES `app_widget` WRITE;
/*!40000 ALTER TABLE `app_widget` DISABLE KEYS */;
INSERT INTO `app_widget` VALUES ('wgt-ai','mod-intelligence','AI_INSIGHTS','{\"top_k\": 5, \"vector_field\": \"image_vector\", \"similarity_threshold\": 0.7}','{\"title\": \"AI 智能分析\", \"showScore\": true, \"allowCompare\": true}','{\"order\": 2, \"height\": \"auto\"}'),('wgt-alert-count','mod-iot-overview','STAT_CARD','{\"filter\": {\"alert_level\": \"CRITICAL\"}, \"aggregation\": \"COUNT\", \"object_type\": \"alert\"}','{\"icon\": \"warning\", \"color\": \"#FF4D4F\", \"title\": \"Critical Alerts\"}','{\"h\": 1, \"w\": 1, \"x\": 1, \"y\": 0}'),('wgt-alert-timeline','mod-iot-alerts','TIMELINE','{\"sort\": \"DESC\", \"time_field\": \"triggered_at\", \"object_type\": \"alert\"}','{\"color_field\": \"alert_level\", \"title_field\": \"title\", \"content_field\": \"message\"}','{\"h\": 4, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-device-count','mod-iot-overview','STAT_CARD','{\"aggregation\": \"COUNT\", \"object_type\": \"device\"}','{\"icon\": \"sensor\", \"color\": \"#1890FF\", \"title\": \"Total Devices\"}','{\"h\": 1, \"w\": 1, \"x\": 0, \"y\": 0}'),('wgt-device-table','mod-iot-devices','TABLE','{\"page_size\": 20, \"object_type\": \"device\"}','{\"columns\": [\"device_id\", \"name\", \"status\", \"category\", \"created_at\"], \"sortable\": true, \"filterable\": true}','{\"h\": 4, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-doc-grid','mod-doc-list','GALLERY','{\"page_size\": 24, \"object_type\": \"document\"}','{\"display_fields\": [\"title\", \"file_type\", \"upload_time\"], \"thumbnail_field\": \"thumbnail_url\"}','{\"h\": 4, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-doc-search-bar','mod-doc-search','SEARCH','{\"object_type\": \"document\", \"search_fields\": [\"title\", \"content\", \"ai_summary\"], \"enable_vector_search\": true}','{\"placeholder\": \"Search documents...\"}','{\"h\": 1, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-doc-viewer','mod-doc-preview','MEDIA_VIEWER','{\"url_field\": \"file_url\", \"object_type\": \"document\"}','{\"show_sidebar\": true, \"enable_annotations\": true}','{\"h\": 4, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-facility-list','mod-geo-list','TABLE','{\"page_size\": 50, \"object_type\": \"facility\"}','{\"columns\": [\"name\", \"facility_type\", \"status\", \"address\"], \"compact\": true}','{\"h\": 4, \"w\": 2, \"x\": 0, \"y\": 0}'),('wgt-facility-map','mod-geo-map','MAP','{\"object_type\": \"facility\", \"location_field\": \"location\"}','{\"map_type\": \"satellite\", \"popup_fields\": [\"name\", \"facility_type\", \"status\"], \"cluster_enabled\": true}','{\"h\": 4, \"w\": 4, \"x\": 0, \"y\": 0}'),('wgt-humidity-chart','mod-iot-overview','CHART','{\"x_axis\": \"reading_time\", \"y_axis\": \"humidity\", \"group_by\": \"device_id\", \"object_type\": \"sensor_reading\"}','{\"title\": \"Humidity Trends\", \"chart_type\": \"line\"}','{\"h\": 2, \"w\": 2, \"x\": 2, \"y\": 1}'),('wgt-media','mod-intelligence','MEDIA_CAROUSEL','{\"link_type\": \"has_recon_image\", \"media_types\": [\"image\", \"video\"]}','{\"title\": \"侦察影像\", \"autoPlay\": false, \"showThumbnails\": true}','{\"order\": 1, \"height\": 250}'),('wgt-minimap','mod-identity','MINI_MAP','{\"lat\": \"latitude\", \"lon\": \"longitude\", \"heading\": \"heading\"}','{\"zoom\": 12, \"title\": \"当前位置\", \"showTrack\": true}','{\"order\": 2, \"height\": 200}'),('wgt-props','mod-identity','PROPERTY_LIST','{\"fields\": [\"mmsi\", \"imo\", \"name\", \"country\", \"status\", \"threat_level\", \"speed\", \"heading\"]}','{\"title\": \"基本信息\", \"layout\": \"vertical\", \"labelWidth\": 100}','{\"order\": 1, \"height\": \"auto\"}'),('wgt-relations','mod-context','RELATION_LIST','{\"link_types\": [\"has_mission\", \"corroborated_by\", \"detected_by\", \"docked_at\"]}','{\"title\": \"关联关系\", \"showType\": true, \"expandable\": true}','{\"order\": 2, \"height\": \"auto\"}'),('wgt-stats','mod-identity','STAT_CARD','{\"metrics\": [\"total_sightings\", \"last_seen_days\", \"threat_score\"]}','{\"title\": \"统计摘要\", \"layout\": \"grid\", \"columns\": 3}','{\"order\": 0, \"height\": 80}'),('wgt-temp-chart','mod-iot-overview','CHART','{\"x_axis\": \"reading_time\", \"y_axis\": \"temperature\", \"group_by\": \"device_id\", \"object_type\": \"sensor_reading\"}','{\"title\": \"Temperature Trends\", \"chart_type\": \"line\"}','{\"h\": 2, \"w\": 2, \"x\": 0, \"y\": 1}'),('wgt-timeline','mod-context','TIMELINE','{\"sources\": [\"sys_action_log\", \"linked_events\"], \"time_field\": \"created_at\"}','{\"mode\": \"left\", \"title\": \"活动时间线\", \"showIcon\": true}','{\"order\": 1, \"height\": 400}');
/*!40000 ALTER TABLE `app_widget` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ctx_link_mapping_def`
--

DROP TABLE IF EXISTS `ctx_link_mapping_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctx_link_mapping_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `link_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_connection_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `join_table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_key_column` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_key_column` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `property_mappings` json DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_ctx_link_mapping_def_link_def_id` (`link_def_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ctx_link_mapping_def`
--

LOCK TABLES `ctx_link_mapping_def` WRITE;
/*!40000 ALTER TABLE `ctx_link_mapping_def` DISABLE KEYS */;
INSERT INTO `ctx_link_mapping_def` VALUES ('3a9f3c0a-dd9e-47be-a35a-fe5208f18015','22e3da28-bef1-46bf-99d1-bc645089b06d','190f434f-da70-4c30-9fbe-63e2a87eaf45','rel_target_report','id','target_id','{\"report_ida\": \"report_id\", \"created_ata\": \"created_at\"}','DRAFT','2026-01-30 16:27:03','2026-01-30 16:27:03'),('58e66620-e451-47e0-849d-e2fa9cb7cb4d','78f5f16f-fd14-4763-9d8e-35eef59b4cc1','conn-456','raw_join_table_v2','src_id','tgt_id','{\"role\": \"role_col\"}','DRAFT','2026-01-29 14:49:53','2026-01-29 14:49:53'),('929d5170-7343-464e-9840-0e46f8cd060b','3b38cf70-4cb1-41b3-bb64-49bea5f15c53','conn-456','raw_join_table_v2','src_id','tgt_id','{\"role\": \"role_col\"}','DRAFT','2026-01-29 14:56:48','2026-01-29 14:56:48'),('c6fbf88b-86ca-4014-b5ec-fbeb81b7d5cc','f2317566-35b9-4a8e-b2cd-798338613227','conn-456','raw_join_table_v2','src_id','tgt_id','{\"role\": \"role_col\"}','DRAFT','2026-01-29 14:46:48','2026-01-29 14:46:48'),('db4b773e-7ef7-447e-a382-26c6e8af627b','linktype-target-report-001',NULL,'rel_target_report','target_id','report_id','{}','DRAFT','2026-01-30 06:17:09',NULL),('e1c27194-74bb-4d4d-aa81-db77e6326d4e','9600e4c0-46bc-4173-a826-30641a129255','conn-456','raw_join_table_v2','src_id','tgt_id','{\"role\": \"role_col\"}','DRAFT','2026-01-29 14:44:22','2026-01-29 14:44:22');
/*!40000 ALTER TABLE `ctx_link_mapping_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ctx_object_instance_lineage`
--

DROP TABLE IF EXISTS `ctx_object_instance_lineage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctx_object_instance_lineage` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '本体对象类型ID',
  `instance_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对象实例ID (同时是Milvus向量ID)',
  `mapping_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '来源映射定义ID',
  `source_table` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始表名 (mdp_raw_store)',
  `source_row_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始行主键/ID',
  `source_file_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '原始文件路径 (如S3 path, 用于非结构化数据)',
  `vector_collection` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Milvus集合名称',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_instance_id` (`instance_id`),
  KEY `idx_object_def_id` (`object_def_id`),
  KEY `idx_mapping_id` (`mapping_id`),
  KEY `idx_source_lookup` (`source_table`,`source_row_id`),
  KEY `idx_vector_collection` (`vector_collection`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对象实例溯源表 - 向量到原始数据的追溯映射';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ctx_object_instance_lineage`
--

LOCK TABLES `ctx_object_instance_lineage` WRITE;
/*!40000 ALTER TABLE `ctx_object_instance_lineage` DISABLE KEYS */;
INSERT INTO `ctx_object_instance_lineage` VALUES ('17eb158f-9349-42ca-86c4-c2cd864e73a9','fc9c9f0f-811b-4204-b6e0-33208541563f','f8557aa1-63ca-4cd7-8741-e4ea8702b0bf','bee2ebd7-e052-49cc-9241-ee366f24f339','raw_e2e_planes_f20b0868','p1',NULL,NULL,'2026-01-29 22:44:24'),('1e772227-d75c-45f7-bd3b-667e50b3adba','6fc14db9-d764-4cc7-9fff-8c9786c13b39','421ba6ab-76d8-4c53-8db2-09e2bbd84d52','63b4f4c6-9546-4454-93af-467c734da700','raw_e2e_planes','p1',NULL,NULL,'2026-01-29 22:35:52'),('55b60313-2ebe-4e73-a00a-4fd10c17a789','ac684509-6193-4dff-842e-3caf1721fbbb','7b62dfb6-858b-44cb-ba8f-574511b7cbbf','1474e2de-4db5-4a77-a45e-dc3b05fe466a','raw_e2e_planes_cdf38c15','p2',NULL,NULL,'2026-01-29 22:46:50'),('576b6fdc-489e-4026-ab18-5ac3f0125870','ac684509-6193-4dff-842e-3caf1721fbbb','74cec031-223d-4fa6-8418-1fa56df8078a','1474e2de-4db5-4a77-a45e-dc3b05fe466a','raw_e2e_planes_cdf38c15','p1',NULL,NULL,'2026-01-29 22:46:50'),('716b586b-64ed-4bda-8d72-7578235d9bf4','96b03573-e3cf-4aad-a8b9-b8523209272c','326c8f6d-5858-4b79-ab44-de192aa5b646','cfbdc6ff-21d6-460d-b937-4c3f39621e1a','raw_e2e_planes_1a7dafa3','p1',NULL,NULL,'2026-01-29 22:49:54'),('bef85f96-331b-4471-86b6-9c302d5d5d32','4f37bc91-f949-4021-9b18-8c7bd09906a3','f201bc41-47a0-4972-8691-dd3ed5a0fa93','e4333925-7a7b-49e7-bd35-b2ca9ffcf11e','raw_e2e_planes_6c4551e8','p2',NULL,NULL,'2026-01-29 22:56:49'),('cce078a5-4bbc-497d-9be8-13a89888ca24','4f37bc91-f949-4021-9b18-8c7bd09906a3','4fba0ec7-8c5e-407b-9ec0-175666cea416','e4333925-7a7b-49e7-bd35-b2ca9ffcf11e','raw_e2e_planes_6c4551e8','p1',NULL,NULL,'2026-01-29 22:56:49'),('ec523237-0143-411a-bd7a-eb8cfd2e191f','fc9c9f0f-811b-4204-b6e0-33208541563f','85294e6a-393c-4319-9255-95852d2221e8','bee2ebd7-e052-49cc-9241-ee366f24f339','raw_e2e_planes_f20b0868','p2',NULL,NULL,'2026-01-29 22:44:24'),('f8003c5f-f585-4d6c-bcf4-087a44ca5fc9','96b03573-e3cf-4aad-a8b9-b8523209272c','94e843e0-624a-4001-98c6-e57a23acbf4a','cfbdc6ff-21d6-460d-b937-4c3f39621e1a','raw_e2e_planes_1a7dafa3','p2',NULL,NULL,'2026-01-29 22:49:54'),('f8bebe0d-d80c-4a24-877b-cb2c8679daf5','6fc14db9-d764-4cc7-9fff-8c9786c13b39','e90ad988-05c0-4677-aa13-78207d2a0743','63b4f4c6-9546-4454-93af-467c734da700','raw_e2e_planes','p2',NULL,NULL,'2026-01-29 22:35:52');
/*!40000 ALTER TABLE `ctx_object_instance_lineage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ctx_object_mapping_def`
--

DROP TABLE IF EXISTS `ctx_object_mapping_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctx_object_mapping_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标本体对象类型ID',
  `source_connection_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '源数据连接ID',
  `source_table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '源表名 (mdp_raw_store中的表)',
  `mapping_spec` json NOT NULL COMMENT 'React Flow图配置 (nodes, edges)',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT' COMMENT '状态: DRAFT, PUBLISHED, ARCHIVED',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_object_def_id` (`object_def_id`),
  KEY `idx_source_connection_id` (`source_connection_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='多模态映射定义表 - 存储React Flow图的映射逻辑';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ctx_object_mapping_def`
--

LOCK TABLES `ctx_object_mapping_def` WRITE;
/*!40000 ALTER TABLE `ctx_object_mapping_def` DISABLE KEYS */;
INSERT INTO `ctx_object_mapping_def` VALUES ('1474e2de-4db5-4a77-a45e-dc3b05fe466a','ac684509-6193-4dff-842e-3caf1721fbbb','conn-default','raw_e2e_planes_cdf38c15','{\"edges\": [{\"source\": \"src_id\", \"target\": \"tgt_id\"}, {\"source\": \"src_tail\", \"target\": \"tgt_tail\"}], \"nodes\": [{\"id\": \"src_id\", \"data\": {\"column\": \"id\"}, \"type\": \"source\"}, {\"id\": \"src_tail\", \"data\": {\"column\": \"tail_number\"}, \"type\": \"source\"}, {\"id\": \"tgt_id\", \"data\": {\"property\": \"id\"}, \"type\": \"target\"}, {\"id\": \"tgt_tail\", \"data\": {\"property\": \"tail_number\"}, \"type\": \"target\"}]}','PUBLISHED','2026-01-29 14:46:49','2026-01-29 14:46:49'),('4f4e72eb-16b3-4967-ac89-ad9111aec1e3','598fd87c-d87d-47e0-ae58-c3505fdf188a','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_targets','{\"edges\": [], \"nodes\": []}','PUBLISHED','2026-01-29 09:05:30','2026-01-29 17:05:29'),('50178de2-4370-41d5-8b2d-070b2d3aac0c','95e3aa24-275e-42ab-8815-451109f46e28','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_recon_images','{\"edges\": [], \"nodes\": []}','PUBLISHED','2026-01-29 09:11:54','2026-01-29 17:11:54'),('63b4f4c6-9546-4454-93af-467c734da700','6fc14db9-d764-4cc7-9fff-8c9786c13b39','conn-default','raw_e2e_planes','{\"edges\": [{\"source\": \"src_id\", \"target\": \"tgt_id\"}, {\"source\": \"src_tail\", \"target\": \"tgt_tail\"}], \"nodes\": [{\"id\": \"src_id\", \"data\": {\"column\": \"id\"}, \"type\": \"source\"}, {\"id\": \"src_tail\", \"data\": {\"column\": \"tail_number\"}, \"type\": \"source\"}, {\"id\": \"tgt_id\", \"data\": {\"property\": \"id\"}, \"type\": \"target\"}, {\"id\": \"tgt_tail\", \"data\": {\"property\": \"tail_number\"}, \"type\": \"target\"}]}','PUBLISHED','2026-01-29 14:35:51','2026-01-29 14:35:51'),('8c3d1cdf-39ef-41d0-b486-26f337dec853','objtype-intel-report-001','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_intel_reports','{}','PUBLISHED','2026-01-29 16:19:34','2026-01-29 16:19:34'),('8c991983-9827-46f0-83c0-5b9fea898c1e','objtype-target-001','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_targets','{}','PUBLISHED','2026-01-29 16:19:34','2026-01-29 16:19:34'),('bee2ebd7-e052-49cc-9241-ee366f24f339','fc9c9f0f-811b-4204-b6e0-33208541563f','conn-default','raw_e2e_planes_f20b0868','{\"edges\": [{\"source\": \"src_id\", \"target\": \"tgt_id\"}, {\"source\": \"src_tail\", \"target\": \"tgt_tail\"}], \"nodes\": [{\"id\": \"src_id\", \"data\": {\"column\": \"id\"}, \"type\": \"source\"}, {\"id\": \"src_tail\", \"data\": {\"column\": \"tail_number\"}, \"type\": \"source\"}, {\"id\": \"tgt_id\", \"data\": {\"property\": \"id\"}, \"type\": \"target\"}, {\"id\": \"tgt_tail\", \"data\": {\"property\": \"tail_number\"}, \"type\": \"target\"}]}','PUBLISHED','2026-01-29 14:44:23','2026-01-29 14:44:23'),('e09698ba-124c-46fc-be5e-33b8e30f007f','objtype-recon-image-001','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_recon_images','{}','PUBLISHED','2026-01-29 16:19:34','2026-01-29 16:19:34'),('fb22bc9f-f317-4c03-b18e-577167c64831','f1b78787-6323-4cc1-9850-72e1036557a7','190f434f-da70-4c30-9fbe-63e2a87eaf45','raw_raw_recon_images','{\"edges\": [], \"nodes\": []}','PUBLISHED','2026-01-29 09:08:57','2026-01-29 17:08:56');
/*!40000 ALTER TABLE `ctx_object_mapping_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ctx_project_object_binding`
--

DROP TABLE IF EXISTS `ctx_project_object_binding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctx_project_object_binding` (
  `project_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `used_version_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目使用的具体版本',
  `project_display_alias` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '项目内的显示别名',
  `is_visible` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`project_id`,`object_def_id`),
  KEY `object_def_id` (`object_def_id`),
  KEY `used_version_id` (`used_version_id`),
  CONSTRAINT `ctx_project_object_binding_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `sys_project` (`id`),
  CONSTRAINT `ctx_project_object_binding_ibfk_2` FOREIGN KEY (`object_def_id`) REFERENCES `meta_object_type_def` (`id`),
  CONSTRAINT `ctx_project_object_binding_ibfk_3` FOREIGN KEY (`used_version_id`) REFERENCES `meta_object_type_ver` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目与对象类型的绑定关系';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ctx_project_object_binding`
--

LOCK TABLES `ctx_project_object_binding` WRITE;
/*!40000 ALTER TABLE `ctx_project_object_binding` DISABLE KEYS */;
INSERT INTO `ctx_project_object_binding` VALUES ('proj-integration-test-001','objtype-intel-report-001','ver-db20a136',NULL,1),('proj-integration-test-001','objtype-recon-image-001','ver-40568975',NULL,1),('proj-integration-test-001','objtype-target-001','ver-98996315',NULL,1);
/*!40000 ALTER TABLE `ctx_project_object_binding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_action_def`
--

DROP TABLE IF EXISTS `meta_action_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_action_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `backing_function_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operation_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_object_type_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parameters_schema` json DEFAULT NULL,
  `property_mapping` json DEFAULT NULL,
  `validation_rules` json DEFAULT NULL,
  `project_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_action_def_api_name` (`api_name`),
  KEY `fk_action_backing_function` (`backing_function_id`),
  CONSTRAINT `fk_action_backing_function` FOREIGN KEY (`backing_function_id`) REFERENCES `meta_function_def` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_action_def`
--

LOCK TABLES `meta_action_def` WRITE;
/*!40000 ALTER TABLE `meta_action_def` DISABLE KEYS */;
INSERT INTO `meta_action_def` VALUES ('9ba8eff8-89b6-4902-92d3-65d816b0baf9','action2','action2',NULL,NULL,'update_property','objtype-intel-report-001','[{\"api_id\": \"a\", \"required\": false, \"data_type\": \"string\", \"display_name\": \"a\"}, {\"api_id\": \"b\", \"required\": false, \"data_type\": \"string\", \"display_name\": \"b\"}]','{\"a\": \"aaa\", \"b\": \"classification\"}','{\"pre_condition\": [{\"expression\": \"\", \"target_field\": \"classification\", \"error_message\": \"\"}], \"post_condition\": [{\"expression\": \"\", \"target_field\": \"aaa\", \"error_message\": \"\"}], \"param_validation\": [{\"expression\": \"\", \"target_field\": \"a\", \"error_message\": \"\"}]}','proj-integration-test-001'),('a06cfd89-30c8-4045-ae9c-a199f0902ea3','action1','action1',NULL,NULL,'update_property','objtype-intel-report-001','[{\"api_id\": \"api1\", \"required\": false, \"data_type\": \"string\", \"display_name\": \"param1\"}, {\"api_id\": \"api2\", \"required\": false, \"data_type\": \"string\", \"display_name\": \"param2\"}]','{\"api1\": \"title\", \"api2\": \"content\"}','{\"pre_condition\": [{\"expression\": \"title=\'good\'\", \"target_field\": \"title\", \"error_message\": \"aaaa\"}], \"post_condition\": [{\"expression\": \"source=\'us\'\", \"target_field\": \"source\", \"error_message\": \"bbbbb\"}], \"param_validation\": [{\"expression\": \"param1 = \'us\'\", \"target_field\": \"api1\", \"error_message\": \"only us is support\"}]}','proj-integration-test-001'),('act_ai_recon_01','analyze_satellite_image','分析卫星图像','fn_ai_recon_01',NULL,NULL,NULL,NULL,NULL,NULL,NULL),('act_intel_verify_01','verify_intel_report','验证情报报告','fn_intel_verify_01',NULL,NULL,NULL,NULL,NULL,NULL,NULL),('act_mission_assign_01','execute_strike_plan','执行打击计划','fn_mission_assign_01',NULL,NULL,NULL,NULL,NULL,NULL,NULL),('d6820fcd-5f93-4177-aa68-4ea8f15151e3','aa','aa',NULL,'','update_property','objtype-target-001','[{\"api_id\": \"aa\", \"required\": false, \"data_type\": \"string\"}, {\"api_id\": \"aa\", \"required\": false, \"data_type\": \"string\"}]','{\"aa\": \"mmsi\"}','{\"pre_condition\": [{\"expression\": \"xx\", \"target_field\": \"lon\", \"error_message\": \"xx\"}], \"post_condition\": [{\"expression\": \"xx\", \"target_field\": \"mmsi\", \"error_message\": \"xx\"}], \"param_validation\": [{\"expression\": \"xx\", \"target_field\": \"aa\", \"error_message\": \"xxx\"}]}','proj-integration-test-001');
/*!40000 ALTER TABLE `meta_action_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_function_def`
--

DROP TABLE IF EXISTS `meta_function_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_function_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_content` longtext COLLATE utf8mb4_unicode_ci COMMENT 'Python Code Content',
  `bound_object_type_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `input_params_schema` json DEFAULT NULL,
  `output_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'VOID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_function_def_api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_function_def`
--

LOCK TABLES `meta_function_def` WRITE;
/*!40000 ALTER TABLE `meta_function_def` DISABLE KEYS */;
INSERT INTO `meta_function_def` VALUES ('fn_ai_recon_01','ai_recon_analyze','AI卫星图像分析','# AI Satellite Analysis Function (Multimodal)\n# AI卫星图像分析\ndef main(context):\n    \"\"\"\n    对卫星/侦察图像进行AI分析\n    Args:\n        context: {\n            \"image_id\": str,           # 图像ID\n            \"confidence_threshold\": float  # 置信度阈值\n        }\n    \"\"\"\n    image_id = context.get(\"image_id\")\n    confidence_threshold = context.get(\"confidence_threshold\", 0.95)\n    if not image_id:\n        return {\"success\": False, \"message\": \"Missing image_id parameter\"}\n    print(f\"[AI Recon] Analyzing image: {image_id}\")\n    print(f\"[AI Recon] Confidence threshold: {confidence_threshold}\")\n    # Simulate getting image object and S3 path\n    # In production:\n    # img_obj = get_object(\"ReconImage\", image_id)\n    # s3_path = img_obj.s3_path\n    s3_path = f\"s3://mdp-recon-images/{image_id}.jpg\"\n    print(f\"[AI Recon] Image path: {s3_path}\")\n    # Simulate AI inference\n    # In production:\n    # detection = cv_model_client.detect_objects(s3_path)\n    # Mock AI detection result\n    detection = {\n        \"confidence\": 0.97,\n        \"detected_objects\": [\"vessel\", \"wake_pattern\"],\n        \"lat\": 25.0340,\n        \"lon\": 121.5645,\n        \"heading\": 45.2\n    }\n    print(f\"[AI Recon] Detection confidence: {detection[\"confidence\"]}\")\n    print(f\"[AI Recon] Detected objects: {detection[\"detected_objects\"]}\")\n    if detection[\"confidence\"] >= confidence_threshold:\n        # High confidence - update target coordinates\n        # In production:\n        # target = img_obj.get_link(\"depicts_target\")\n        # target.lat = detection[\"lat\"]\n        # target.lon = detection[\"lon\"]\n        # target.save()\n        print(f\"[AI Recon] Updating target coordinates: ({detection[\"lat\"]}, {detection[\"lon\"]})\")\n        return {\n            \"success\": True,\n            \"image_id\": image_id,\n            \"confidence\": detection[\"confidence\"],\n            \"detected_objects\": detection[\"detected_objects\"],\n            \"coordinates_updated\": True,\n            \"new_lat\": detection[\"lat\"],\n            \"new_lon\": detection[\"lon\"],\n            \"message\": f\"Target coordinates corrected by AI (Confidence: {detection[\"confidence\"]:.2%})\"\n        }\n    else:\n        print(f\"[AI Recon] Low confidence ({detection[\"confidence\"]:.2%}), no changes made\")\n        return {\n            \"success\": True,\n            \"image_id\": image_id,\n            \"confidence\": detection[\"confidence\"],\n            \"detected_objects\": detection[\"detected_objects\"],\n            \"coordinates_updated\": False,\n            \"message\": f\"Low confidence detection ({detection[\"confidence\"]:.2%}), no changes made\"\n        }\n',NULL,'对侦察图像进行AI分析，识别目标并更新坐标信息','[{\"name\": \"image_id\", \"type\": \"string\", \"required\": true, \"description\": \"侦察图像ID\"}, {\"name\": \"confidence_threshold\", \"type\": \"number\", \"default\": 0.95, \"required\": false, \"description\": \"AI置信度阈值 (0-1)\"}]','OBJECT'),('fn_intel_verify_01','intel_verify','情报验证','# Intelligence Verification Function\n# 验证情报报告，关联目标威胁等级升级\ndef main(context):\n    \"\"\"\n    验证情报报告并更新关联目标的威胁等级\n    Args:\n        context: {\n            \"report_id\": str,  # 情报报告ID\n            \"status\": str      # 验证状态: VERIFIED / REJECTED\n        }\n    \"\"\"\n    report_id = context.get(\"report_id\")\n    status = context.get(\"status\", \"VERIFIED\")\n    if not report_id:\n        return {\"success\": False, \"message\": \"Missing report_id parameter\"}\n    print(f\"[Intel Verify] Processing report: {report_id}\")\n    print(f\"[Intel Verify] New status: {status}\")\n    # Simulate getting report object\n    # In production: report = get_object(\"IntelReport\", report_id)\n    result_messages = [f\"Report {report_id} status updated to {status}\"]\n    if status == \"VERIFIED\":\n        # Simulate finding linked target and escalating threat level\n        # In production: \n        # links = get_links(report_id, \"corroborates_target\")\n        # target = get_object(\"Target\", links[0][\"target_id\"])\n        # update_object(\"Target\", target_id, {\"threat_level\": \"HIGH\"})\n        print(\"[Intel Verify] Escalating linked target to HIGH threat level\")\n        result_messages.append(\"Linked target escalated to HIGH threat level\")\n        return {\n            \"success\": True,\n            \"report_id\": report_id,\n            \"status\": status,\n            \"threat_escalated\": True,\n            \"message\": \" | \".join(result_messages)\n        }\n    return {\n        \"success\": True,\n        \"report_id\": report_id,\n        \"status\": status,\n        \"threat_escalated\": False,\n        \"message\": \" | \".join(result_messages)\n    }\n',NULL,'验证情报报告，如验证通过则升级关联目标的威胁等级为HIGH','[{\"name\": \"report_id\", \"type\": \"string\", \"required\": true, \"description\": \"情报报告ID\"}, {\"name\": \"status\", \"type\": \"string\", \"default\": \"VERIFIED\", \"required\": false, \"description\": \"验证状态 (VERIFIED/REJECTED)\"}]','OBJECT'),('fn_mission_assign_01','mission_assign','任务自动分配','# Auto-Assign Strike Mission Function\n# 自动分配打击任务\ndef main(context):\n    \"\"\"\n    创建打击任务并分配可用战机\n    Args:\n        context: {\n            \"plan_id\": str,       # 作战计划ID\n            \"mission_type\": str,  # 任务类型\n            \"required_jets\": int  # 需要的战机数量\n        }\n    \"\"\"\n    plan_id = context.get(\"plan_id\")\n    mission_type = context.get(\"mission_type\", \"Precision Strike\")\n    required_jets = context.get(\"required_jets\", 2)\n    if not plan_id:\n        return {\"success\": False, \"message\": \"Missing plan_id parameter\"}\n    print(f\"[Mission Assign] Processing plan: {plan_id}\")\n    print(f\"[Mission Assign] Mission type: {mission_type}\")\n    print(f\"[Mission Assign] Required jets: {required_jets}\")\n    # Simulate creating mission\n    mission_code = f\"MSN-{plan_id[:8]}-ALPHA\"\n    print(f\"[Mission Assign] Created mission: {mission_code}\")\n    # Simulate querying available J-20 fighters\n    # In production:\n    # available_jets = ontology.search(\"FighterJet\")\n    #     .filter(model=\"J-20\", status=\"READY\")\n    #     .limit(required_jets)\n    # Mock available jets\n    available_jets = [\n        {\"id\": \"jet-001\", \"tail_number\": \"J20-1001\", \"status\": \"READY\"},\n        {\"id\": \"jet-002\", \"tail_number\": \"J20-1002\", \"status\": \"READY\"},\n        {\"id\": \"jet-003\", \"tail_number\": \"J20-1003\", \"status\": \"READY\"},\n    ][:required_jets]\n    if len(available_jets) < required_jets:\n        error_msg = f\"Insufficient J-20 assets: need {required_jets}, found {len(available_jets)}\"\n        print(f\"[Mission Assign] ERROR: {error_msg}\")\n        raise Exception(error_msg)\n    # Assign jets to mission\n    assigned_jets = []\n    for jet in available_jets:\n        # In production: \n        # mission.link(\"assigned_assets\", jet)\n        # jet.status = \"ASSIGNED\"\n        # jet.save()\n        assigned_jets.append(jet[\"tail_number\"])\n        print(f\"[Mission Assign] Assigned jet: {jet[\"tail_number\"]}\")\n    return {\n        \"success\": True,\n        \"mission_code\": mission_code,\n        \"mission_type\": mission_type,\n        \"assigned_jets\": assigned_jets,\n        \"jet_count\": len(assigned_jets),\n        \"message\": f\"Mission {mission_code} created with {len(assigned_jets)} jets assigned\"\n    }\n',NULL,'根据作战计划创建任务，查询可用J-20战机并分配到任务','[{\"name\": \"plan_id\", \"type\": \"string\", \"required\": true, \"description\": \"作战计划ID\"}, {\"name\": \"mission_type\", \"type\": \"string\", \"default\": \"Precision Strike\", \"required\": false, \"description\": \"任务类型\"}, {\"name\": \"required_jets\", \"type\": \"number\", \"default\": 2, \"required\": false, \"description\": \"需要的战机数量\"}]','OBJECT');
/*!40000 ALTER TABLE `meta_function_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `meta_link_type`
--

DROP TABLE IF EXISTS `meta_link_type`;
/*!50001 DROP VIEW IF EXISTS `meta_link_type`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_link_type` AS SELECT 
 1 AS `id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `source_type_id`,
 1 AS `target_type_id`,
 1 AS `cardinality`,
 1 AS `created_at`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `meta_link_type_def`
--

DROP TABLE IF EXISTS `meta_link_type_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_link_type_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_version_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '当前激活版本',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='链接类型定义（不可变标识）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_link_type_def`
--

LOCK TABLES `meta_link_type_def` WRITE;
/*!40000 ALTER TABLE `meta_link_type_def` DISABLE KEYS */;
INSERT INTO `meta_link_type_def` VALUES ('22e3da28-bef1-46bf-99d1-bc645089b06d','aaa','51793bdc-1d07-4f27-b64e-c079d1f25b5a','2026-01-30 08:26:33'),('381652b1-7f35-4e58-926e-ab2050e02f7d','test_link_rel_0ff5ffce','ea72f7a8-e274-4872-b79d-c587abaefa45','2026-01-29 06:44:21'),('4360a5a6-9e8e-4dfe-b39f-9841c65f3032','test_link_rel','c13ea21a-6b0e-43f9-869f-ee3754efb7f6','2026-01-29 06:35:49'),('9600e4c0-46bc-4173-a826-30641a129255','test_link_map_d6114c5f','d83f3bf8-42e9-4b10-903f-e3979ba8c068','2026-01-29 06:44:22'),('c4f73e74-0e85-4efb-aded-b57b062044a0','test_link_map','089a456c-ca5c-4cf5-a293-50f39d878866','2026-01-29 06:35:50'),('linktype-report-image-001','report_references_image','linkver-00d41da9','2026-01-26 06:52:58'),('linktype-target-image-001','target_captured_in_image','linkver-d7510624','2026-01-26 06:52:58'),('linktype-target-report-001','target_mentioned_in_report','linkver-fa0457ad','2026-01-26 06:52:58');
/*!40000 ALTER TABLE `meta_link_type_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_link_type_ver`
--

DROP TABLE IF EXISTS `meta_link_type_ver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_link_type_ver` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cardinality` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'DRAFT',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `source_key_column` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Source table key column (usually primary key)',
  `target_key_column` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Target table key column (foreign key for 1:N, or join key)',
  PRIMARY KEY (`id`),
  KEY `def_id` (`def_id`),
  KEY `source_object_def_id` (`source_object_def_id`),
  KEY `target_object_def_id` (`target_object_def_id`),
  CONSTRAINT `meta_link_type_ver_ibfk_1` FOREIGN KEY (`def_id`) REFERENCES `meta_link_type_def` (`id`),
  CONSTRAINT `meta_link_type_ver_ibfk_2` FOREIGN KEY (`source_object_def_id`) REFERENCES `meta_object_type_def` (`id`),
  CONSTRAINT `meta_link_type_ver_ibfk_3` FOREIGN KEY (`target_object_def_id`) REFERENCES `meta_object_type_def` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='链接类型版本';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_link_type_ver`
--

LOCK TABLES `meta_link_type_ver` WRITE;
/*!40000 ALTER TABLE `meta_link_type_ver` DISABLE KEYS */;
INSERT INTO `meta_link_type_ver` VALUES ('089a456c-ca5c-4cf5-a293-50f39d878866','c4f73e74-0e85-4efb-aded-b57b062044a0','1.0','test_link_map','6af67b06-ba14-4102-bd7b-dc8a5f9d09a4','2afa0af0-a4c7-492d-b5ee-97873065e258','MANY_TO_MANY','DRAFT','2026-01-29 06:35:50',NULL,NULL),('51793bdc-1d07-4f27-b64e-c079d1f25b5a','22e3da28-bef1-46bf-99d1-bc645089b06d','1.0','aaa','objtype-target-001','objtype-intel-report-001','MANY_TO_MANY','DRAFT','2026-01-30 08:26:33',NULL,NULL),('c13ea21a-6b0e-43f9-869f-ee3754efb7f6','4360a5a6-9e8e-4dfe-b39f-9841c65f3032','1.0','Test Link','e1c42d5d-8555-4bf1-b1db-2fbe5a5eb7bd','5ac513a9-0c41-45c3-ba9f-937680dc7e77','MANY_TO_MANY','DRAFT','2026-01-29 06:35:49',NULL,NULL),('d83f3bf8-42e9-4b10-903f-e3979ba8c068','9600e4c0-46bc-4173-a826-30641a129255','1.0','test_link_map_d6114c5f','fcd2e967-4b89-4222-ada3-57b3d5953333','c340710e-b7a6-4e3d-aca7-86677a7f32ec','MANY_TO_MANY','DRAFT','2026-01-29 06:44:22',NULL,NULL),('ea72f7a8-e274-4872-b79d-c587abaefa45','381652b1-7f35-4e58-926e-ab2050e02f7d','1.0','Test Link','cd75487b-9a7b-43b9-8e67-8bb00a80c20a','cd88ccdc-2c85-445d-8aea-c297b0570250','MANY_TO_MANY','DRAFT','2026-01-29 06:44:21',NULL,NULL),('linkver-00d41da9','linktype-report-image-001','1.0','报告引用图像','objtype-intel-report-001','objtype-recon-image-001','ONE_TO_MANY','PUBLISHED','2026-01-26 06:52:58','id','report_id'),('linkver-d7510624','linktype-target-image-001','1.0','目标在图像中出现','objtype-target-001','objtype-recon-image-001','ONE_TO_MANY','PUBLISHED','2026-01-26 06:52:58','id','target_id'),('linkver-fa0457ad','linktype-target-report-001','1.0','目标在报告中提及','objtype-target-001','objtype-intel-report-001','MANY_TO_MANY','PUBLISHED','2026-01-26 06:52:58','id','id');
/*!40000 ALTER TABLE `meta_link_type_ver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `meta_object_type`
--

DROP TABLE IF EXISTS `meta_object_type`;
/*!50001 DROP VIEW IF EXISTS `meta_object_type`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_object_type` AS SELECT 
 1 AS `id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `description`,
 1 AS `property_schema`,
 1 AS `project_id`,
 1 AS `created_at`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `meta_object_type_def`
--

DROP TABLE IF EXISTS `meta_object_type_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_object_type_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `stereotype` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'ENTITY' COMMENT 'ENTITY, EVENT, DOCUMENT, MEDIA, METRIC',
  `current_version_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '当前激活版本',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对象类型定义（不可变标识）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_object_type_def`
--

LOCK TABLES `meta_object_type_def` WRITE;
/*!40000 ALTER TABLE `meta_object_type_def` DISABLE KEYS */;
INSERT INTO `meta_object_type_def` VALUES ('2afa0af0-a4c7-492d-b5ee-97873065e258','test_tgt_map','ENTITY','0b9cd89a-248b-4790-9836-d9b05c295128','2026-01-29 06:35:50'),('598fd87c-d87d-47e0-ae58-c3505fdf188a','obj1','ENTITY','0f5199b3-eb4b-4f29-9429-f85758fbfa67','2026-01-29 01:05:29'),('5ac513a9-0c41-45c3-ba9f-937680dc7e77','test_tgt_obj','ENTITY','22dcee7f-4172-4aa3-9e32-46ccea1d7c85','2026-01-29 06:35:49'),('6af67b06-ba14-4102-bd7b-dc8a5f9d09a4','test_src_map','ENTITY','0a7e034c-7e50-4d36-a70f-18f9bf850d5d','2026-01-29 06:35:50'),('6fc14db9-d764-4cc7-9fff-8c9786c13b39','e2e_plane','ENTITY','38b5bec5-f178-4e82-b358-51290ac84c56','2026-01-29 06:35:51'),('95e3aa24-275e-42ab-8815-451109f46e28','bbb','ENTITY','6e6ea83e-869f-4fa6-bffb-2235347ab0d5','2026-01-29 01:11:54'),('a35c8789-b766-4e3e-944a-425930a70450','test_v3_object','ENTITY','624b3af6-3418-419b-aff3-b61434190477','2026-01-29 06:39:47'),('ac684509-6193-4dff-842e-3caf1721fbbb','e2e_plane_aa03629d','ENTITY','7c812c74-8c10-46e8-b1a2-64ad0e6f4ba1','2026-01-29 06:46:49'),('c340710e-b7a6-4e3d-aca7-86677a7f32ec','test_tgt_map_daaa2d76','ENTITY','bd88b3b0-8b0e-4dc6-88fe-9c65d72b1003','2026-01-29 06:44:22'),('cd75487b-9a7b-43b9-8e67-8bb00a80c20a','test_src_obj_5d6341d5','ENTITY','f40d98c5-224f-4b1f-92de-5177625726d4','2026-01-29 06:44:21'),('cd88ccdc-2c85-445d-8aea-c297b0570250','test_tgt_obj_31489b5e','ENTITY','1ca3150a-51d6-4a76-83fd-ad36713ea7e9','2026-01-29 06:44:21'),('e1c42d5d-8555-4bf1-b1db-2fbe5a5eb7bd','test_src_obj','ENTITY','bf38b1f1-d8a0-49a5-bee6-894420cc62f4','2026-01-29 06:35:49'),('f1b78787-6323-4cc1-9850-72e1036557a7','aaaa','ENTITY','0fe5eeb9-f54e-49b0-89c9-0534a6306e1e','2026-01-29 01:08:57'),('fc9c9f0f-811b-4204-b6e0-33208541563f','e2e_plane_1166844e','ENTITY','959c2083-e648-408d-ba35-7b3ec50714bb','2026-01-29 06:44:23'),('fcd2e967-4b89-4222-ada3-57b3d5953333','test_src_map_91d09e74','ENTITY','e5e4fdb5-ed90-4bd7-94c6-835eee596690','2026-01-29 06:44:22'),('objtype-intel-report-001','IntelReport','DOCUMENT','ver-db20a136','2026-01-26 06:52:58'),('objtype-recon-image-001','ReconImage','MEDIA','ver-40568975','2026-01-26 06:52:58'),('objtype-target-001','Target','ENTITY','ver-98996315','2026-01-26 06:52:58');
/*!40000 ALTER TABLE `meta_object_type_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_object_type_ver`
--

DROP TABLE IF EXISTS `meta_object_type_ver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_object_type_ver` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `icon` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '图标名称或URL',
  `color` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '主题色 HEX',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'DRAFT' COMMENT 'DRAFT, PUBLISHED, DEPRECATED',
  `enable_global_search` tinyint(1) DEFAULT '0' COMMENT '启用全文搜索',
  `enable_geo_index` tinyint(1) DEFAULT '0' COMMENT '启用地理索引',
  `enable_vector_index` tinyint(1) DEFAULT '0' COMMENT '启用向量索引(AI)',
  `cache_ttl_seconds` int DEFAULT '0' COMMENT '缓存生存时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `def_id` (`def_id`),
  CONSTRAINT `meta_object_type_ver_ibfk_1` FOREIGN KEY (`def_id`) REFERENCES `meta_object_type_def` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对象类型版本（包含具体配置）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_object_type_ver`
--

LOCK TABLES `meta_object_type_ver` WRITE;
/*!40000 ALTER TABLE `meta_object_type_ver` DISABLE KEYS */;
INSERT INTO `meta_object_type_ver` VALUES ('0a7e034c-7e50-4d36-a70f-18f9bf850d5d','6af67b06-ba14-4102-bd7b-dc8a5f9d09a4','1.0','test_src_map',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:35:50'),('0b9cd89a-248b-4790-9836-d9b05c295128','2afa0af0-a4c7-492d-b5ee-97873065e258','1.0','test_tgt_map',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:35:50'),('0f5199b3-eb4b-4f29-9429-f85758fbfa67','598fd87c-d87d-47e0-ae58-c3505fdf188a','v1.0','obj1',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 01:05:30'),('0fe5eeb9-f54e-49b0-89c9-0534a6306e1e','f1b78787-6323-4cc1-9850-72e1036557a7','v1.0','aaaa',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 01:08:57'),('1ca3150a-51d6-4a76-83fd-ad36713ea7e9','cd88ccdc-2c85-445d-8aea-c297b0570250','1.0','test_tgt_obj_31489b5e',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:44:21'),('22dcee7f-4172-4aa3-9e32-46ccea1d7c85','5ac513a9-0c41-45c3-ba9f-937680dc7e77','1.0','test_tgt_obj',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:35:49'),('38b5bec5-f178-4e82-b358-51290ac84c56','6fc14db9-d764-4cc7-9fff-8c9786c13b39','1.0','e2e_plane',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:35:51'),('5faec05c-7250-4114-b08b-ecc2d0d303dd','a35c8789-b766-4e3e-944a-425930a70450','1.0','test_v3_object',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:39:47'),('624b3af6-3418-419b-aff3-b61434190477','a35c8789-b766-4e3e-944a-425930a70450','1.1','V3 Object v1.1',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:39:47'),('6e6ea83e-869f-4fa6-bffb-2235347ab0d5','95e3aa24-275e-42ab-8815-451109f46e28','v1.0','bbb',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 01:11:54'),('7c812c74-8c10-46e8-b1a2-64ad0e6f4ba1','ac684509-6193-4dff-842e-3caf1721fbbb','1.0','e2e_plane_aa03629d',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:46:49'),('959c2083-e648-408d-ba35-7b3ec50714bb','fc9c9f0f-811b-4204-b6e0-33208541563f','1.0','e2e_plane_1166844e',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:44:23'),('bd88b3b0-8b0e-4dc6-88fe-9c65d72b1003','c340710e-b7a6-4e3d-aca7-86677a7f32ec','1.0','test_tgt_map_daaa2d76',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:44:22'),('bf38b1f1-d8a0-49a5-bee6-894420cc62f4','e1c42d5d-8555-4bf1-b1db-2fbe5a5eb7bd','1.0','test_src_obj',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:35:49'),('e5e4fdb5-ed90-4bd7-94c6-835eee596690','fcd2e967-4b89-4222-ada3-57b3d5953333','1.0','test_src_map_91d09e74',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:44:22'),('f40d98c5-224f-4b1f-92de-5177625726d4','cd75487b-9a7b-43b9-8e67-8bb00a80c20a','1.0','test_src_obj_5d6341d5',NULL,NULL,NULL,'DRAFT',0,0,0,0,'2026-01-29 06:44:21'),('ver-40568975','objtype-recon-image-001','1.0','侦察图像','Reconnaissance and satellite imagery','CameraOutlined','#722ed1','PUBLISHED',1,1,1,0,'2026-01-26 06:52:58'),('ver-98996315','objtype-target-001','1.0','海上目标','Maritime vessel/target tracking data','AimOutlined','#1890ff','PUBLISHED',1,1,1,0,'2026-01-26 06:52:58'),('ver-db20a136','objtype-intel-report-001','1.0','情报报告','Intelligence reports and analysis documents','FileTextOutlined','#52c41a','PUBLISHED',1,1,1,0,'2026-01-26 06:52:58');
/*!40000 ALTER TABLE `meta_object_type_ver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `meta_project`
--

DROP TABLE IF EXISTS `meta_project`;
/*!50001 DROP VIEW IF EXISTS `meta_project`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_project` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `description`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `meta_shared_property`
--

DROP TABLE IF EXISTS `meta_shared_property`;
/*!50001 DROP VIEW IF EXISTS `meta_shared_property`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_shared_property` AS SELECT 
 1 AS `id`,
 1 AS `project_id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `data_type`,
 1 AS `formatter`,
 1 AS `description`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `meta_shared_property_def`
--

DROP TABLE IF EXISTS `meta_shared_property_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_shared_property_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'STRING, INT, DOUBLE, BOOLEAN, DATETIME, GEO_POINT, JSON, VECTOR, MEDIA_REF',
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='全局共享属性定义池，可被多个对象类型复用';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_shared_property_def`
--

LOCK TABLES `meta_shared_property_def` WRITE;
/*!40000 ALTER TABLE `meta_shared_property_def` DISABLE KEYS */;
INSERT INTO `meta_shared_property_def` VALUES ('14fecb66-55eb-49bc-8f29-7ee4737999dc','tail_number_0dbd5b0f',NULL,'STRING',NULL,'2026-01-29 06:44:23'),('15db4547-aa4e-414b-a65a-c660eab5891c','tail_number',NULL,'STRING',NULL,'2026-01-29 06:35:51'),('4ee58671-ec4f-4e21-9544-fe8f6d1fa289','id','ID','STRING','Property for test_studio_object','2026-01-28 08:47:28'),('7e21d555-6f01-4f2e-80c6-34aaedac6cca','test_v3_obj_prop',NULL,'INTEGER',NULL,'2026-01-29 06:35:49'),('cbef8255-b63d-4fd0-b320-21baa37cee55','_sync_timestamp','_sync_timestamp','DATE','Property for new_object_type','2026-01-28 08:22:43'),('fa698b46-3d48-419f-8027-eb4f7217a817','tail_number_58a85741',NULL,'STRING',NULL,'2026-01-29 06:46:49'),('prop-22345928','lon','经度','DOUBLE',NULL,'2026-01-26 06:52:58'),('prop-29fb1491','sensor_type','传感器类型','STRING',NULL,'2026-01-26 06:52:58'),('prop-2a75e156','classification','密级','STRING',NULL,'2026-01-26 06:52:58'),('prop-3508c6b4','title','标题','STRING',NULL,'2026-01-26 06:52:58'),('prop-3974fe59','mmsi','MMSI','STRING',NULL,'2026-01-26 06:52:58'),('prop-40148a4e','last_seen','最后发现','DATETIME',NULL,'2026-01-26 06:52:58'),('prop-46b58a2e','region','区域','STRING',NULL,'2026-01-26 06:52:58'),('prop-5c1ed6d8','content','内容摘要','STRING',NULL,'2026-01-26 06:52:58'),('prop-65122a5a','heading','航向','INT',NULL,'2026-01-26 06:52:58'),('prop-74d153e4','location','位置描述','STRING',NULL,'2026-01-26 06:52:58'),('prop-86183af6','created_at','创建时间','DATETIME',NULL,'2026-01-26 06:52:58'),('prop-8c85c8d0','lat','纬度','DOUBLE',NULL,'2026-01-26 06:52:58'),('prop-9fe79d59','capture_time','拍摄时间','DATETIME',NULL,'2026-01-26 06:52:58'),('prop-ad6f7635','name','船名','STRING','\n[CONSTRAINTS:{\"regex_pattern\":\"[A-Z0-9]\",\"min_length\":1,\"max_length\":10}]','2026-01-26 06:52:58'),('prop-b5bde07b','file_path','文件路径','STRING',NULL,'2026-01-26 06:52:58'),('prop-c37061f3','length','船长(m)','DOUBLE',NULL,'2026-01-26 06:52:58'),('prop-c722b6ba','vessel_type','船型','STRING',NULL,'2026-01-26 06:52:58'),('prop-c7939262','image_id','图像ID','STRING',NULL,'2026-01-26 06:52:58'),('prop-cc7cd59b','filename','文件名','STRING',NULL,'2026-01-26 06:52:58'),('prop-d0b1eab0','flag','船旗国','STRING',NULL,'2026-01-26 06:52:58'),('prop-ea97ac82','resolution','分辨率','STRING',NULL,'2026-01-26 06:52:58'),('prop-ec5b4c23','source','来源','STRING',NULL,'2026-01-26 06:52:58'),('prop-efcfd454','speed','航速(节)','DOUBLE',NULL,'2026-01-26 06:52:58'),('prop-f1318fcb','report_id','报告编号','STRING',NULL,'2026-01-26 06:52:58');
/*!40000 ALTER TABLE `meta_shared_property_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rel_link_ver_property`
--

DROP TABLE IF EXISTS `rel_link_ver_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rel_link_ver_property` (
  `id` int NOT NULL AUTO_INCREMENT,
  `link_ver_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `property_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `local_api_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_link_property` (`link_ver_id`,`property_def_id`),
  KEY `property_def_id` (`property_def_id`),
  CONSTRAINT `rel_link_ver_property_ibfk_1` FOREIGN KEY (`link_ver_id`) REFERENCES `meta_link_type_ver` (`id`) ON DELETE CASCADE,
  CONSTRAINT `rel_link_ver_property_ibfk_2` FOREIGN KEY (`property_def_id`) REFERENCES `meta_shared_property_def` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='链接版本与属性的关联关系';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rel_link_ver_property`
--

LOCK TABLES `rel_link_ver_property` WRITE;
/*!40000 ALTER TABLE `rel_link_ver_property` DISABLE KEYS */;
/*!40000 ALTER TABLE `rel_link_ver_property` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rel_object_ver_property`
--

DROP TABLE IF EXISTS `rel_object_ver_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rel_object_ver_property` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_ver_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `property_def_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `local_api_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '本地别名，可覆盖共享属性名',
  `local_display_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `local_data_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_primary_key` tinyint(1) DEFAULT '0',
  `is_required` tinyint(1) DEFAULT '0',
  `is_title` tinyint(1) DEFAULT '0' COMMENT '作为对象标题显示',
  `default_value` text COLLATE utf8mb4_unicode_ci COMMENT '默认值',
  `validation_rules` json DEFAULT NULL COMMENT '验证规则',
  `is_searchable` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Enable full-text search indexing',
  `is_filterable` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Enable facet/aggregation indexing',
  `is_sortable` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Enable sorting capability',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_ver_property` (`object_ver_id`,`property_def_id`),
  KEY `property_def_id` (`property_def_id`),
  CONSTRAINT `rel_object_ver_property_ibfk_1` FOREIGN KEY (`object_ver_id`) REFERENCES `meta_object_type_ver` (`id`) ON DELETE CASCADE,
  CONSTRAINT `rel_object_ver_property_ibfk_2` FOREIGN KEY (`property_def_id`) REFERENCES `meta_shared_property_def` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对象版本与属性的关联关系';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rel_object_ver_property`
--

LOCK TABLES `rel_object_ver_property` WRITE;
/*!40000 ALTER TABLE `rel_object_ver_property` DISABLE KEYS */;
INSERT INTO `rel_object_ver_property` VALUES (1,'ver-98996315','prop-3974fe59','mmsi',NULL,NULL,1,0,0,NULL,NULL,0,1,0),(2,'ver-98996315','prop-ad6f7635','name',NULL,NULL,0,0,1,NULL,NULL,1,0,0),(3,'ver-98996315','prop-c722b6ba','vessel_type',NULL,NULL,0,0,0,NULL,NULL,0,1,0),(4,'ver-98996315','prop-d0b1eab0','flag',NULL,NULL,0,0,0,NULL,NULL,0,1,0),(5,'ver-98996315','prop-c37061f3','length',NULL,NULL,0,0,0,NULL,NULL,0,0,1),(6,'ver-98996315','prop-8c85c8d0','lat',NULL,NULL,0,0,0,NULL,NULL,0,0,0),(7,'ver-98996315','prop-22345928','lon',NULL,NULL,0,0,0,NULL,NULL,0,0,0),(8,'ver-98996315','prop-efcfd454','speed',NULL,NULL,0,0,0,NULL,NULL,0,0,1),(9,'ver-98996315','prop-65122a5a','heading',NULL,NULL,0,0,0,NULL,NULL,0,0,0),(10,'ver-98996315','prop-40148a4e','last_seen',NULL,NULL,0,0,0,NULL,NULL,0,0,1),(11,'ver-db20a136','prop-f1318fcb','report_id','report_id','STRING',1,0,0,NULL,NULL,0,1,0),(12,'ver-db20a136','prop-3508c6b4','title','title','STRING',0,0,1,NULL,NULL,1,0,0),(13,'ver-db20a136','prop-5c1ed6d8','content','content','STRING',0,0,0,NULL,NULL,1,0,0),(14,'ver-db20a136','prop-2a75e156','classification','classification','STRING',0,0,0,NULL,NULL,0,1,0),(15,'ver-db20a136','prop-ec5b4c23','source','source','STRING',0,0,0,NULL,NULL,0,1,0),(16,'ver-db20a136','prop-46b58a2e','region','region','STRING',0,0,0,NULL,NULL,0,1,0),(17,'ver-db20a136','prop-86183af6','created_at','created_at','DATE',0,0,0,NULL,NULL,0,0,1),(18,'ver-40568975','prop-c7939262','image_id',NULL,NULL,1,0,0,NULL,NULL,0,0,0),(19,'ver-40568975','prop-cc7cd59b','filename',NULL,NULL,0,0,1,NULL,NULL,1,0,0),(20,'ver-40568975','prop-9fe79d59','capture_time',NULL,NULL,0,0,0,NULL,NULL,0,0,1),(21,'ver-40568975','prop-29fb1491','sensor_type',NULL,NULL,0,0,0,NULL,NULL,0,1,0),(22,'ver-40568975','prop-ea97ac82','resolution',NULL,NULL,0,0,0,NULL,NULL,0,1,0),(23,'ver-40568975','prop-74d153e4','location',NULL,NULL,0,0,0,NULL,NULL,1,0,0),(24,'ver-40568975','prop-b5bde07b','file_path',NULL,NULL,0,0,0,NULL,NULL,0,0,0),(93,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'id','id','STRING',1,0,0,NULL,'null',0,0,0),(94,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'mmsi','mmsi','STRING',0,0,0,NULL,'null',0,0,0),(95,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'name','name','STRING',0,0,0,NULL,'null',0,0,0),(96,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'vessel_type','vessel_type','STRING',0,0,0,NULL,'null',0,0,0),(97,'0f5199b3-eb4b-4f29-9429-f85758fbfa67','prop-d0b1eab0','flag','flag','STRING',0,0,0,NULL,'null',0,0,0),(99,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'lon','lon','STRING',0,0,0,NULL,'null',0,0,0),(101,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'heading','heading','STRING',0,0,0,NULL,'null',0,0,0),(102,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'last_seen','last_seen','DATE',0,0,0,NULL,'null',0,0,0),(103,'0f5199b3-eb4b-4f29-9429-f85758fbfa67',NULL,'_sync_timestamp','_sync_timestamp','DATE',0,0,0,NULL,'null',0,0,0),(104,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'id','id','STRING',1,1,0,NULL,'null',0,0,0),(105,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'image_id','image_id','STRING',0,0,0,NULL,'null',0,0,0),(106,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'filename','filename','STRING',0,0,0,NULL,'null',0,0,0),(107,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'capture_time','capture_time','DATE',0,0,0,NULL,'null',0,0,0),(108,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'sensor_type','sensor_type','STRING',0,0,0,NULL,'null',0,0,0),(109,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'resolution','resolution','STRING',0,0,0,NULL,'null',0,0,0),(110,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'location','location','STRING',0,0,0,NULL,'null',0,0,0),(111,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'file_path','file_path','STRING',0,0,0,NULL,'null',0,0,0),(112,'0fe5eeb9-f54e-49b0-89c9-0534a6306e1e',NULL,'_sync_timestamp','_sync_timestamp','DATE',0,0,0,NULL,'null',0,0,0),(113,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'id','id','STRING',1,1,0,NULL,'null',0,0,0),(114,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'image_id','image_id','STRING',0,0,0,NULL,'null',0,0,0),(115,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'filename','filename','STRING',0,0,0,NULL,'null',0,0,0),(116,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'capture_time','capture_time','DATE',0,0,0,NULL,'null',0,0,0),(117,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'sensor_type','sensor_type','STRING',0,0,0,NULL,'null',0,0,0),(118,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'resolution','resolution','STRING',0,0,0,NULL,'null',0,0,0),(119,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'location','location','STRING',0,0,0,NULL,'null',0,0,0),(120,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'file_path','file_path','STRING',0,0,0,NULL,'null',0,0,0),(121,'6e6ea83e-869f-4fa6-bffb-2235347ab0d5',NULL,'_sync_timestamp','_sync_timestamp','DATE',0,0,0,NULL,'null',0,0,0),(123,'38b5bec5-f178-4e82-b358-51290ac84c56','15db4547-aa4e-414b-a65a-c660eab5891c',NULL,NULL,NULL,0,0,1,NULL,'null',0,0,0),(125,'959c2083-e648-408d-ba35-7b3ec50714bb','14fecb66-55eb-49bc-8f29-7ee4737999dc',NULL,NULL,NULL,0,0,1,NULL,'null',0,0,0),(127,'7c812c74-8c10-46e8-b1a2-64ad0e6f4ba1','fa698b46-3d48-419f-8027-eb4f7217a817',NULL,NULL,NULL,0,0,1,NULL,'null',0,0,0),(132,'ver-db20a136',NULL,'aaa','aaa','STRING',0,0,0,NULL,'null',0,0,0);
/*!40000 ALTER TABLE `rel_object_ver_property` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rel_target_report`
--

DROP TABLE IF EXISTS `rel_target_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rel_target_report` (
  `id` varchar(36) NOT NULL,
  `target_id` varchar(36) NOT NULL COMMENT 'FK to Target object',
  `report_id` varchar(36) NOT NULL COMMENT 'FK to IntelReport object',
  `mention_type` varchar(50) DEFAULT 'DIRECT' COMMENT 'Type of mention: DIRECT, INDIRECT, INFERRED',
  `confidence_score` decimal(5,2) DEFAULT '1.00' COMMENT 'Confidence of the mention (0.00-1.00)',
  `context_snippet` text COMMENT 'Text snippet where target is mentioned',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_target_report` (`target_id`,`report_id`),
  KEY `idx_target_id` (`target_id`),
  KEY `idx_report_id` (`report_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Join table for Target <-> IntelReport N:N relationship';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rel_target_report`
--

LOCK TABLES `rel_target_report` WRITE;
/*!40000 ALTER TABLE `rel_target_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `rel_target_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_action_log`
--

DROP TABLE IF EXISTS `sys_action_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_action_log` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trigger_user_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Trigger User ID',
  `input_params` json DEFAULT NULL COMMENT 'Input Parameters',
  `execution_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'SUCCESS, FAILED',
  `error_message` text COLLATE utf8mb4_unicode_ci,
  `duration_ms` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_action_log`
--

LOCK TABLES `sys_action_log` WRITE;
/*!40000 ALTER TABLE `sys_action_log` DISABLE KEYS */;
INSERT INTO `sys_action_log` VALUES ('1d47a3ad-ebf8-4227-9252-9aa5042e7cc5','proj-001','44618028-8477-4bf7-a906-da821c9e7070','user-002','{\"param1\": \"value2\", \"source_id\": \"obj-002\"}','SUCCESS',NULL,230,'2026-01-24 20:45:27'),('9b8c1037-3765-4b52-8ae0-9f7274b419b1','proj-001','44618028-8477-4bf7-a906-da821c9e7070',NULL,'{\"batch\": true, \"source_id\": \"obj-004\"}','SUCCESS',NULL,89,'2026-01-24 21:15:27'),('a53ecc8f-7906-4798-b0dd-cb9ff7eb690f','default-project','act_intel_verify_01',NULL,'{\"object_id\": \"target-48a103fa\", \"timestamp\": \"2026-01-26T14:53:35.673291\", \"object_type\": \"Target\", \"new_threat_level\": \"HIGH\", \"verification_source\": \"E2E_TEST\"}','SUCCESS',NULL,9,'2026-01-26 14:53:36'),('abc448e7-95a1-47c5-82b8-5efd4fb93f75','proj-001','44618028-8477-4bf7-a906-da821c9e7070','user-001','{\"param1\": \"value1\", \"source_id\": \"obj-001\"}','SUCCESS',NULL,150,'2026-01-24 20:15:27'),('df8afaa8-f2db-4786-bbe1-45f6d0c6d6f3','proj-001','44618028-8477-4bf7-a906-da821c9e7070','user-001','{\"source_id\": \"obj-003\"}','FAILED','Test error: Connection timeout',5000,'2026-01-24 21:00:27');
/*!40000 ALTER TABLE `sys_action_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_connection`
--

DROP TABLE IF EXISTS `sys_connection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_connection` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `conn_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MYSQL',
  `config_json` json NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVE',
  `error_message` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_tested_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_connection`
--

LOCK TABLES `sys_connection` WRITE;
/*!40000 ALTER TABLE `sys_connection` DISABLE KEYS */;
INSERT INTO `sys_connection` VALUES ('190f434f-da70-4c30-9fbe-63e2a87eaf45','mysql-source','MYSQL','{\"host\": \"localhost\", \"port\": 3306, \"user\": \"root\", \"database\": \"mdp_raw_store\", \"password\": \"Ga0binGB\"}','ACTIVE',NULL,'2026-01-28 12:56:42','2026-01-25 14:16:12','2026-01-28 12:56:56');
/*!40000 ALTER TABLE `sys_connection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dataset`
--

DROP TABLE IF EXISTS `sys_dataset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dataset` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `connection_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `location_config` json NOT NULL COMMENT '数据位置：表名/S3路径/API端点等',
  `cached_schema` json DEFAULT NULL COMMENT '缓存的数据结构schema',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集定义，指向具体的数据表/文件/API';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dataset`
--

LOCK TABLES `sys_dataset` WRITE;
/*!40000 ALTER TABLE `sys_dataset` DISABLE KEYS */;
INSERT INTO `sys_dataset` VALUES ('dataset-rel-target-report','190f434f-da70-4c30-9fbe-63e2a87eaf45','rel_target_report','{\"table\": \"rel_target_report\", \"schema\": \"mdp_raw_store\"}','{\"columns\": [{\"name\": \"id\", \"type\": \"VARCHAR(36)\"}, {\"name\": \"target_id\", \"type\": \"VARCHAR(50)\"}, {\"name\": \"report_id\", \"type\": \"VARCHAR(50)\"}, {\"name\": \"created_at\", \"type\": \"DATETIME\"}]}'),('ds-device-001','conn-mysql-001','Device Registry','{\"table\": \"devices\", \"schema\": \"iot_raw_data\"}','{\"columns\": [{\"name\": \"device_id\", \"type\": \"VARCHAR(50)\"}, {\"name\": \"device_name\", \"type\": \"VARCHAR(100)\"}, {\"name\": \"location\", \"type\": \"VARCHAR(200)\"}, {\"name\": \"status\", \"type\": \"VARCHAR(20)\"}]}'),('ds-docs-001','conn-s3-001','PDF Documents','{\"file_format\": \"PDF\", \"path_pattern\": \"documents*.pdf\"}',NULL),('ds-images-001','conn-s3-001','Image Assets','{\"file_format\": \"IMAGE\", \"path_pattern\": \"images*.{jpg,png}\"}',NULL),('ds-locations-001','conn-pg-001','Facility Locations','{\"table\": \"facilities\", \"geometry_column\": \"geom\"}','{\"columns\": [{\"name\": \"id\", \"type\": \"UUID\"}, {\"name\": \"name\", \"type\": \"VARCHAR(200)\"}, {\"name\": \"geom\", \"type\": \"GEOMETRY(Point, 4326)\"}, {\"name\": \"category\", \"type\": \"VARCHAR(50)\"}]}'),('ds-sensor-001','conn-mysql-001','Sensor Readings','{\"table\": \"sensor_readings\", \"schema\": \"iot_raw_data\"}','{\"columns\": [{\"name\": \"id\", \"type\": \"BIGINT\"}, {\"name\": \"device_id\", \"type\": \"VARCHAR(50)\"}, {\"name\": \"temperature\", \"type\": \"DECIMAL(5,2)\"}, {\"name\": \"humidity\", \"type\": \"DECIMAL(5,2)\"}, {\"name\": \"timestamp\", \"type\": \"DATETIME\"}]}');
/*!40000 ALTER TABLE `sys_dataset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `sys_datasource_table`
--

DROP TABLE IF EXISTS `sys_datasource_table`;
/*!50001 DROP VIEW IF EXISTS `sys_datasource_table`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sys_datasource_table` AS SELECT 
 1 AS `id`,
 1 AS `connection_id`,
 1 AS `table_name`,
 1 AS `db_type`,
 1 AS `columns_schema`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sys_index_error_sample`
--

DROP TABLE IF EXISTS `sys_index_error_sample`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_index_error_sample` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `job_run_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '作业运行ID',
  `raw_row_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始数据行ID',
  `error_category` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '错误类别: SEMANTIC, AI_INFERENCE, MEDIA_IO, SYSTEM',
  `error_message` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '错误消息',
  `stack_trace` text COLLATE utf8mb4_unicode_ci COMMENT '堆栈跟踪 (可选)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_job_run_id` (`job_run_id`),
  KEY `idx_error_category` (`error_category`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='索引错误采样表 - Dead Letter Queue';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_index_error_sample`
--

LOCK TABLES `sys_index_error_sample` WRITE;
/*!40000 ALTER TABLE `sys_index_error_sample` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_index_error_sample` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_index_job_run`
--

DROP TABLE IF EXISTS `sys_index_job_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_index_job_run` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mapping_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '映射定义ID',
  `object_def_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对象类型ID',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'SUCCESS' COMMENT '状态: SUCCESS, PARTIAL_SUCCESS, FAILED',
  `rows_processed` int NOT NULL DEFAULT '0' COMMENT '处理的原始行数',
  `rows_indexed` int NOT NULL DEFAULT '0' COMMENT '成功索引的行数',
  `metrics_json` json DEFAULT NULL COMMENT '详细指标 (pk_collisions, ai_latency_avg_ms, etc.)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_mapping_id` (`mapping_id`),
  KEY `idx_object_def_id` (`object_def_id`),
  KEY `idx_status` (`status`),
  KEY `idx_start_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='索引作业运行记录 - 存储执行信息和健康指标';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_index_job_run`
--

LOCK TABLES `sys_index_job_run` WRITE;
/*!40000 ALTER TABLE `sys_index_job_run` DISABLE KEYS */;
INSERT INTO `sys_index_job_run` VALUES ('12ff92ab-ebe8-435f-867e-366d2a994df0','bee2ebd7-e052-49cc-9241-ee366f24f339','fc9c9f0f-811b-4204-b6e0-33208541563f','2026-01-29 14:44:24','2026-01-29 14:44:25','SUCCESS',2,2,'{\"pk_collisions\": 0, \"transform_errors\": 0, \"ai_latency_avg_ms\": 0, \"ai_inference_count\": 0, \"corrupt_media_files\": 0, \"vector_dim_mismatch\": 0, \"ai_low_confidence_count\": 0}','2026-01-29 14:44:25'),('19c511e2-290b-4f51-aeed-ee2e8e78020f','63b4f4c6-9546-4454-93af-467c734da700','6fc14db9-d764-4cc7-9fff-8c9786c13b39','2026-01-29 14:35:52','2026-01-29 14:35:53','SUCCESS',2,2,'{\"pk_collisions\": 0, \"transform_errors\": 0, \"ai_latency_avg_ms\": 0, \"ai_inference_count\": 0, \"corrupt_media_files\": 0, \"vector_dim_mismatch\": 0, \"ai_low_confidence_count\": 0}','2026-01-29 14:35:53'),('2643864b-9de2-45e5-ab72-6307c561df0e','e4333925-7a7b-49e7-bd35-b2ca9ffcf11e','4f37bc91-f949-4021-9b18-8c7bd09906a3','2026-01-29 14:56:49','2026-01-29 14:56:49','SUCCESS',2,2,'{\"pk_collisions\": 0, \"transform_errors\": 0, \"ai_latency_avg_ms\": 0, \"ai_inference_count\": 0, \"corrupt_media_files\": 0, \"vector_dim_mismatch\": 0, \"ai_low_confidence_count\": 0}','2026-01-29 14:56:49'),('6b422335-0db0-4261-ac91-bb9014416585','cfbdc6ff-21d6-460d-b937-4c3f39621e1a','96b03573-e3cf-4aad-a8b9-b8523209272c','2026-01-29 14:49:54','2026-01-29 14:49:55','SUCCESS',2,2,'{\"pk_collisions\": 0, \"transform_errors\": 0, \"ai_latency_avg_ms\": 0, \"ai_inference_count\": 0, \"corrupt_media_files\": 0, \"vector_dim_mismatch\": 0, \"ai_low_confidence_count\": 0}','2026-01-29 14:49:55'),('ae1957d1-55a7-421b-8fe6-0edb74435dc9','1474e2de-4db5-4a77-a45e-dc3b05fe466a','ac684509-6193-4dff-842e-3caf1721fbbb','2026-01-29 14:46:50','2026-01-29 14:46:50','SUCCESS',2,2,'{\"pk_collisions\": 0, \"transform_errors\": 0, \"ai_latency_avg_ms\": 0, \"ai_inference_count\": 0, \"corrupt_media_files\": 0, \"vector_dim_mismatch\": 0, \"ai_low_confidence_count\": 0}','2026-01-29 14:46:50');
/*!40000 ALTER TABLE `sys_index_job_run` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_link_instance`
--

DROP TABLE IF EXISTS `sys_link_instance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_link_instance` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `link_type_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_instance_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_instance_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_object_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_object_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `valid_start` datetime DEFAULT NULL,
  `valid_end` datetime DEFAULT NULL,
  `properties` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sys_link_instance_link_type_id` (`link_type_id`),
  KEY `idx_link_source` (`source_instance_id`),
  KEY `idx_link_target` (`target_instance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_link_instance`
--

LOCK TABLES `sys_link_instance` WRITE;
/*!40000 ALTER TABLE `sys_link_instance` DISABLE KEYS */;
INSERT INTO `sys_link_instance` VALUES ('112dc27c-fb2b-478f-a96e-4d953b9716b0','linktype-report-image-001','report-bac67d41','image-99fbec40',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('12eb43fd-8ec0-464e-b8fe-891f4e13c464','linktype-target-image-001','target-8d176c8d','image-9d9a8cce',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('230e78a4-d2de-46ef-8718-caf09cdaafb0','linktype-target-report-001','target-3d309474','report-48669e84',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('245e5239-403b-440e-8357-d4c51bd2fd64','linktype-target-report-001','target-e6904f08','report-ac3b89be',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('3171605a-f002-4d1a-8404-a1de4e8932a9','linktype-report-image-001','report-a7716421','image-92b5429b',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('7b511613-7195-4885-b926-915e583be14f','linktype-target-report-001','target-9cff89db','report-a7716421',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('9b7d8aac-234e-4e24-8c6a-d0768aca0754','linktype-target-image-001','target-e6904f08','image-99fbec40',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('be2dcacd-5318-465c-a9db-54b789bed8f5','linktype-target-image-001','target-3d309474','image-cf771130',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('c53ef8db-d5af-44c2-b229-a6e3c0582021','linktype-report-image-001','report-a76eaac9','image-cf771130',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('dcbfbd5d-92fe-4545-a9b1-de274eafafcb','linktype-target-report-001','target-84e8c7f4','report-a76eaac9',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('e72cf6ea-ab48-4904-b6df-6eb4c2174864','linktype-target-image-001','target-d3f7c483','image-92b5429b',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00'),('e9b20eb5-8b73-4963-997c-159a64cd4a6a','linktype-target-report-001','target-fc6dc2e8','report-bac67d41',NULL,NULL,NULL,NULL,'{}','2026-01-26 14:53:00');
/*!40000 ALTER TABLE `sys_link_instance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_object_instance`
--

DROP TABLE IF EXISTS `sys_object_instance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_object_instance` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_type_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `properties` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sys_object_instance_type_id` (`object_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_object_instance`
--

LOCK TABLES `sys_object_instance` WRITE;
/*!40000 ALTER TABLE `sys_object_instance` DISABLE KEYS */;
INSERT INTO `sys_object_instance` VALUES ('p1','fc9c9f0f-811b-4204-b6e0-33208541563f','\"{\\\"tail_number\\\": \\\"FN-001\\\", \\\"model\\\": \\\"F-16\\\"}\"','2026-01-29 14:44:25','2026-01-29 14:44:25');
/*!40000 ALTER TABLE `sys_object_instance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_pipeline_def`
--

DROP TABLE IF EXISTS `sys_pipeline_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_pipeline_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `object_ver_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标对象版本',
  `dataset_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '源数据集',
  `mode` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'VIRTUAL' COMMENT 'VIRTUAL(实时查询), MATERIALIZED(物化), MEDIA_EXTRACT(多媒体处理)',
  `transform_rules` json DEFAULT NULL COMMENT '字段映射和转换规则',
  `filter_predicate` text COLLATE utf8mb4_unicode_ci COMMENT '过滤条件 SQL WHERE',
  `sync_schedule` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Cron表达式',
  `media_process_config` json DEFAULT NULL COMMENT '多媒体处理配置：OCR/ASR/向量化等',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `object_ver_id` (`object_ver_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `sys_pipeline_def_ibfk_1` FOREIGN KEY (`object_ver_id`) REFERENCES `meta_object_type_ver` (`id`),
  CONSTRAINT `sys_pipeline_def_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `sys_dataset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据管道定义';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_pipeline_def`
--

LOCK TABLES `sys_pipeline_def` WRITE;
/*!40000 ALTER TABLE `sys_pipeline_def` DISABLE KEYS */;
INSERT INTO `sys_pipeline_def` VALUES ('pipe-device-cache','Device Registry Cache','obj-device-v1','ds-device-001','MATERIALIZED','{\"mappings\": [{\"source\": \"device_id\", \"target\": \"device_id\"}, {\"source\": \"device_name\", \"target\": \"name\"}, {\"source\": \"status\", \"target\": \"status\"}, {\"source\": \"location\", \"target\": \"category\"}]}',NULL,'0 */5 * * * *',NULL,1,'2026-01-23 02:35:47'),('pipe-doc-extract','Document AI Extraction','obj-document-v1','ds-docs-001','MEDIA_EXTRACT','{\"mappings\": [{\"source\": \"file_path\", \"target\": \"file_url\"}, {\"source\": \"file_name\", \"target\": \"title\"}, {\"source\": \"mime_type\", \"target\": \"file_type\"}, {\"source\": \"size\", \"target\": \"file_size\"}]}',NULL,'0 0 * * * *','{\"max_pages\": 100, \"ocr_enabled\": true, \"ocr_language\": \"eng+chi_sim\", \"embedding_model\": \"text-embedding-ada-002\", \"summarize_enabled\": true}',1,'2026-01-23 02:35:47'),('pipe-facility-geo','Facility GIS Sync','obj-facility-v1','ds-locations-001','VIRTUAL','{\"mappings\": [{\"source\": \"id\", \"target\": \"id\", \"transform\": \"TO_STRING\"}, {\"source\": \"name\", \"target\": \"name\"}, {\"source\": \"geom\", \"target\": \"location\", \"transform\": \"ST_ASGEOJSON\"}, {\"source\": \"category\", \"target\": \"facility_type\"}]}',NULL,NULL,NULL,1,'2026-01-23 02:35:47'),('pipe-image-extract','Image AI Extraction','obj-image-v1','ds-images-001','MEDIA_EXTRACT','{\"mappings\": [{\"source\": \"file_path\", \"target\": \"file_url\"}, {\"source\": \"file_name\", \"target\": \"title\"}, {\"source\": \"size\", \"target\": \"file_size\"}]}',NULL,'0 30 * * * *','{\"ocr_enabled\": true, \"thumbnail_size\": {\"width\": 200, \"height\": 200}, \"embedding_model\": \"clip-vit-large\", \"exif_extraction\": true}',1,'2026-01-23 02:35:47'),('pipe-sensor-realtime','Sensor Realtime Sync','obj-sensor-reading-v1','ds-sensor-001','VIRTUAL','{\"mappings\": [{\"source\": \"id\", \"target\": \"id\", \"transform\": \"TO_STRING\"}, {\"source\": \"device_id\", \"target\": \"device_id\"}, {\"source\": \"temperature\", \"target\": \"temperature\"}, {\"source\": \"humidity\", \"target\": \"humidity\"}, {\"source\": \"timestamp\", \"target\": \"reading_time\"}]}','timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)',NULL,NULL,1,'2026-01-23 02:35:47');
/*!40000 ALTER TABLE `sys_pipeline_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_project`
--

DROP TABLE IF EXISTS `sys_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_project` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目/工作空间，作为应用和对象绑定的上下文';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_project`
--

LOCK TABLES `sys_project` WRITE;
/*!40000 ALTER TABLE `sys_project` DISABLE KEYS */;
INSERT INTO `sys_project` VALUES ('proj-integration-test-001','Maritime Intelligence','Integration testing project for maritime intelligence','2026-01-26 06:52:58','2026-01-26 06:52:58');
/*!40000 ALTER TABLE `sys_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_sync_job_def`
--

DROP TABLE IF EXISTS `sys_sync_job_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_sync_job_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `connection_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_config` json DEFAULT NULL,
  `target_table` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `target_table_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sync_mode` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `schedule_cron` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_run_at` datetime DEFAULT NULL,
  `last_run_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_enabled` tinyint(1) NOT NULL DEFAULT '1',
  `rows_synced` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `cached_schema` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `connection_id` (`connection_id`),
  CONSTRAINT `sys_sync_job_def_ibfk_1` FOREIGN KEY (`connection_id`) REFERENCES `sys_connection` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_sync_job_def`
--

LOCK TABLES `sys_sync_job_def` WRITE;
/*!40000 ALTER TABLE `sys_sync_job_def` DISABLE KEYS */;
INSERT INTO `sys_sync_job_def` VALUES ('2ce57f79-3b99-4cd0-af96-068b74ddbf99','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_rel_target_report',NULL,'{\"table\": \"raw_rel_target_report\"}','raw_raw_rel_target_report',NULL,'FULL_OVERWRITE',NULL,NULL,NULL,1,NULL,'2026-01-30 10:34:05','2026-01-30 10:34:05','{\"columns\": [{\"name\": \"id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"target_id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"report_id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"mention_type\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"confidence_score\", \"type\": \"DECIMAL(5, 2)\", \"nullable\": true}, {\"name\": \"context_snippet\", \"type\": \"TEXT\", \"nullable\": true}, {\"name\": \"created_at\", \"type\": \"DATETIME\", \"nullable\": true}]}'),('3efc14dc-cc78-4ddd-b142-2e4a9ded45c5','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_recon_images',NULL,'{\"table\": \"raw_recon_images\"}','raw_raw_recon_images',NULL,'FULL_OVERWRITE',NULL,'2026-01-29 07:11:14','SUCCESS',1,5,'2026-01-29 07:10:59','2026-01-29 07:11:14','{\"columns\": [{\"name\": \"id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"image_id\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"filename\", \"type\": \"VARCHAR(200)\", \"nullable\": true}, {\"name\": \"capture_time\", \"type\": \"DATETIME\", \"nullable\": true}, {\"name\": \"sensor_type\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"resolution\", \"type\": \"VARCHAR(20)\", \"nullable\": true}, {\"name\": \"location\", \"type\": \"VARCHAR(200)\", \"nullable\": true}, {\"name\": \"file_path\", \"type\": \"VARCHAR(500)\", \"nullable\": true}, {\"name\": \"_sync_timestamp\", \"type\": \"DATETIME\", \"nullable\": true}]}'),('65484c9b-a79d-4967-a55c-8aca9fc35e40','190f434f-da70-4c30-9fbe-63e2a87eaf45','Test Sync raw_intel_reports',NULL,'{\"table\": \"raw_intel_reports\"}','test_raw_raw_intel_reports',NULL,'FULL_OVERWRITE',NULL,NULL,NULL,1,NULL,'2026-01-28 15:48:50','2026-01-28 15:48:50','{\"columns\": [{\"name\": \"id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"report_id\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"title\", \"type\": \"VARCHAR(200)\", \"nullable\": true}, {\"name\": \"content\", \"type\": \"TEXT\", \"nullable\": true}, {\"name\": \"classification\", \"type\": \"VARCHAR(20)\", \"nullable\": true}, {\"name\": \"source\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"region\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"created_at\", \"type\": \"DATETIME\", \"nullable\": true}, {\"name\": \"_sync_timestamp\", \"type\": \"DATETIME\", \"nullable\": true}]}'),('732f0fa6-39fd-40bb-849c-cedadd79bcf2','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_action_plans',NULL,'{\"table\": \"raw_action_plans\"}','raw_raw_action_plans',NULL,'FULL_OVERWRITE',NULL,'2026-01-28 12:12:28','FAILED',1,1,'2026-01-25 14:24:03','2026-01-28 12:12:28',NULL),('7cdab54f-4410-4353-92e3-f25c6a99c336','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_intel_reports',NULL,'{\"table\": \"raw_intel_reports\"}','raw_raw_intel_reports',NULL,'FULL_OVERWRITE',NULL,'2026-01-27 05:27:36','SUCCESS',1,5,'2026-01-26 15:13:42','2026-01-27 05:27:36',NULL),('887cfb4f-2118-47a9-b880-6252ab5d39a4','190f434f-da70-4c30-9fbe-63e2a87eaf45','Test Sync raw_intel_reports',NULL,'{\"table\": \"raw_intel_reports\"}','test_raw_raw_intel_reports',NULL,'FULL_OVERWRITE',NULL,NULL,NULL,1,NULL,'2026-01-28 15:49:28','2026-01-28 15:49:28','{\"columns\": [{\"name\": \"id\", \"type\": \"VARCHAR(36)\", \"nullable\": false}, {\"name\": \"report_id\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"title\", \"type\": \"VARCHAR(200)\", \"nullable\": true}, {\"name\": \"content\", \"type\": \"TEXT\", \"nullable\": true}, {\"name\": \"classification\", \"type\": \"VARCHAR(20)\", \"nullable\": true}, {\"name\": \"source\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"region\", \"type\": \"VARCHAR(50)\", \"nullable\": true}, {\"name\": \"created_at\", \"type\": \"DATETIME\", \"nullable\": true}, {\"name\": \"_sync_timestamp\", \"type\": \"DATETIME\", \"nullable\": true}]}'),('9986af19-5148-4667-b250-7770328f8b39','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_targets',NULL,'{\"table\": \"raw_targets\"}','raw_raw_targets',NULL,'FULL_OVERWRITE',NULL,'2026-01-29 08:20:54','SUCCESS',1,10,'2026-01-27 10:05:47','2026-01-29 08:20:54',NULL),('f3daa999-c54a-46fa-aba1-7ed2dceeefb4','190f434f-da70-4c30-9fbe-63e2a87eaf45','Sync raw_recon_images',NULL,'{\"table\": \"raw_recon_images\"}','raw_raw_recon_images',NULL,'INCREMENTAL',NULL,'2026-01-28 12:21:20','SUCCESS',1,5,'2026-01-27 05:31:17','2026-01-28 12:21:20',NULL);
/*!40000 ALTER TABLE `sys_sync_job_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_sync_run_log`
--

DROP TABLE IF EXISTS `sys_sync_run_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_sync_run_log` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `job_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rows_processed` int DEFAULT NULL,
  `error_message` text COLLATE utf8mb4_unicode_ci,
  `duration_ms` int DEFAULT NULL,
  `rows_affected` int DEFAULT NULL,
  `triggered_by` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `job_id` (`job_id`),
  CONSTRAINT `sys_sync_run_log_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `sys_sync_job_def` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_sync_run_log`
--

LOCK TABLES `sys_sync_run_log` WRITE;
/*!40000 ALTER TABLE `sys_sync_run_log` DISABLE KEYS */;
INSERT INTO `sys_sync_run_log` VALUES ('06af0797-5a55-4eb4-ba5b-29de7c3ea8c2','f3daa999-c54a-46fa-aba1-7ed2dceeefb4','2026-01-27 05:31:29','2026-01-27 05:31:30','SUCCESS',NULL,NULL,558,5,'API',NULL),('0dcfc3bb-e315-4af2-befd-4b1d6b1aa2bd','9986af19-5148-4667-b250-7770328f8b39','2026-01-28 12:13:10','2026-01-28 12:13:10','FAILED',NULL,NULL,463,10,'API','\'Settings\' object has no attribute \'ontology_raw_data_url\'\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 231, in run_sync_job\n    rows_copied = _copy_to_ontology_raw_data(\n                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 46, in _copy_to_ontology_raw_data\n    ontology_engine = _get_ontology_raw_data_engine()\n                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 26, in _get_ontology_raw_data_engine\n    return create_engine(settings.ontology_raw_data_url, pool_pre_ping=True)\n                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 1026, in __getattr__\n    raise AttributeError(f\'{type(self).__name__!r} object has no attribute {item!r}\')\nAttributeError: \'Settings\' object has no attribute \'ontology_raw_data_url\'\n'),('2bfc34b0-ea63-4a19-ba47-8aeb33ea78bf','f3daa999-c54a-46fa-aba1-7ed2dceeefb4','2026-01-28 12:21:20','2026-01-28 12:21:20','SUCCESS',NULL,NULL,4,5,'API',NULL),('2f1950e8-4e42-435e-802c-5cddf97782b1','732f0fa6-39fd-40bb-849c-cedadd79bcf2','2026-01-25 14:36:10','2026-01-25 14:36:10','SUCCESS',NULL,NULL,175,1,'API',NULL),('338c76ba-2972-4df6-b7c5-9c42696094d1','f3daa999-c54a-46fa-aba1-7ed2dceeefb4','2026-01-28 12:16:16','2026-01-28 12:16:16','FAILED',NULL,NULL,-369,5,'API','\'Settings\' object has no attribute \'ontology_raw_data_url\'\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 231, in run_sync_job\n    rows_copied = _copy_to_ontology_raw_data(\n                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 46, in _copy_to_ontology_raw_data\n    ontology_engine = _get_ontology_raw_data_engine()\n                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 26, in _get_ontology_raw_data_engine\n    return create_engine(settings.ontology_raw_data_url, pool_pre_ping=True)\n                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 1026, in __getattr__\n    raise AttributeError(f\'{type(self).__name__!r} object has no attribute {item!r}\')\nAttributeError: \'Settings\' object has no attribute \'ontology_raw_data_url\'\n'),('3a092a31-54c3-46fd-ad1e-13b27df6cafd','732f0fa6-39fd-40bb-849c-cedadd79bcf2','2026-01-27 05:27:42','2026-01-27 05:27:42','FAILED',NULL,NULL,360,0,'API','Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\nTraceback (most recent call last):\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\npymysql.err.ProgrammingError: (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1679, in execute\n    return execute_function(sql, *args)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1779, in exec_driver_sql\n    ret = self._execute_context(\n          ^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1846, in _execute_context\n    return self._exec_single_context(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1986, in _exec_single_context\n    self._handle_dbapi_exception(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 2363, in _handle_dbapi_exception\n    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\nsqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 141, in run_sync_job\n    rows_affected = _sync_mysql_table(\n                    ^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 77, in _sync_mysql_table\n    for chunk_df in pd.read_sql(query, source_engine, chunksize=chunk_size):\n                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 730, in read_sql\n    return pandas_sql.read_query(\n           ^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1856, in read_query\n    result = self.execute(sql, params)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1681, in execute\n    raise DatabaseError(f\"Execution failed on sql \'{sql}\': {exc}\") from exc\npandas.errors.DatabaseError: Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n'),('4f2e268f-8413-43ff-af98-a3d883ad8e49','9986af19-5148-4667-b250-7770328f8b39','2026-01-29 08:20:53','2026-01-29 08:20:54','SUCCESS',NULL,NULL,760,10,'API',NULL),('55faa8bc-cdb3-449f-88c7-6ee9e48e6649','f3daa999-c54a-46fa-aba1-7ed2dceeefb4','2026-01-28 12:05:29','2026-01-28 12:05:29','FAILED',NULL,NULL,322,5,'API','\'Settings\' object has no attribute \'ontology_raw_data_url\'\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 231, in run_sync_job\n    rows_copied = _copy_to_ontology_raw_data(\n                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 46, in _copy_to_ontology_raw_data\n    ontology_engine = _get_ontology_raw_data_engine()\n                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 26, in _get_ontology_raw_data_engine\n    return create_engine(settings.ontology_raw_data_url, pool_pre_ping=True)\n                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pydantic\\main.py\", line 1026, in __getattr__\n    raise AttributeError(f\'{type(self).__name__!r} object has no attribute {item!r}\')\nAttributeError: \'Settings\' object has no attribute \'ontology_raw_data_url\'\n'),('581a1df8-7e68-480a-bfa9-2674e8ca9a2f','7cdab54f-4410-4353-92e3-f25c6a99c336','2026-01-27 05:27:36','2026-01-27 05:27:36','SUCCESS',NULL,NULL,194,5,'API',NULL),('58de82f4-f4e1-4aec-8613-b98895f05642','7cdab54f-4410-4353-92e3-f25c6a99c336','2026-01-26 15:13:51','2026-01-26 15:13:51','SUCCESS',NULL,NULL,254,5,'API',NULL),('a1c7a4f6-f62f-4cf5-a6e3-9ba23aeb6934','732f0fa6-39fd-40bb-849c-cedadd79bcf2','2026-01-28 12:12:28','2026-01-28 12:12:28','FAILED',NULL,NULL,-37,0,'API','Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\npymysql.err.ProgrammingError: (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1679, in execute\n    return execute_function(sql, *args)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1779, in exec_driver_sql\n    ret = self._execute_context(\n          ^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1846, in _execute_context\n    return self._exec_single_context(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1986, in _exec_single_context\n    self._handle_dbapi_exception(\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 2363, in _handle_dbapi_exception\n    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\nsqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 200, in run_sync_job\n    rows_affected = _sync_mysql_table(\n                    ^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 136, in _sync_mysql_table\n    for chunk_df in pd.read_sql(query, source_engine, chunksize=chunk_size):\n                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 730, in read_sql\n    return pandas_sql.read_query(\n           ^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1856, in read_query\n    result = self.execute(sql, params)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1681, in execute\n    raise DatabaseError(f\"Execution failed on sql \'{sql}\': {exc}\") from exc\npandas.errors.DatabaseError: Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n'),('eb7249ff-19b8-4abb-a1a1-088a92d7fa86','732f0fa6-39fd-40bb-849c-cedadd79bcf2','2026-01-27 05:27:35','2026-01-27 05:27:35','FAILED',NULL,NULL,63,0,'API','Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\nTraceback (most recent call last):\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\npymysql.err.ProgrammingError: (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1679, in execute\n    return execute_function(sql, *args)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1779, in exec_driver_sql\n    ret = self._execute_context(\n          ^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1846, in _execute_context\n    return self._exec_single_context(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1986, in _exec_single_context\n    self._handle_dbapi_exception(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 2363, in _handle_dbapi_exception\n    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\base.py\", line 1967, in _exec_single_context\n    self.dialect.do_execute(\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\sqlalchemy\\engine\\default.py\", line 952, in do_execute\n    cursor.execute(statement, parameters)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 153, in execute\n    result = self._query(query)\n             ^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\cursors.py\", line 322, in _query\n    conn.query(q)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 575, in query\n    self._affected_rows = self._read_query_result(unbuffered=unbuffered)\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 826, in _read_query_result\n    result.read()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 1203, in read\n    first_packet = self.connection._read_packet()\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\connections.py\", line 782, in _read_packet\n    packet.raise_for_error()\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\protocol.py\", line 219, in raise_for_error\n    err.raise_mysql_exception(self._data)\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pymysql\\err.py\", line 150, in raise_mysql_exception\n    raise errorclass(errno, errval)\nsqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 141, in run_sync_job\n    rows_affected = _sync_mysql_table(\n                    ^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\PC\\code\\mdp\\backend\\app\\engine\\sync_worker.py\", line 77, in _sync_mysql_table\n    for chunk_df in pd.read_sql(query, source_engine, chunksize=chunk_size):\n                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 730, in read_sql\n    return pandas_sql.read_query(\n           ^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1856, in read_query\n    result = self.execute(sql, params)\n             ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"c:\\Users\\PC\\code\\mdp\\.venv\\Lib\\site-packages\\pandas\\io\\sql.py\", line 1681, in execute\n    raise DatabaseError(f\"Execution failed on sql \'{sql}\': {exc}\") from exc\npandas.errors.DatabaseError: Execution failed on sql \'SELECT * FROM raw_action_plans\': (pymysql.err.ProgrammingError) (1146, \"Table \'mdp_raw_store.raw_action_plans\' doesn\'t exist\")\n[SQL: SELECT * FROM raw_action_plans]\n(Background on this error at: https://sqlalche.me/e/20/f405)\n'),('f4fd6e5b-505d-443d-bb43-3c569a2ed09a','3efc14dc-cc78-4ddd-b142-2e4a9ded45c5','2026-01-29 07:11:14','2026-01-29 07:11:14','SUCCESS',NULL,NULL,130,5,'API',NULL);
/*!40000 ALTER TABLE `sys_sync_run_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_sync_task`
--

DROP TABLE IF EXISTS `sys_sync_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_sync_task` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pipeline_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` timestamp NOT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'PENDING, RUNNING, SUCCESS, FAILED',
  `rows_processed` int DEFAULT '0',
  `error_message` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `pipeline_id` (`pipeline_id`),
  CONSTRAINT `sys_sync_task_ibfk_1` FOREIGN KEY (`pipeline_id`) REFERENCES `sys_pipeline_def` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据同步任务执行记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_sync_task`
--

LOCK TABLES `sys_sync_task` WRITE;
/*!40000 ALTER TABLE `sys_sync_task` DISABLE KEYS */;
INSERT INTO `sys_sync_task` VALUES ('task-001','pipe-device-cache','2026-01-21 16:00:00','2026-01-21 16:00:15','SUCCESS',1250,NULL),('task-002','pipe-device-cache','2026-01-21 16:05:00','2026-01-21 16:05:12','SUCCESS',1252,NULL),('task-003','pipe-doc-extract','2026-01-21 16:00:00','2026-01-21 16:02:45','SUCCESS',45,NULL),('task-004','pipe-image-extract','2026-01-21 16:30:00','2026-01-21 16:31:20','SUCCESS',128,NULL),('task-005','pipe-device-cache','2026-01-21 16:10:00',NULL,'RUNNING',0,NULL);
/*!40000 ALTER TABLE `sys_sync_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'ontology_meta_new'
--

--
-- Current Database: `mdp_raw_store`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `mdp_raw_store` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `mdp_raw_store`;

--
-- Table structure for table `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3`
--

DROP TABLE IF EXISTS `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3` (
  `id` text,
  `object_def_id` text,
  `tail_number` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3`
--

LOCK TABLES `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3` WRITE;
/*!40000 ALTER TABLE `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3` DISABLE KEYS */;
INSERT INTO `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3` VALUES ('p1','4f37bc91-f949-4021-9b18-8c7bd09906a3','FN-001'),('p2','4f37bc91-f949-4021-9b18-8c7bd09906a3','FN-002');
/*!40000 ALTER TABLE `obj_instance_4f37bc91_f949_4021_9b18_8c7bd09906a3` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39`
--

DROP TABLE IF EXISTS `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39` (
  `id` text,
  `object_def_id` text,
  `tail_number` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39`
--

LOCK TABLES `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39` WRITE;
/*!40000 ALTER TABLE `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39` DISABLE KEYS */;
INSERT INTO `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39` VALUES ('p1','6fc14db9-d764-4cc7-9fff-8c9786c13b39','FN-001'),('p2','6fc14db9-d764-4cc7-9fff-8c9786c13b39','FN-002');
/*!40000 ALTER TABLE `obj_instance_6fc14db9_d764_4cc7_9fff_8c9786c13b39` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c`
--

DROP TABLE IF EXISTS `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c` (
  `id` text,
  `object_def_id` text,
  `tail_number` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c`
--

LOCK TABLES `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c` WRITE;
/*!40000 ALTER TABLE `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c` DISABLE KEYS */;
INSERT INTO `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c` VALUES ('p1','96b03573-e3cf-4aad-a8b9-b8523209272c','FN-001'),('p2','96b03573-e3cf-4aad-a8b9-b8523209272c','FN-002');
/*!40000 ALTER TABLE `obj_instance_96b03573_e3cf_4aad_a8b9_b8523209272c` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb`
--

DROP TABLE IF EXISTS `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb` (
  `id` text,
  `object_def_id` text,
  `tail_number` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb`
--

LOCK TABLES `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb` WRITE;
/*!40000 ALTER TABLE `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb` DISABLE KEYS */;
INSERT INTO `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb` VALUES ('p1','ac684509-6193-4dff-842e-3caf1721fbbb','FN-001'),('p2','ac684509-6193-4dff-842e-3caf1721fbbb','FN-002');
/*!40000 ALTER TABLE `obj_instance_ac684509_6193_4dff_842e_3caf1721fbbb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f`
--

DROP TABLE IF EXISTS `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f` (
  `id` text,
  `object_def_id` text,
  `tail_number` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f`
--

LOCK TABLES `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f` WRITE;
/*!40000 ALTER TABLE `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f` DISABLE KEYS */;
INSERT INTO `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f` VALUES ('p1','fc9c9f0f-811b-4204-b6e0-33208541563f','FN-001'),('p2','fc9c9f0f-811b-4204-b6e0-33208541563f','FN-002');
/*!40000 ALTER TABLE `obj_instance_fc9c9f0f_811b_4204_b6e0_33208541563f` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_e2e_planes`
--

DROP TABLE IF EXISTS `raw_e2e_planes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_e2e_planes` (
  `id` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `tail_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_e2e_planes`
--

LOCK TABLES `raw_e2e_planes` WRITE;
/*!40000 ALTER TABLE `raw_e2e_planes` DISABLE KEYS */;
INSERT INTO `raw_e2e_planes` VALUES ('p1','F-16','FN-001','Ready'),('p2','F-35','FN-002','Maintenance');
/*!40000 ALTER TABLE `raw_e2e_planes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_e2e_planes_1a7dafa3`
--

DROP TABLE IF EXISTS `raw_e2e_planes_1a7dafa3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_e2e_planes_1a7dafa3` (
  `id` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `tail_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_e2e_planes_1a7dafa3`
--

LOCK TABLES `raw_e2e_planes_1a7dafa3` WRITE;
/*!40000 ALTER TABLE `raw_e2e_planes_1a7dafa3` DISABLE KEYS */;
INSERT INTO `raw_e2e_planes_1a7dafa3` VALUES ('p1','F-16','FN-001','Ready'),('p2','F-35','FN-002','Maintenance');
/*!40000 ALTER TABLE `raw_e2e_planes_1a7dafa3` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_e2e_planes_6c4551e8`
--

DROP TABLE IF EXISTS `raw_e2e_planes_6c4551e8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_e2e_planes_6c4551e8` (
  `id` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `tail_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_e2e_planes_6c4551e8`
--

LOCK TABLES `raw_e2e_planes_6c4551e8` WRITE;
/*!40000 ALTER TABLE `raw_e2e_planes_6c4551e8` DISABLE KEYS */;
INSERT INTO `raw_e2e_planes_6c4551e8` VALUES ('p1','F-16','FN-001','Ready'),('p2','F-35','FN-002','Maintenance');
/*!40000 ALTER TABLE `raw_e2e_planes_6c4551e8` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_e2e_planes_cdf38c15`
--

DROP TABLE IF EXISTS `raw_e2e_planes_cdf38c15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_e2e_planes_cdf38c15` (
  `id` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `tail_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_e2e_planes_cdf38c15`
--

LOCK TABLES `raw_e2e_planes_cdf38c15` WRITE;
/*!40000 ALTER TABLE `raw_e2e_planes_cdf38c15` DISABLE KEYS */;
INSERT INTO `raw_e2e_planes_cdf38c15` VALUES ('p1','F-16','FN-001','Ready'),('p2','F-35','FN-002','Maintenance');
/*!40000 ALTER TABLE `raw_e2e_planes_cdf38c15` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_e2e_planes_f20b0868`
--

DROP TABLE IF EXISTS `raw_e2e_planes_f20b0868`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_e2e_planes_f20b0868` (
  `id` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `tail_number` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_e2e_planes_f20b0868`
--

LOCK TABLES `raw_e2e_planes_f20b0868` WRITE;
/*!40000 ALTER TABLE `raw_e2e_planes_f20b0868` DISABLE KEYS */;
INSERT INTO `raw_e2e_planes_f20b0868` VALUES ('p1','F-16','FN-001','Ready'),('p2','F-35','FN-002','Maintenance');
/*!40000 ALTER TABLE `raw_e2e_planes_f20b0868` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_intel_reports`
--

DROP TABLE IF EXISTS `raw_intel_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_intel_reports` (
  `id` varchar(36) NOT NULL,
  `report_id` varchar(50) DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `content` text,
  `classification` varchar(20) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `region` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_intel_reports`
--

LOCK TABLES `raw_intel_reports` WRITE;
/*!40000 ALTER TABLE `raw_intel_reports` DISABLE KEYS */;
INSERT INTO `raw_intel_reports` VALUES ('report-48669e84','RPT-2024410','海上态势综合评估','综合各类情报源，对南海海域当前态势进行全面评估。','秘密','技术侦察','东海','2026-01-02 22:52:59','2026-01-26 22:52:59'),('report-a76eaac9','RPT-2024653','可疑船只跟踪报告','监测到一艘悬挂巴拿马国旗的船只在黄海海域进行非正常活动。','公开','卫星侦察','西太平洋','2025-12-28 22:52:59','2026-01-26 22:52:59'),('report-a7716421','RPT-2024268','重点目标监视报告','对编号为519287460的目标进行持续监视，记录其航行轨迹和停靠港口。','秘密','人工情报','渤海','2026-01-25 22:52:59','2026-01-26 22:52:59'),('report-ac3b89be','RPT-2024638','重点目标监视报告','对编号为810578919的目标进行持续监视，记录其航行轨迹和停靠港口。','秘密','卫星侦察','东海','2026-01-03 22:52:59','2026-01-26 22:52:59'),('report-bac67d41','RPT-2024506','异常活动预警通报','在印度洋海域发现异常船舶聚集现象，需要进一步关注。','秘密','卫星侦察','南海','2026-01-11 22:52:59','2026-01-26 22:52:59');
/*!40000 ALTER TABLE `raw_intel_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_raw_recon_images`
--

DROP TABLE IF EXISTS `raw_raw_recon_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_raw_recon_images` (
  `id` text,
  `image_id` text,
  `filename` text,
  `capture_time` datetime DEFAULT NULL,
  `sensor_type` text,
  `resolution` text,
  `location` text,
  `file_path` text,
  `_sync_timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_raw_recon_images`
--

LOCK TABLES `raw_raw_recon_images` WRITE;
/*!40000 ALTER TABLE `raw_raw_recon_images` DISABLE KEYS */;
INSERT INTO `raw_raw_recon_images` VALUES ('image-92b5429b','IMG-227898','recon_3958_opt.tif','2026-01-24 22:52:59','侦察机','5m','印度洋 (21.78°N, 125.77°E)','/data/imagery/2024/12/recon_4030.tif','2026-01-29 07:11:14'),('image-99fbec40','IMG-718630','recon_6275_ir.tif','2026-01-26 16:52:59','无人机','3m','马六甲海峡 (23.5°N, 126.22°E)','/data/imagery/2024/12/recon_5733.tif','2026-01-29 07:11:14'),('image-9a8d0a71','IMG-877344','recon_4468_ir.tif','2026-01-21 02:52:59','SAR雷达','5m','渤海 (22.91°N, 118.97°E)','/data/imagery/2025/11/recon_3719.tif','2026-01-29 07:11:14'),('image-9d9a8cce','IMG-995533','recon_5011_ir.tif','2026-01-21 12:52:59','侦察机','5m','印度洋 (18.65°N, 111.82°E)','/data/imagery/2025/01/recon_2138.tif','2026-01-29 07:11:14'),('image-cf771130','IMG-419395','recon_8530_opt.tif','2026-01-26 14:52:59','SAR雷达','0.5m','东海 (20.73°N, 119.35°E)','/data/imagery/2024/02/recon_9368.tif','2026-01-29 07:11:14');
/*!40000 ALTER TABLE `raw_raw_recon_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_raw_targets`
--

DROP TABLE IF EXISTS `raw_raw_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_raw_targets` (
  `id` text,
  `mmsi` text,
  `name` text,
  `vessel_type` text,
  `flag` text,
  `length` double DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `heading` bigint DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_raw_targets`
--

LOCK TABLES `raw_raw_targets` WRITE;
/*!40000 ALTER TABLE `raw_raw_targets` DISABLE KEYS */;
INSERT INTO `raw_raw_targets` VALUES ('target-3d309474','758550181','Arctic Explorer','集装箱船','美国',311.1,28.181411,120.214395,24.4,61,'2026-01-24 03:52:59','2026-01-29 08:20:54'),('target-48a103fa','810578919','海上勇士','货船','马绍尔群岛',347.9,22.450397,123.389592,2.8,10,'2026-01-24 07:52:59','2026-01-29 08:20:54'),('target-6e38f513','554560912','Pacific Mariner','拖船','马绍尔群岛',228.4,34.31767,116.542766,25,350,'2026-01-24 23:52:59','2026-01-29 08:20:54'),('target-84e8c7f4','153207413','东方之星','渔船','巴拿马',264.4,22.052281,113.652977,17.9,137,'2026-01-25 05:52:59','2026-01-29 08:20:54'),('target-8d176c8d','704355595','Ocean Pioneer','集装箱船','韩国',297.9,27.349232,111.028632,0.8,110,'2026-01-26 02:52:59','2026-01-29 08:20:54'),('target-9cff89db','147753379','Blue Horizon','客轮','马绍尔群岛',104.6,19.121894,125.022241,15.2,30,'2026-01-26 22:52:59','2026-01-29 08:20:54'),('target-cf1fbd23','378492291','Arctic Explorer','货船','中国',63.3,27.481739,120.191857,13.5,349,'2026-01-26 05:52:59','2026-01-29 08:20:54'),('target-d3f7c483','524334609','太平洋探索者','油轮','日本',55.4,18.788538,125.214042,15.2,196,'2026-01-26 15:52:59','2026-01-29 08:20:54'),('target-e6904f08','519287460','Silver Wave','客轮','巴拿马',101.5,33.649164,123.53717,11.9,192,'2026-01-26 09:52:59','2026-01-29 08:20:54'),('target-fc6dc2e8','348967487','Golden Dragon','集装箱船','新加坡',264.7,29.168029,125.847861,24.6,307,'2026-01-24 04:52:59','2026-01-29 08:20:54');
/*!40000 ALTER TABLE `raw_raw_targets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_recon_images`
--

DROP TABLE IF EXISTS `raw_recon_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_recon_images` (
  `id` varchar(36) NOT NULL,
  `image_id` varchar(50) DEFAULT NULL,
  `filename` varchar(200) DEFAULT NULL,
  `capture_time` datetime DEFAULT NULL,
  `sensor_type` varchar(50) DEFAULT NULL,
  `resolution` varchar(20) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_recon_images`
--

LOCK TABLES `raw_recon_images` WRITE;
/*!40000 ALTER TABLE `raw_recon_images` DISABLE KEYS */;
INSERT INTO `raw_recon_images` VALUES ('image-92b5429b','IMG-227898','recon_3958_opt.tif','2026-01-24 22:52:59','侦察机','5m','印度洋 (21.78°N, 125.77°E)','/data/imagery/2024/12/recon_4030.tif','2026-01-26 22:52:59'),('image-99fbec40','IMG-718630','recon_6275_ir.tif','2026-01-26 16:52:59','无人机','3m','马六甲海峡 (23.5°N, 126.22°E)','/data/imagery/2024/12/recon_5733.tif','2026-01-26 22:52:59'),('image-9a8d0a71','IMG-877344','recon_4468_ir.tif','2026-01-21 02:52:59','SAR雷达','5m','渤海 (22.91°N, 118.97°E)','/data/imagery/2025/11/recon_3719.tif','2026-01-26 22:52:59'),('image-9d9a8cce','IMG-995533','recon_5011_ir.tif','2026-01-21 12:52:59','侦察机','5m','印度洋 (18.65°N, 111.82°E)','/data/imagery/2025/01/recon_2138.tif','2026-01-26 22:52:59'),('image-cf771130','IMG-419395','recon_8530_opt.tif','2026-01-26 14:52:59','SAR雷达','0.5m','东海 (20.73°N, 119.35°E)','/data/imagery/2024/02/recon_9368.tif','2026-01-26 22:52:59');
/*!40000 ALTER TABLE `raw_recon_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_rel_target_report`
--

DROP TABLE IF EXISTS `raw_rel_target_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_rel_target_report` (
  `id` varchar(36) NOT NULL,
  `target_id` varchar(36) NOT NULL COMMENT 'FK to Target object',
  `report_id` varchar(36) NOT NULL COMMENT 'FK to IntelReport object',
  `mention_type` varchar(50) DEFAULT 'DIRECT' COMMENT 'Type of mention: DIRECT, INDIRECT, INFERRED',
  `confidence_score` decimal(5,2) DEFAULT '1.00' COMMENT 'Confidence of the mention (0.00-1.00)',
  `context_snippet` text COMMENT 'Text snippet where target is mentioned',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_rel_target_report`
--

LOCK TABLES `raw_rel_target_report` WRITE;
/*!40000 ALTER TABLE `raw_rel_target_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `raw_rel_target_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_targets`
--

DROP TABLE IF EXISTS `raw_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_targets` (
  `id` varchar(36) NOT NULL,
  `mmsi` varchar(20) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `vessel_type` varchar(50) DEFAULT NULL,
  `flag` varchar(50) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `heading` int DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_targets`
--

LOCK TABLES `raw_targets` WRITE;
/*!40000 ALTER TABLE `raw_targets` DISABLE KEYS */;
INSERT INTO `raw_targets` VALUES ('target-3d309474','758550181','Arctic Explorer','集装箱船','美国',311.1,28.181411,120.214395,24.4,61,'2026-01-24 03:52:59','2026-01-26 22:52:59'),('target-48a103fa','810578919','海上勇士','货船','马绍尔群岛',347.9,22.450397,123.389592,2.8,10,'2026-01-24 07:52:59','2026-01-26 22:52:59'),('target-6e38f513','554560912','Pacific Mariner','拖船','马绍尔群岛',228.4,34.31767,116.542766,25,350,'2026-01-24 23:52:59','2026-01-26 22:52:59'),('target-84e8c7f4','153207413','东方之星','渔船','巴拿马',264.4,22.052281,113.652977,17.9,137,'2026-01-25 05:52:59','2026-01-26 22:52:59'),('target-8d176c8d','704355595','Ocean Pioneer','集装箱船','韩国',297.9,27.349232,111.028632,0.8,110,'2026-01-26 02:52:59','2026-01-26 22:52:59'),('target-9cff89db','147753379','Blue Horizon','客轮','马绍尔群岛',104.6,19.121894,125.022241,15.2,30,'2026-01-26 22:52:59','2026-01-26 22:52:59'),('target-cf1fbd23','378492291','Arctic Explorer','货船','中国',63.3,27.481739,120.191857,13.5,349,'2026-01-26 05:52:59','2026-01-26 22:52:59'),('target-d3f7c483','524334609','太平洋探索者','油轮','日本',55.4,18.788538,125.214042,15.2,196,'2026-01-26 15:52:59','2026-01-26 22:52:59'),('target-e6904f08','519287460','Silver Wave','客轮','巴拿马',101.5,33.649164,123.53717,11.9,192,'2026-01-26 09:52:59','2026-01-26 22:52:59'),('target-fc6dc2e8','348967487','Golden Dragon','集装箱船','新加坡',264.7,29.168029,125.847861,24.6,307,'2026-01-24 04:52:59','2026-01-26 22:52:59');
/*!40000 ALTER TABLE `raw_targets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_targets_new`
--

DROP TABLE IF EXISTS `raw_targets_new`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_targets_new` (
  `id` varchar(36) NOT NULL,
  `mmsi` varchar(20) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `vessel_type` varchar(50) DEFAULT NULL,
  `flag` varchar(50) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `heading` int DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_targets_new`
--

LOCK TABLES `raw_targets_new` WRITE;
/*!40000 ALTER TABLE `raw_targets_new` DISABLE KEYS */;
INSERT INTO `raw_targets_new` VALUES ('target-3d309474','758550181','Arctic Explorer','集装箱船','美国',311.1,28.181411,120.214395,24.4,61,'2026-01-24 03:52:59','2026-01-26 22:52:59'),('target-48a103fa','810578919','海上勇士','货船','马绍尔群岛',347.9,22.450397,123.389592,2.8,10,'2026-01-24 07:52:59','2026-01-26 22:52:59'),('target-6e38f513','554560912','Pacific Mariner','拖船','马绍尔群岛',228.4,34.31767,116.542766,25,350,'2026-01-24 23:52:59','2026-01-26 22:52:59'),('target-84e8c7f4','153207413','东方之星','渔船','巴拿马',264.4,22.052281,113.652977,17.9,137,'2026-01-25 05:52:59','2026-01-26 22:52:59'),('target-8d176c8d','704355595','Ocean Pioneer','集装箱船','韩国',297.9,27.349232,111.028632,0.8,110,'2026-01-26 02:52:59','2026-01-26 22:52:59'),('target-9cff89db','147753379','Blue Horizon','客轮','马绍尔群岛',104.6,19.121894,125.022241,15.2,30,'2026-01-26 22:52:59','2026-01-26 22:52:59'),('target-cf1fbd23','378492291','Arctic Explorer','货船','中国',63.3,27.481739,120.191857,13.5,349,'2026-01-26 05:52:59','2026-01-26 22:52:59'),('target-d3f7c483','524334609','太平洋探索者','油轮','日本',55.4,18.788538,125.214042,15.2,196,'2026-01-26 15:52:59','2026-01-26 22:52:59'),('target-e6904f08','519287460','Silver Wave','客轮','巴拿马',101.5,33.649164,123.53717,11.9,192,'2026-01-26 09:52:59','2026-01-26 22:52:59'),('target-fc6dc2e8','348967487','Golden Dragon','集装箱船','新加坡',264.7,29.168029,125.847861,24.6,307,'2026-01-24 04:52:59','2026-01-26 22:52:59');
/*!40000 ALTER TABLE `raw_targets_new` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'mdp_raw_store'
--

--
-- Current Database: `ontology_raw_data`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ontology_raw_data` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ontology_raw_data`;

--
-- Table structure for table `raw_raw_recon_images`
--

DROP TABLE IF EXISTS `raw_raw_recon_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_raw_recon_images` (
  `id` text,
  `image_id` text,
  `filename` text,
  `capture_time` datetime DEFAULT NULL,
  `sensor_type` text,
  `resolution` text,
  `location` text,
  `file_path` text,
  `_sync_timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_raw_recon_images`
--

LOCK TABLES `raw_raw_recon_images` WRITE;
/*!40000 ALTER TABLE `raw_raw_recon_images` DISABLE KEYS */;
INSERT INTO `raw_raw_recon_images` VALUES ('image-92b5429b','IMG-227898','recon_3958_opt.tif','2026-01-24 22:52:59','侦察机','5m','印度洋 (21.78°N, 125.77°E)','/data/imagery/2024/12/recon_4030.tif','2026-01-29 07:11:14'),('image-99fbec40','IMG-718630','recon_6275_ir.tif','2026-01-26 16:52:59','无人机','3m','马六甲海峡 (23.5°N, 126.22°E)','/data/imagery/2024/12/recon_5733.tif','2026-01-29 07:11:14'),('image-9a8d0a71','IMG-877344','recon_4468_ir.tif','2026-01-21 02:52:59','SAR雷达','5m','渤海 (22.91°N, 118.97°E)','/data/imagery/2025/11/recon_3719.tif','2026-01-29 07:11:14'),('image-9d9a8cce','IMG-995533','recon_5011_ir.tif','2026-01-21 12:52:59','侦察机','5m','印度洋 (18.65°N, 111.82°E)','/data/imagery/2025/01/recon_2138.tif','2026-01-29 07:11:14'),('image-cf771130','IMG-419395','recon_8530_opt.tif','2026-01-26 14:52:59','SAR雷达','0.5m','东海 (20.73°N, 119.35°E)','/data/imagery/2024/02/recon_9368.tif','2026-01-29 07:11:14');
/*!40000 ALTER TABLE `raw_raw_recon_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_raw_targets`
--

DROP TABLE IF EXISTS `raw_raw_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_raw_targets` (
  `id` text,
  `mmsi` text,
  `name` text,
  `vessel_type` text,
  `flag` text,
  `length` double DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `heading` bigint DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `_sync_timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_raw_targets`
--

LOCK TABLES `raw_raw_targets` WRITE;
/*!40000 ALTER TABLE `raw_raw_targets` DISABLE KEYS */;
INSERT INTO `raw_raw_targets` VALUES ('target-3d309474','758550181','Arctic Explorer','集装箱船','美国',311.1,28.181411,120.214395,24.4,61,'2026-01-24 03:52:59','2026-01-29 08:20:54'),('target-48a103fa','810578919','海上勇士','货船','马绍尔群岛',347.9,22.450397,123.389592,2.8,10,'2026-01-24 07:52:59','2026-01-29 08:20:54'),('target-6e38f513','554560912','Pacific Mariner','拖船','马绍尔群岛',228.4,34.31767,116.542766,25,350,'2026-01-24 23:52:59','2026-01-29 08:20:54'),('target-84e8c7f4','153207413','东方之星','渔船','巴拿马',264.4,22.052281,113.652977,17.9,137,'2026-01-25 05:52:59','2026-01-29 08:20:54'),('target-8d176c8d','704355595','Ocean Pioneer','集装箱船','韩国',297.9,27.349232,111.028632,0.8,110,'2026-01-26 02:52:59','2026-01-29 08:20:54'),('target-9cff89db','147753379','Blue Horizon','客轮','马绍尔群岛',104.6,19.121894,125.022241,15.2,30,'2026-01-26 22:52:59','2026-01-29 08:20:54'),('target-cf1fbd23','378492291','Arctic Explorer','货船','中国',63.3,27.481739,120.191857,13.5,349,'2026-01-26 05:52:59','2026-01-29 08:20:54'),('target-d3f7c483','524334609','太平洋探索者','油轮','日本',55.4,18.788538,125.214042,15.2,196,'2026-01-26 15:52:59','2026-01-29 08:20:54'),('target-e6904f08','519287460','Silver Wave','客轮','巴拿马',101.5,33.649164,123.53717,11.9,192,'2026-01-26 09:52:59','2026-01-29 08:20:54'),('target-fc6dc2e8','348967487','Golden Dragon','集装箱船','新加坡',264.7,29.168029,125.847861,24.6,307,'2026-01-24 04:52:59','2026-01-29 08:20:54');
/*!40000 ALTER TABLE `raw_raw_targets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'ontology_raw_data'
--

--
-- Current Database: `ontology`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ontology` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ontology`;

--
-- Table structure for table `data_fighter`
--

DROP TABLE IF EXISTS `data_fighter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_fighter` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `callsign` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fuel` int DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lat` decimal(10,6) DEFAULT NULL,
  `lon` decimal(10,6) DEFAULT NULL,
  `altitude` int DEFAULT NULL,
  `squadron_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `base_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_fighter`
--

LOCK TABLES `data_fighter` WRITE;
/*!40000 ALTER TABLE `data_fighter` DISABLE KEYS */;
INSERT INTO `data_fighter` VALUES ('1fe7236d-7f49-44bf-a9c0-4b728a696f7c',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('32772af3-f122-45d6-a05b-9adf5da56ab5',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('3a22fff6-494b-4dbf-8ed9-73559ef68de8',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('40a8bc1b-d1ef-4bb5-825d-5e82d6204d05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('50000000-0000-0000-0000-000000000001','Ghost-1',90,'Ready',34.052200,108.945100,10000,NULL,NULL),('50000000-0000-0000-0000-000000000002','Ghost-2',85,'Ready',34.053000,108.946000,9500,NULL,NULL),('50000000-0000-0000-0000-000000000003','Dragon-1',75,'In Flight',35.123400,110.567800,12000,NULL,NULL),('5f6e1f01-e41e-46f1-a614-0a66a8a54e97',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('7985b098-3aad-4f0a-89ca-4032e0ecdd47',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('a1766628-b3b1-4e2e-a1ab-31ef38dc28fb',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('c23aa1b8-2ea8-4b7f-bc11-7d380dff9682',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('d0d72d1a-84bb-4940-918e-3f729e92aaa4',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `data_fighter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_mission`
--

DROP TABLE IF EXISTS `data_mission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_mission` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority` int DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_mission`
--

LOCK TABLES `data_mission` WRITE;
/*!40000 ALTER TABLE `data_mission` DISABLE KEYS */;
INSERT INTO `data_mission` VALUES ('52000000-0000-0000-0000-000000000001','Operation Thunder','strike','in_progress',NULL,NULL,NULL);
/*!40000 ALTER TABLE `data_mission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_target`
--

DROP TABLE IF EXISTS `data_target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_target` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `threat_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority` int DEFAULT NULL,
  `lat` decimal(10,6) DEFAULT NULL,
  `lon` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_target`
--

LOCK TABLES `data_target` WRITE;
/*!40000 ALTER TABLE `data_target` DISABLE KEYS */;
INSERT INTO `data_target` VALUES ('51000000-0000-0000-0000-000000000001','Radar Station Alpha','high','radar',9,35.500000,111.500000),('51000000-0000-0000-0000-000000000002','Bunker Bravo','high','bunker',8,36.000000,112.000000);
/*!40000 ALTER TABLE `data_target` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `link_mission_participation`
--

DROP TABLE IF EXISTS `link_mission_participation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `link_mission_participation` (
  `mission_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fighter_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`mission_id`,`fighter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `link_mission_participation`
--

LOCK TABLES `link_mission_participation` WRITE;
/*!40000 ALTER TABLE `link_mission_participation` DISABLE KEYS */;
INSERT INTO `link_mission_participation` VALUES ('52000000-0000-0000-0000-000000000001','50000000-0000-0000-0000-000000000001','leader');
/*!40000 ALTER TABLE `link_mission_participation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logic_action_def`
--

DROP TABLE IF EXISTS `logic_action_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logic_action_def` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `backing_function_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_act_api` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logic_action_def`
--

LOCK TABLES `logic_action_def` WRITE;
/*!40000 ALTER TABLE `logic_action_def` DISABLE KEYS */;
/*!40000 ALTER TABLE `logic_action_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logic_function_def`
--

DROP TABLE IF EXISTS `logic_function_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logic_function_def` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `code_content` longtext,
  `input_schema` json DEFAULT NULL,
  `output_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_func_api` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logic_function_def`
--

LOCK TABLES `logic_function_def` WRITE;
/*!40000 ALTER TABLE `logic_function_def` DISABLE KEYS */;
/*!40000 ALTER TABLE `logic_function_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_action_def`
--

DROP TABLE IF EXISTS `meta_action_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_action_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `backing_function_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_action_def_api_name` (`api_name`),
  KEY `fk_action_backing_function` (`backing_function_id`),
  CONSTRAINT `fk_action_backing_function` FOREIGN KEY (`backing_function_id`) REFERENCES `meta_function_def` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_action_def`
--

LOCK TABLES `meta_action_def` WRITE;
/*!40000 ALTER TABLE `meta_action_def` DISABLE KEYS */;
INSERT INTO `meta_action_def` VALUES ('40000000-0000-0000-0000-000000000001','action_calculate_distance','Calculate Distance Action','30000000-0000-0000-0000-000000000001'),('40000000-0000-0000-0000-000000000002','action_send_alert','Send Alert Notification','30000000-0000-0000-0000-000000000002'),('40000000-0000-0000-0000-000000000003','action_update_object_status','Update Object Status','30000000-0000-0000-0000-000000000003'),('40000000-0000-0000-0000-000000000004','action_generate_daily_report','Generate Daily Report','30000000-0000-0000-0000-000000000004'),('40000000-0000-0000-0000-000000000005','action_validate_input','Validate Input Data','30000000-0000-0000-0000-000000000005');
/*!40000 ALTER TABLE `meta_action_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meta_function_def`
--

DROP TABLE IF EXISTS `meta_function_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_function_def` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_content` longtext COLLATE utf8mb4_unicode_ci COMMENT 'Python Code Content',
  `bound_object_type_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `input_params_schema` json DEFAULT NULL,
  `output_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'VOID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_function_def_api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_function_def`
--

LOCK TABLES `meta_function_def` WRITE;
/*!40000 ALTER TABLE `meta_function_def` DISABLE KEYS */;
INSERT INTO `meta_function_def` VALUES ('30000000-0000-0000-0000-000000000001','calculate_distance','Calculate Distances','def main(ctx):\n    \"\"\"Calculate distance between two coordinates\"\"\"\n    import math\n    lat1 = ctx.get(\'lat1\', 0)\n    lon1 = ctx.get(\'lon1\', 0)\n    lat2 = ctx.get(\'lat2\', 0)\n    lon2 = ctx.get(\'lon2\', 0)\n    \n    R = 6371  # Earth radius in km\n    dlat = math.radians(lat2 - lat1)\n    dlon = math.radians(lon2 - lon1)\n    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2\n    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))\n    return R * c',NULL,'Calculate distance between two coordinates (km)','[{\"name\": \"lat1\", \"type\": \"DOUBLE\", \"required\": true}, {\"name\": \"lon1\", \"type\": \"DOUBLE\", \"required\": true}, {\"name\": \"lat2\", \"type\": \"DOUBLE\", \"required\": true}, {\"name\": \"lon2\", \"type\": \"DOUBLE\", \"required\": true}]','DOUBLE'),('30000000-0000-0000-0000-000000000002','send_notification','Send Notification','def main(ctx):\n    \"\"\"Send notification to specified recipients\"\"\"\n    title = ctx.get(\'title\', \'Notification\')\n    message = ctx.get(\'message\', \'\')\n    recipients = ctx.get(\'recipients\', [])\n    \n    print(f\"Sending notification: {title} to {recipients}\")\n    return {\"status\": \"sent\", \"count\": len(recipients)}',NULL,'Send notification message to specified recipients','[{\"name\": \"title\", \"type\": \"STRING\", \"required\": true}, {\"name\": \"message\", \"type\": \"STRING\", \"required\": true}, {\"name\": \"recipients\", \"type\": \"ARRAY\", \"required\": true}]','OBJECT'),('30000000-0000-0000-0000-000000000003','update_status','Update Status','def main(ctx):\n    \"\"\"Update the status of an object\"\"\"\n    object_id = ctx.get(\'object_id\', \'\')\n    new_status = ctx.get(\'new_status\', \'unknown\')\n    \n    return {\"object_id\": object_id, \"status\": new_status, \"updated\": True}',NULL,'Update object status','[{\"name\": \"object_id\", \"type\": \"STRING\", \"required\": true}, {\"name\": \"new_status\", \"type\": \"STRING\", \"required\": true}]','OBJECT'),('30000000-0000-0000-0000-000000000004','generate_report','Generate Report','def main(ctx):\n    \"\"\"Generate a report for the specified date range\"\"\"\n    report_type = ctx.get(\'report_type\', \'default\')\n    start_date = ctx.get(\'start_date\', \'\')\n    end_date = ctx.get(\'end_date\', \'\')\n    \n    return {\"report_type\": report_type, \"start\": start_date, \"end\": end_date, \"generated\": True}',NULL,'Generate report for specified date range','[{\"name\": \"report_type\", \"type\": \"STRING\", \"required\": true}, {\"name\": \"start_date\", \"type\": \"DATE\", \"required\": true}, {\"name\": \"end_date\", \"type\": \"DATE\", \"required\": true}]','OBJECT'),('30000000-0000-0000-0000-000000000005','validate_data','Validate Data','def main(ctx):\n    \"\"\"Validate data against specified rules\"\"\"\n    data = ctx.get(\'data\', {})\n    rules = ctx.get(\'rules\', [])\n    \n    errors = []\n    # Simple validation logic\n    for rule in rules:\n        field = rule.get(\'field\', \'\')\n        if field and field not in data:\n            errors.append(f\"Missing field: {field}\")\n    \n    return {\"valid\": len(errors) == 0, \"errors\": errors}',NULL,'Validate data against specified rules','[{\"name\": \"data\", \"type\": \"OBJECT\", \"required\": true}, {\"name\": \"rules\", \"type\": \"ARRAY\", \"required\": true}]','OBJECT');
/*!40000 ALTER TABLE `meta_function_def` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `meta_link_type`
--

DROP TABLE IF EXISTS `meta_link_type`;
/*!50001 DROP VIEW IF EXISTS `meta_link_type`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_link_type` AS SELECT 
 1 AS `id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `source_type_id`,
 1 AS `target_type_id`,
 1 AS `cardinality`,
 1 AS `created_at`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `meta_object_type`
--

DROP TABLE IF EXISTS `meta_object_type`;
/*!50001 DROP VIEW IF EXISTS `meta_object_type`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_object_type` AS SELECT 
 1 AS `id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `description`,
 1 AS `project_id`,
 1 AS `created_at`,
 1 AS `updated_at`,
 1 AS `property_schema`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `meta_project`
--

DROP TABLE IF EXISTS `meta_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_project` (
  `id` varchar(36) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_project`
--

LOCK TABLES `meta_project` WRITE;
/*!40000 ALTER TABLE `meta_project` DISABLE KEYS */;
INSERT INTO `meta_project` VALUES ('proj-default','Battlefield System','Global Project','2026-01-14 17:35:21');
/*!40000 ALTER TABLE `meta_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `meta_shared_property`
--

DROP TABLE IF EXISTS `meta_shared_property`;
/*!50001 DROP VIEW IF EXISTS `meta_shared_property`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `meta_shared_property` AS SELECT 
 1 AS `id`,
 1 AS `api_name`,
 1 AS `display_name`,
 1 AS `data_type`,
 1 AS `formatter`,
 1 AS `description`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `meta_test_scenario`
--

DROP TABLE IF EXISTS `meta_test_scenario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meta_test_scenario` (
  `id` varchar(36) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `steps_config` json DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meta_test_scenario`
--

LOCK TABLES `meta_test_scenario` WRITE;
/*!40000 ALTER TABLE `meta_test_scenario` DISABLE KEYS */;
/*!40000 ALTER TABLE `meta_test_scenario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ont_link_rule`
--

DROP TABLE IF EXISTS `ont_link_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ont_link_rule` (
  `id` varchar(36) NOT NULL,
  `link_type_id` varchar(36) NOT NULL,
  `rule_type` varchar(20) NOT NULL COMMENT 'FOREIGN_KEY, JOIN_TABLE',
  `source_column_id` varchar(36) DEFAULT NULL,
  `target_column_id` varchar(36) DEFAULT NULL,
  `join_table_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rule_link` (`link_type_id`),
  CONSTRAINT `fk_rule_link` FOREIGN KEY (`link_type_id`) REFERENCES `ont_link_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ont_link_rule`
--

LOCK TABLES `ont_link_rule` WRITE;
/*!40000 ALTER TABLE `ont_link_rule` DISABLE KEYS */;
/*!40000 ALTER TABLE `ont_link_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ont_link_type`
--

DROP TABLE IF EXISTS `ont_link_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ont_link_type` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `source_object_type_id` varchar(36) NOT NULL,
  `target_object_type_id` varchar(36) NOT NULL,
  `cardinality` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_link_api` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ont_link_type`
--

LOCK TABLES `ont_link_type` WRITE;
/*!40000 ALTER TABLE `ont_link_type` DISABLE KEYS */;
INSERT INTO `ont_link_type` VALUES ('link-base','stationed_at','Stationed At','obj-fighter','obj-base','MANY_TO_ONE'),('link-part','participation','Participates In','obj-fighter','obj-mission','MANY_TO_MANY');
/*!40000 ALTER TABLE `ont_link_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ont_object_property`
--

DROP TABLE IF EXISTS `ont_object_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ont_object_property` (
  `id` varchar(36) NOT NULL,
  `object_type_id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `mapped_column_id` varchar(36) NOT NULL,
  `shared_type_id` varchar(36) DEFAULT NULL,
  `is_primary_key` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_prop_api` (`object_type_id`,`api_name`),
  KEY `fk_prop_col` (`mapped_column_id`),
  CONSTRAINT `fk_prop_col` FOREIGN KEY (`mapped_column_id`) REFERENCES `sys_dataset_column` (`id`),
  CONSTRAINT `fk_prop_obj` FOREIGN KEY (`object_type_id`) REFERENCES `ont_object_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ont_object_property`
--

LOCK TABLES `ont_object_property` WRITE;
/*!40000 ALTER TABLE `ont_object_property` DISABLE KEYS */;
INSERT INTO `ont_object_property` VALUES ('prop-f-call','obj-fighter','callsign','Callsign','col-f-call',NULL,0),('prop-f-fuel','obj-fighter','fuel','Fuel Level','col-f-fuel',NULL,0),('prop-t-name','obj-target','name','Target Name','col-t-name',NULL,0);
/*!40000 ALTER TABLE `ont_object_property` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ont_object_type`
--

DROP TABLE IF EXISTS `ont_object_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ont_object_type` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `description` text,
  `backing_dataset_id` varchar(36) NOT NULL,
  `title_property_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_obj_api` (`api_name`),
  KEY `fk_obj_ds` (`backing_dataset_id`),
  CONSTRAINT `fk_obj_ds` FOREIGN KEY (`backing_dataset_id`) REFERENCES `sys_dataset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ont_object_type`
--

LOCK TABLES `ont_object_type` WRITE;
/*!40000 ALTER TABLE `ont_object_type` DISABLE KEYS */;
INSERT INTO `ont_object_type` VALUES ('obj-fighter','fighter','Fighter Jet (Updated)',NULL,'ds-fighter',NULL,'2026-01-07 22:28:53'),('obj-mission','mission','Mission',NULL,'ds-mission',NULL,'2026-01-07 22:28:53'),('obj-target','target','Enemy Target',NULL,'ds-target',NULL,'2026-01-07 22:28:53');
/*!40000 ALTER TABLE `ont_object_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ont_shared_property_type`
--

DROP TABLE IF EXISTS `ont_shared_property_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ont_shared_property_type` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `data_type` varchar(50) NOT NULL,
  `formatter` varchar(500) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL COMMENT '描述',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_shared_api` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ont_shared_property_type`
--

LOCK TABLES `ont_shared_property_type` WRITE;
/*!40000 ALTER TABLE `ont_shared_property_type` DISABLE KEYS */;
INSERT INTO `ont_shared_property_type` VALUES ('de99eb76-15c7-4343-8f7a-fc5ef070f5a0','aa','a','INTEGER','{\"min_value\":1,\"max_value\":112}','111','2026-01-14 00:12:27');
/*!40000 ALTER TABLE `ont_shared_property_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_action_log`
--

DROP TABLE IF EXISTS `sys_action_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_action_log` (
  `id` varchar(36) NOT NULL,
  `project_id` varchar(36) DEFAULT 'default',
  `action_def_id` varchar(36) NOT NULL,
  `source_object_id` varchar(36) DEFAULT NULL,
  `request_params` json DEFAULT NULL,
  `execution_status` varchar(20) DEFAULT NULL,
  `duration_ms` int DEFAULT NULL,
  `error_message` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_action_log`
--

LOCK TABLES `sys_action_log` WRITE;
/*!40000 ALTER TABLE `sys_action_log` DISABLE KEYS */;
INSERT INTO `sys_action_log` VALUES ('0664d64f-c497-4321-8983-56277411d87d','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',5,NULL,'2026-01-19 21:14:52'),('082e3abe-4b0f-47c3-8e50-2ab68cf9eb9d','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',13,NULL,'2026-01-19 21:14:03'),('0e23db85-2723-477f-9c62-5e1fdd973db0','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',85,NULL,'2026-01-21 17:37:54'),('0e7de975-48fa-462d-a2c5-a4b9d7b11a55','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',68,NULL,'2026-01-19 01:00:15'),('110df1fc-3d32-4223-807c-fe886530fbe0','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',41,NULL,'2026-01-19 00:55:11'),('15fcd013-819d-4617-b5f6-13bba12bbc9f','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',19,NULL,'2026-01-19 00:57:01'),('18c7cf56-bf85-4540-a089-ac5c225ca829','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',11,NULL,'2026-01-19 00:51:29'),('19d33440-8dd2-4c12-8b1d-1d94ac87eb55','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',7,NULL,'2026-01-19 01:29:11'),('3f26746e-8689-4ce2-9571-0482ac625c6d','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',7,NULL,'2026-01-19 00:59:25'),('3f79e82d-93db-450b-b8e0-41ff31e0299d','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',19,NULL,'2026-01-19 01:00:08'),('409c74a1-67f9-4c44-898f-650f0f9ecf91','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',34,NULL,'2026-01-21 17:39:44'),('43c68905-c4a5-4ed9-860c-3ed464abb42f','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',13,NULL,'2026-01-19 01:15:01'),('5fb680a1-c9fb-4689-a172-17a065e249ae','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',7,NULL,'2026-01-19 01:17:42'),('645058ff-fe84-4e5c-8578-2d0e9926817e','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',29,NULL,'2026-01-21 16:15:02'),('6a62225a-59bf-462f-ae79-9a8d0ae85134','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',22,NULL,'2026-01-19 00:28:35'),('743e979d-b339-47ae-8585-d9cd6da20cd9','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',8,NULL,'2026-01-19 01:12:12'),('80a8addd-d707-4482-a793-44342615460e','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',7,NULL,'2026-01-19 21:07:13'),('82ef0a3d-2bf1-4456-bec0-e2057758d73e','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',11,NULL,'2026-01-19 01:05:18'),('88c820a0-f547-4972-a949-fec3317b4036','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',17,NULL,'2026-01-19 21:00:24'),('8fc5b068-0087-4c94-b941-ac63a956529f','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',16,NULL,'2026-01-19 21:15:18'),('c94ef596-4b3d-403c-96fb-2eb2191c36ae','default','40000000-0000-0000-0000-000000000001','1fe7236d-7f49-44bf-a9c0-4b728a696f7c','{}','SUCCESS',15,NULL,'2026-01-19 21:13:56');
/*!40000 ALTER TABLE `sys_action_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dataset`
--

DROP TABLE IF EXISTS `sys_dataset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dataset` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `storage_type` varchar(50) DEFAULT 'MYSQL_TABLE',
  `storage_location` varchar(255) NOT NULL COMMENT '物理表名',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sys_dataset_api_name` (`api_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dataset`
--

LOCK TABLES `sys_dataset` WRITE;
/*!40000 ALTER TABLE `sys_dataset` DISABLE KEYS */;
INSERT INTO `sys_dataset` VALUES ('ds-','dataset_','Dataset for Test Type','VIRTUAL','virtual_'),('ds-fighter','dataset_fighter','Fighter Data','MYSQL_TABLE','data_fighter'),('ds-mission','dataset_mission','Mission Data','MYSQL_TABLE','data_mission'),('ds-target','dataset_target','Target Data','MYSQL_TABLE','data_target'),('ds-test_dup_160771b4','dataset_test_dup_160771b4','Dataset for First Type','VIRTUAL','virtual_test_dup_160771b4'),('ds-test_dup_60d2e19c','dataset_test_dup_60d2e19c','Dataset for First Type','VIRTUAL','virtual_test_dup_60d2e19c'),('ds-test_dup_639c84e2','dataset_test_dup_639c84e2','Dataset for First Type','VIRTUAL','virtual_test_dup_639c84e2'),('ds-test_dup_d1c41000','dataset_test_dup_d1c41000','Dataset for First Type','VIRTUAL','virtual_test_dup_d1c41000'),('ds-test_dup_fe8531a8','dataset_test_dup_fe8531a8','Dataset for First Type','VIRTUAL','virtual_test_dup_fe8531a8'),('ds-test_obj_2520c234','dataset_test_obj_2520c234','Dataset for Test Object test_obj_2520c234','VIRTUAL','virtual_test_obj_2520c234'),('ds-test_obj_293e1293','dataset_test_obj_293e1293','Dataset for Test Object test_obj_293e1293','VIRTUAL','virtual_test_obj_293e1293'),('ds-test_obj_3c0d2d6f','dataset_test_obj_3c0d2d6f','Dataset for Test Object test_obj_3c0d2d6f','VIRTUAL','virtual_test_obj_3c0d2d6f'),('ds-test_obj_7c9f4f1e','dataset_test_obj_7c9f4f1e','Dataset for Test Object test_obj_7c9f4f1e','VIRTUAL','virtual_test_obj_7c9f4f1e'),('ds-test_obj_af087b7e','dataset_test_obj_af087b7e','Dataset for Test Object test_obj_af087b7e','VIRTUAL','virtual_test_obj_af087b7e');
/*!40000 ALTER TABLE `sys_dataset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dataset_column`
--

DROP TABLE IF EXISTS `sys_dataset_column`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dataset_column` (
  `id` varchar(36) NOT NULL,
  `dataset_id` varchar(36) NOT NULL,
  `column_name` varchar(100) NOT NULL,
  `physical_type` varchar(50) NOT NULL,
  `is_primary_key` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dataset_col` (`dataset_id`,`column_name`),
  CONSTRAINT `fk_col_ds` FOREIGN KEY (`dataset_id`) REFERENCES `sys_dataset` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dataset_column`
--

LOCK TABLES `sys_dataset_column` WRITE;
/*!40000 ALTER TABLE `sys_dataset_column` DISABLE KEYS */;
INSERT INTO `sys_dataset_column` VALUES ('col-f-call','ds-fighter','callsign','VARCHAR',0),('col-f-fuel','ds-fighter','fuel','INT',0),('col-f-id','ds-fighter','id','VARCHAR',1),('col-t-id','ds-target','id','VARCHAR',1),('col-t-name','ds-target','name','VARCHAR',0);
/*!40000 ALTER TABLE `sys_dataset_column` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `sys_datasource_table`
--

DROP TABLE IF EXISTS `sys_datasource_table`;
/*!50001 DROP VIEW IF EXISTS `sys_datasource_table`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sys_datasource_table` AS SELECT 
 1 AS `id`,
 1 AS `table_name`,
 1 AS `db_type`,
 1 AS `columns_schema`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `sys_object_instance`
--

DROP TABLE IF EXISTS `sys_object_instance`;
/*!50001 DROP VIEW IF EXISTS `sys_object_instance`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sys_object_instance` AS SELECT 
 1 AS `id`,
 1 AS `object_type_id`,
 1 AS `properties`,
 1 AS `created_at`,
 1 AS `updated_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'ontology'
--

--
-- Current Database: `ontology_meta_new`
--

USE `ontology_meta_new`;

--
-- Final view structure for view `meta_link_type`
--

/*!50001 DROP VIEW IF EXISTS `meta_link_type`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_link_type` AS select `d`.`id` AS `id`,`d`.`api_name` AS `api_name`,`v`.`display_name` AS `display_name`,`v`.`source_object_def_id` AS `source_type_id`,`v`.`target_object_def_id` AS `target_type_id`,`v`.`cardinality` AS `cardinality`,`d`.`created_at` AS `created_at`,`v`.`created_at` AS `updated_at` from (`meta_link_type_def` `d` left join `meta_link_type_ver` `v` on((`d`.`current_version_id` = `v`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `meta_object_type`
--

/*!50001 DROP VIEW IF EXISTS `meta_object_type`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_object_type` AS select `d`.`id` AS `id`,`d`.`api_name` AS `api_name`,`v`.`display_name` AS `display_name`,`v`.`description` AS `description`,NULL AS `property_schema`,NULL AS `project_id`,`d`.`created_at` AS `created_at`,`v`.`created_at` AS `updated_at` from (`meta_object_type_def` `d` left join `meta_object_type_ver` `v` on((`d`.`current_version_id` = `v`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `meta_project`
--

/*!50001 DROP VIEW IF EXISTS `meta_project`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_project` AS select `sys_project`.`id` AS `id`,`sys_project`.`name` AS `name`,`sys_project`.`description` AS `description`,`sys_project`.`created_at` AS `created_at` from `sys_project` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `meta_shared_property`
--

/*!50001 DROP VIEW IF EXISTS `meta_shared_property`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_shared_property` AS select `meta_shared_property_def`.`id` AS `id`,'proj-default' AS `project_id`,`meta_shared_property_def`.`api_name` AS `api_name`,`meta_shared_property_def`.`display_name` AS `display_name`,`meta_shared_property_def`.`data_type` AS `data_type`,NULL AS `formatter`,`meta_shared_property_def`.`description` AS `description`,`meta_shared_property_def`.`created_at` AS `created_at` from `meta_shared_property_def` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sys_datasource_table`
--

/*!50001 DROP VIEW IF EXISTS `sys_datasource_table`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sys_datasource_table` AS select `d`.`id` AS `id`,`d`.`connection_id` AS `connection_id`,coalesce(json_unquote(json_extract(`d`.`location_config`,'$.table')),`d`.`name`) AS `table_name`,coalesce(`c`.`conn_type`,'MySQL') AS `db_type`,json_extract(`d`.`cached_schema`,'$.columns') AS `columns_schema`,now() AS `created_at` from (`sys_dataset` `d` left join `sys_connection` `c` on((`d`.`connection_id` = `c`.`id`))) where (json_extract(`d`.`location_config`,'$.table') is not null) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Current Database: `mdp_raw_store`
--

USE `mdp_raw_store`;

--
-- Current Database: `ontology_raw_data`
--

USE `ontology_raw_data`;

--
-- Current Database: `ontology`
--

USE `ontology`;

--
-- Final view structure for view `meta_link_type`
--

/*!50001 DROP VIEW IF EXISTS `meta_link_type`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_link_type` AS select `ont_link_type`.`id` AS `id`,`ont_link_type`.`api_name` AS `api_name`,`ont_link_type`.`display_name` AS `display_name`,`ont_link_type`.`source_object_type_id` AS `source_type_id`,`ont_link_type`.`target_object_type_id` AS `target_type_id`,`ont_link_type`.`cardinality` AS `cardinality`,now() AS `created_at`,now() AS `updated_at` from `ont_link_type` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `meta_object_type`
--

/*!50001 DROP VIEW IF EXISTS `meta_object_type`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_object_type` AS select `t`.`id` AS `id`,`t`.`api_name` AS `api_name`,`t`.`display_name` AS `display_name`,`t`.`description` AS `description`,'proj-default' AS `project_id`,`t`.`created_at` AS `created_at`,now() AS `updated_at`,(select json_objectagg(`p`.`api_name`,'string') from `ont_object_property` `p` where (`p`.`object_type_id` = `t`.`id`)) AS `property_schema` from `ont_object_type` `t` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `meta_shared_property`
--

/*!50001 DROP VIEW IF EXISTS `meta_shared_property`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `meta_shared_property` AS select `spt`.`id` AS `id`,`spt`.`api_name` AS `api_name`,`spt`.`display_name` AS `display_name`,`spt`.`data_type` AS `data_type`,`spt`.`formatter` AS `formatter`,`spt`.`description` AS `description`,`spt`.`created_at` AS `created_at` from `ont_shared_property_type` `spt` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sys_datasource_table`
--

/*!50001 DROP VIEW IF EXISTS `sys_datasource_table`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sys_datasource_table` AS select `ds`.`id` AS `id`,`ds`.`storage_location` AS `table_name`,'MySQL' AS `db_type`,(select json_arrayagg(json_object('name',`dc`.`column_name`,'type',`dc`.`physical_type`,'is_primary_key',`dc`.`is_primary_key`)) from `sys_dataset_column` `dc` where (`dc`.`dataset_id` = `ds`.`id`)) AS `columns_schema`,now() AS `created_at` from `sys_dataset` `ds` where (`ds`.`storage_type` = 'MYSQL_TABLE') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sys_object_instance`
--

/*!50001 DROP VIEW IF EXISTS `sys_object_instance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sys_object_instance` AS select `data_fighter`.`id` AS `id`,'obj-fighter' AS `object_type_id`,json_object('callsign',`data_fighter`.`callsign`,'fuel',`data_fighter`.`fuel`,'status',`data_fighter`.`status`,'lat',`data_fighter`.`lat`,'lon',`data_fighter`.`lon`) AS `properties`,now() AS `created_at`,now() AS `updated_at` from `data_fighter` union all select `data_target`.`id` AS `id`,'obj-target' AS `object_type_id`,json_object('name',`data_target`.`name`,'threat_level',`data_target`.`threat_level`,'lat',`data_target`.`lat`,'lon',`data_target`.`lon`) AS `properties`,now() AS `created_at`,now() AS `updated_at` from `data_target` union all select `data_mission`.`id` AS `id`,'obj-mission' AS `object_type_id`,json_object('name',`data_mission`.`name`,'type',`data_mission`.`type`,'status',`data_mission`.`status`) AS `properties`,now() AS `created_at`,now() AS `updated_at` from `data_mission` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-31 15:21:20
