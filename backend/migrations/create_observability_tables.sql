-- =============================================
-- Migration: Observability Tables
-- MDP Platform V3.1 - Index Health Module
-- Date: 2026-01-25
-- =============================================

-- =============================================
-- Table 1: sys_index_job_run (作业运行记录)
-- 存储每次索引作业的执行信息和指标
-- =============================================
CREATE TABLE IF NOT EXISTS sys_index_job_run (
    id VARCHAR(36) PRIMARY KEY,
    mapping_id VARCHAR(36) NOT NULL COMMENT '映射定义ID',
    object_def_id VARCHAR(36) NOT NULL COMMENT '对象类型ID',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME DEFAULT NULL COMMENT '结束时间',
    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' COMMENT '状态: SUCCESS, PARTIAL_SUCCESS, FAILED',
    rows_processed INT NOT NULL DEFAULT 0 COMMENT '处理的原始行数',
    rows_indexed INT NOT NULL DEFAULT 0 COMMENT '成功索引的行数',
    metrics_json JSON COMMENT '详细指标 (pk_collisions, ai_latency_avg_ms, etc.)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_mapping_id (mapping_id),
    INDEX idx_object_def_id (object_def_id),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='索引作业运行记录 - 存储执行信息和健康指标';

-- =============================================
-- Table 2: sys_index_error_sample (错误采样表)
-- Dead Letter Queue - 存储错误样本用于调试
-- =============================================
CREATE TABLE IF NOT EXISTS sys_index_error_sample (
    id VARCHAR(36) PRIMARY KEY,
    job_run_id VARCHAR(36) NOT NULL COMMENT '作业运行ID',
    raw_row_id VARCHAR(100) NOT NULL COMMENT '原始数据行ID',
    error_category VARCHAR(20) NOT NULL COMMENT '错误类别: SEMANTIC, AI_INFERENCE, MEDIA_IO, SYSTEM',
    error_message VARCHAR(2000) NOT NULL COMMENT '错误消息',
    stack_trace TEXT DEFAULT NULL COMMENT '堆栈跟踪 (可选)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_job_run_id (job_run_id),
    INDEX idx_error_category (error_category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='索引错误采样表 - Dead Letter Queue';
