-- =============================================
-- Migration: Multimodal Mapping Module Tables
-- MDP Platform V3.1
-- Date: 2026-01-25
-- =============================================

-- =============================================
-- Table 1: ctx_object_mapping_def (映射定义表)
-- 存储 React Flow 图的映射逻辑
-- =============================================
CREATE TABLE IF NOT EXISTS ctx_object_mapping_def (
    id VARCHAR(36) PRIMARY KEY,
    object_def_id VARCHAR(36) NOT NULL COMMENT '目标本体对象类型ID',
    source_connection_id VARCHAR(36) NOT NULL COMMENT '源数据连接ID',
    source_table_name VARCHAR(100) NOT NULL COMMENT '源表名 (mdp_raw_store中的表)',
    mapping_spec JSON NOT NULL COMMENT 'React Flow图配置 (nodes, edges)',
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' COMMENT '状态: DRAFT, PUBLISHED, ARCHIVED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_object_def_id (object_def_id),
    INDEX idx_source_connection_id (source_connection_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='多模态映射定义表 - 存储React Flow图的映射逻辑';

-- =============================================
-- Table 2: ctx_object_instance_lineage (对象实例溯源表)
-- 记录向量与原始数据的映射关系，支持反向追溯
-- =============================================
CREATE TABLE IF NOT EXISTS ctx_object_instance_lineage (
    id VARCHAR(36) PRIMARY KEY,
    object_def_id VARCHAR(36) NOT NULL COMMENT '本体对象类型ID',
    instance_id VARCHAR(36) NOT NULL COMMENT '对象实例ID (同时是ChromaDB向量ID)',
    mapping_id VARCHAR(36) NOT NULL COMMENT '来源映射定义ID',
    source_table VARCHAR(100) NOT NULL COMMENT '原始表名 (mdp_raw_store)',
    source_row_id VARCHAR(100) NOT NULL COMMENT '原始行主键/ID',
    source_file_path VARCHAR(500) DEFAULT NULL COMMENT '原始文件路径 (如S3 path, 用于非结构化数据)',
    vector_collection VARCHAR(100) DEFAULT NULL COMMENT 'ChromaDB集合名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for fast lookup
    INDEX idx_instance_id (instance_id),
    INDEX idx_object_def_id (object_def_id),
    INDEX idx_mapping_id (mapping_id),
    INDEX idx_source_lookup (source_table, source_row_id),
    INDEX idx_vector_collection (vector_collection)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='对象实例溯源表 - 向量到原始数据的追溯映射';
