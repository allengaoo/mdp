-- Migration: Add source_key_column and target_key_column to meta_link_type_ver
-- Purpose: Store key column mapping for 1:N, N:1, 1:1 relationships
-- Date: 2026-01-30

-- Add columns to meta_link_type_ver
ALTER TABLE meta_link_type_ver 
ADD COLUMN source_key_column VARCHAR(100) NULL COMMENT 'Source table key column (usually primary key)',
ADD COLUMN target_key_column VARCHAR(100) NULL COMMENT 'Target table key column (foreign key for 1:N, or join key)';

-- Verify columns were added
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'meta_link_type_ver'
  AND COLUMN_NAME IN ('source_key_column', 'target_key_column');
