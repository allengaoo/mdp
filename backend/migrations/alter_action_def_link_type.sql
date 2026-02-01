-- Migration: Add link_type_id to meta_action_def
-- This column stores the Link Type ID when operation_type is 'link_objects' or 'unlink_objects'

ALTER TABLE meta_action_def
ADD COLUMN link_type_id VARCHAR(64) NULL COMMENT 'Link Type ID for link_objects/unlink_objects operations';

-- Add index for better query performance
CREATE INDEX idx_action_def_link_type ON meta_action_def(link_type_id);
