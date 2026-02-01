-- Migration: Add link_type_id to meta_action_def table
-- Purpose: Support link_objects and unlink_objects operation types

ALTER TABLE meta_action_def
ADD COLUMN link_type_id VARCHAR(64) NULL COMMENT 'Associated Link Type ID (used when operation_type is link_objects or unlink_objects)';

-- Add index for faster lookups
CREATE INDEX idx_action_def_link_type ON meta_action_def(link_type_id);
