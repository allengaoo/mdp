-- Migration: Add project_id to meta_function_def
-- project_id: NULL = global function (OMA), non-null = project-scoped (Studio)

ALTER TABLE meta_function_def
ADD COLUMN project_id VARCHAR(36) NULL COMMENT 'Project ID - NULL for global functions, non-null for project-scoped';

CREATE INDEX idx_function_def_project ON meta_function_def(project_id);
