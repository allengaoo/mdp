-- ============================================================
-- Migration: Add Search Configuration Flags to Property Bindings
-- MDP Platform V3.1 - Global Search Module
-- ============================================================
-- Purpose: Make indexing configurable per object-property binding.
--          Not all fields should be indexed the same way.
--
-- Flags:
--   is_searchable: Enable full-text search (ES text field)
--   is_filterable: Enable facets/aggregations (ES keyword field)
--   is_sortable:   Enable sorting (ES sortable field)
-- ============================================================

-- Add search configuration columns to rel_object_ver_property
ALTER TABLE rel_object_ver_property
ADD COLUMN is_searchable TINYINT(1) NOT NULL DEFAULT 0 
    COMMENT 'Enable full-text search indexing (ES text field)',
ADD COLUMN is_filterable TINYINT(1) NOT NULL DEFAULT 0 
    COMMENT 'Enable facet/aggregation indexing (ES keyword field)',
ADD COLUMN is_sortable TINYINT(1) NOT NULL DEFAULT 0 
    COMMENT 'Enable sorting capability (ES sortable field)';

-- Add index for efficient querying of searchable properties
CREATE INDEX idx_property_searchable ON rel_object_ver_property (is_searchable);
CREATE INDEX idx_property_filterable ON rel_object_ver_property (is_filterable);

-- ============================================================
-- Verification Query
-- ============================================================
-- SELECT 
--     ovp.id,
--     spd.api_name AS property_name,
--     ovp.is_searchable,
--     ovp.is_filterable,
--     ovp.is_sortable
-- FROM rel_object_ver_property ovp
-- JOIN meta_shared_property_def spd ON ovp.property_def_id = spd.id
-- LIMIT 10;
