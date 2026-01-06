-- MDP Platform Demo Database Schema
-- Compatible with MySQL 8.0+

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 1. Meta Layer (Definitions)
-- ==========================================

-- 1.0 Projects (Project Definitions)
CREATE TABLE `meta_project` (
  `id` varchar(36) NOT NULL COMMENT 'UUID',
  `name` varchar(100) NOT NULL COMMENT '项目名称，如 Battlefield Demo',
  `description` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.1 Object Types (Blueprints like "Fighter", "Mission")
CREATE TABLE `meta_object_type` (
  `id` varchar(36) NOT NULL COMMENT 'UUID',
  `api_name` varchar(100) NOT NULL COMMENT 'Unique API Identifier, e.g., fighter',
  `display_name` varchar(200) NOT NULL COMMENT 'Display Name, e.g., Fighter Jet',
  `description` varchar(500) DEFAULT NULL,
  `property_schema` json DEFAULT NULL COMMENT 'List of property definitions (key, type, label)',
  `project_id` varchar(36) DEFAULT NULL COMMENT 'Project ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_object_type_api_name` (`api_name`),
  KEY `ix_meta_object_type_project_id` (`project_id`),
  CONSTRAINT `fk_obj_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.2 Link Types (Relationship Definitions)
CREATE TABLE `meta_link_type` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `source_type_id` varchar(36) NOT NULL COMMENT 'Source Object Type ID',
  `target_type_id` varchar(36) NOT NULL COMMENT 'Target Object Type ID',
  `cardinality` varchar(50) NOT NULL DEFAULT 'MANY_TO_MANY' COMMENT '1:1, 1:N, M:N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_link_type_api_name` (`api_name`),
  KEY `ix_meta_link_type_source_type_id` (`source_type_id`),
  KEY `ix_meta_link_type_target_type_id` (`target_type_id`),
  CONSTRAINT `fk_link_source_type` FOREIGN KEY (`source_type_id`) REFERENCES `meta_object_type` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_link_target_type` FOREIGN KEY (`target_type_id`) REFERENCES `meta_object_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.3 Functions (Business Logic Code)
CREATE TABLE `meta_function_def` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `code_content` longtext COMMENT 'Python Code Content',
  `bound_object_type_id` varchar(36) DEFAULT NULL COMMENT 'Optional: Bound to specific object type',
  `description` varchar(500) COMMENT '函数描述',
  `input_params_schema` json COMMENT '输入参数定义 [{"name":"a", "type":"int", "required":true}]',
  `output_type` varchar(50) DEFAULT 'VOID' COMMENT '返回值类型: STRING, INTEGER, OBJECT, VOID等',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_function_def_api_name` (`api_name`),
  KEY `fk_function_bound_type` (`bound_object_type_id`),
  CONSTRAINT `fk_function_bound_type` FOREIGN KEY (`bound_object_type_id`) REFERENCES `meta_object_type` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.4 Actions (User Triggers)
CREATE TABLE `meta_action_def` (
  `id` varchar(36) NOT NULL,
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `backing_function_id` varchar(36) NOT NULL COMMENT 'Function ID to execute',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_meta_action_def_api_name` (`api_name`),
  KEY `fk_action_backing_function` (`backing_function_id`),
  CONSTRAINT `fk_action_backing_function` FOREIGN KEY (`backing_function_id`) REFERENCES `meta_function_def` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.5 Shared Properties (Common Properties across ObjectTypes)
CREATE TABLE `meta_shared_property` (
  `id` varchar(36) NOT NULL,
  `project_id` varchar(36) NOT NULL COMMENT '归属的项目',
  `api_name` varchar(100) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `data_type` varchar(50) NOT NULL COMMENT 'String, Integer, Date...',
  `formatter` varchar(500) DEFAULT NULL COMMENT '格式化规则',
  `description` varchar(500),
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_shared_prop_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 2. Instance Layer (Actual Data)
-- ==========================================

-- 2.1 Object Instances (Data Rows with JSON properties)
CREATE TABLE `sys_object_instance` (
  `id` varchar(36) NOT NULL,
  `object_type_id` varchar(36) NOT NULL,
  `properties` json DEFAULT NULL COMMENT 'Dynamic properties: {"fuel": 80}',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sys_object_instance_type_id` (`object_type_id`),
  CONSTRAINT `fk_instance_type` FOREIGN KEY (`object_type_id`) REFERENCES `meta_object_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.2 Link Instances (Connections)
CREATE TABLE `sys_link_instance` (
  `id` varchar(36) NOT NULL,
  `link_type_id` varchar(36) NOT NULL,
  `source_instance_id` varchar(36) NOT NULL,
  `target_instance_id` varchar(36) NOT NULL,
  `properties` json DEFAULT NULL COMMENT 'Link properties: {"role": "Leader"}',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sys_link_instance_link_type_id` (`link_type_id`),
  KEY `ix_sys_link_instance_source_id` (`source_instance_id`),
  KEY `ix_sys_link_instance_target_id` (`target_instance_id`),
  CONSTRAINT `fk_link_inst_type` FOREIGN KEY (`link_type_id`) REFERENCES `meta_link_type` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_link_inst_source` FOREIGN KEY (`source_instance_id`) REFERENCES `sys_object_instance` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_link_inst_target` FOREIGN KEY (`target_instance_id`) REFERENCES `sys_object_instance` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 2.5 Data Source Tables (Raw Data Sources)
-- ==========================================

-- 2.5.1 Data Source Table Definitions
CREATE TABLE `sys_datasource_table` (
  `id` varchar(36) NOT NULL COMMENT 'UUID',
  `table_name` varchar(100) NOT NULL COMMENT '原始数据表名',
  `db_type` varchar(20) DEFAULT 'MySQL' COMMENT '数据库类型',
  `columns_schema` json COMMENT '存储列定义 [{"name": "id", "type": "int"}, ...]',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_sys_datasource_table_name` (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 3. Runtime & Testing Layer
-- ==========================================

-- 3.1 Action Execution Logs
CREATE TABLE `sys_action_log` (
  `id` varchar(36) NOT NULL,
  `project_id` varchar(36) NOT NULL,
  `action_def_id` varchar(36) NOT NULL,
  `trigger_user_id` varchar(36) COMMENT '触发用户',
  `input_params` json COMMENT '执行入参',
  `execution_status` varchar(20) COMMENT 'SUCCESS, FAILED',
  `error_message` text,
  `duration_ms` int COMMENT '执行耗时',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sys_action_log_project_id` (`project_id`),
  KEY `ix_sys_action_log_action_def_id` (`action_def_id`),
  KEY `ix_sys_action_log_created_at` (`created_at`),
  CONSTRAINT `fk_action_log_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_action_log_action_def` FOREIGN KEY (`action_def_id`) REFERENCES `meta_action_def` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.2 Test Scenarios
CREATE TABLE `meta_test_scenario` (
  `id` varchar(36) NOT NULL,
  `project_id` varchar(36) NOT NULL,
  `name` varchar(100),
  `steps_config` json COMMENT '存储编排的动作序列，例如 [{"actionId": "...", "params": "..."}]',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_meta_test_scenario_project_id` (`project_id`),
  CONSTRAINT `fk_test_scenario_project` FOREIGN KEY (`project_id`) REFERENCES `meta_project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

