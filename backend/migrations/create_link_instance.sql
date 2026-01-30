-- ============================================================
-- Migration: Create sys_link_instance table
-- MDP Platform V3.1 - Graph Analysis Module
-- ============================================================
-- Purpose: Store link instances between object instances.
--          Supports temporal validity and custom properties.
-- ============================================================

CREATE TABLE IF NOT EXISTS sys_link_instance (
    id VARCHAR(36) PRIMARY KEY,
    
    -- Link type reference (schema)
    link_type_id VARCHAR(36),
    
    -- Polymorphic source/target
    source_instance_id VARCHAR(255) NOT NULL,
    target_instance_id VARCHAR(255) NOT NULL,
    
    -- Object types for quick filtering
    source_object_type VARCHAR(100),
    target_object_type VARCHAR(100),
    
    -- Temporal validity
    valid_start DATETIME,
    valid_end DATETIME,
    
    -- Custom properties (JSON)
    properties JSON,
    
    -- Audit
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_link_source (source_instance_id),
    INDEX idx_link_target (target_instance_id),
    INDEX idx_link_type (link_type_id),
    INDEX idx_link_temporal (valid_start, valid_end),
    INDEX idx_link_source_type (source_object_type),
    INDEX idx_link_target_type (target_object_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Verification
-- ============================================================
-- SELECT TABLE_NAME, ENGINE, TABLE_ROWS 
-- FROM information_schema.TABLES 
-- WHERE TABLE_SCHEMA = 'ontology_meta_new' AND TABLE_NAME = 'sys_link_instance';
