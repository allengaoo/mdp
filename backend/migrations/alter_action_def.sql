-- Migration: Extend meta_action_def table for V3 Action Definition
-- Date: 2026-01-31

-- Add new columns to support full action definition structure
ALTER TABLE meta_action_def
ADD COLUMN description VARCHAR(500) NULL AFTER display_name,
ADD COLUMN operation_type VARCHAR(50) NULL AFTER description,
ADD COLUMN target_object_type_id VARCHAR(36) NULL AFTER operation_type,
ADD COLUMN parameters_schema JSON NULL AFTER target_object_type_id,
ADD COLUMN property_mapping JSON NULL AFTER parameters_schema,
ADD COLUMN validation_rules JSON NULL AFTER property_mapping,
ADD COLUMN project_id VARCHAR(36) NULL AFTER validation_rules;

-- Make backing_function_id optional (allow NULL)
ALTER TABLE meta_action_def
MODIFY COLUMN backing_function_id VARCHAR(36) NULL;

-- Add foreign key constraints (optional - can be added later if needed)
-- ALTER TABLE meta_action_def
-- ADD CONSTRAINT fk_action_target_object FOREIGN KEY (target_object_type_id) REFERENCES meta_object_type(id),
-- ADD CONSTRAINT fk_action_project FOREIGN KEY (project_id) REFERENCES meta_project(id);
