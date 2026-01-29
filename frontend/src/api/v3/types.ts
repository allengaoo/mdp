/**
 * V3 API Type Definitions - MDP Platform V3.1
 * TypeScript interfaces matching backend V3.1 response models.
 */

// ==========================================
// System Layer - Project
// ==========================================

export interface IV3Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface IV3ProjectWithStats extends IV3Project {
  object_count: number;
  link_count: number;
}

export interface IV3ProjectCreate {
  name: string;
  description?: string | null;
}

export interface IV3ProjectUpdate {
  name?: string;
  description?: string | null;
}

// ==========================================
// Ontology Layer - Shared Property
// ==========================================

export interface IV3SharedProperty {
  id: string;
  api_name: string;
  display_name: string | null;
  data_type: string;
  description: string | null;
  created_at: string | null;
}

export interface IV3SharedPropertyCreate {
  api_name: string;
  display_name?: string | null;
  data_type: string;
  description?: string | null;
}

export interface IV3SharedPropertyUpdate {
  display_name?: string | null;
  data_type?: string;
  description?: string | null;
}

// ==========================================
// Ontology Layer - Object Type
// ==========================================

export interface IV3ObjectTypeDef {
  id: string;
  api_name: string;
  stereotype: string;
  current_version_id: string | null;
  created_at: string | null;
}

export interface IV3ObjectTypeVer {
  id: string;
  def_id: string;
  version_number: string;
  display_name: string | null;
  description: string | null;
  icon: string | null;
  color: string | null;
  status: string;
  enable_global_search: boolean;
  enable_geo_index: boolean;
  enable_vector_index: boolean;
  cache_ttl_seconds: number;
  created_at: string | null;
}

export interface IV3ObjectTypeProperty {
  binding_id: number;
  property_def_id: string;
  /** API name of the shared property (for Use Shared Property dropdown). */
  shared_property_api_name?: string;
  /** Display name of the shared property. */
  shared_property_display_name?: string;
  api_name: string;
  display_name: string | null;
  data_type: string;
  is_primary_key: boolean;
  is_required: boolean;
  is_title: boolean;
  default_value: string | null;
  validation_rules: Record<string, unknown> | null;
}

export interface IV3ObjectTypeFull {
  // Definition fields
  id: string;
  api_name: string;
  stereotype: string;
  // Current version fields
  version_id: string | null;
  version_number: string | null;
  display_name: string | null;
  description: string | null;
  icon: string | null;
  color: string | null;
  status: string | null;
  // Properties
  properties: IV3ObjectTypeProperty[];
  // Datasource information
  datasource?: {
    type?: 'pipeline' | 'mapping';
    dataset_id?: string;
    dataset_name?: string;
    table_name?: string;
    db_type?: string;
    connection_id?: string;
    connection_name?: string;
    pipeline_id?: string;
    pipeline_mode?: string;
    sync_status?: string; // PENDING, RUNNING, SUCCESS, FAILED
    last_sync_time?: string;
    rows_processed?: number;
    source_table_name?: string; // For mapping type
    mapping_id?: string;
  } | null;
}

export interface IV3ObjectTypeCreate {
  api_name: string;
  stereotype?: string;
}

export interface IV3ObjectTypeVerCreate {
  def_id: string;
  version_number: string;
  display_name?: string | null;
  description?: string | null;
  icon?: string | null;
  color?: string | null;
  status?: string;
  enable_global_search?: boolean;
  enable_geo_index?: boolean;
  enable_vector_index?: boolean;
  cache_ttl_seconds?: number;
}

export interface IV3ObjectTypeVerUpdate {
  display_name?: string | null;
  description?: string | null;
  icon?: string | null;
  color?: string | null;
  status?: string;
  enable_global_search?: boolean;
  enable_geo_index?: boolean;
  enable_vector_index?: boolean;
  cache_ttl_seconds?: number;
}

// ==========================================
// Ontology Layer - Link Type
// ==========================================

export interface IV3LinkTypeDef {
  id: string;
  api_name: string;
  current_version_id: string | null;
  created_at: string | null;
}

export interface IV3LinkTypeVer {
  id: string;
  def_id: string;
  version_number: string;
  display_name: string | null;
  source_object_def_id: string;
  target_object_def_id: string;
  cardinality: string;
  status: string;
  created_at: string | null;
}

export interface IV3LinkTypeFull {
  // Definition fields
  id: string;
  api_name: string;
  // Current version fields
  version_id: string | null;
  version_number: string | null;
  display_name: string | null;
  source_object_def_id: string | null;
  target_object_def_id: string | null;
  cardinality: string | null;
  status: string | null;
  // Joined object type names
  source_type_name: string | null;
  target_type_name: string | null;
}

export interface IV3LinkTypeCreate {
  api_name: string;
  description?: string | null;
}

// ==========================================
// Context Layer - Project Object Binding
// ==========================================

export interface IV3ProjectObjectBinding {
  project_id: string;
  object_def_id: string;
  used_version_id: string;
  project_display_alias: string | null;
  is_visible: boolean;
}

export interface IV3ProjectObjectBindingWithDetails extends IV3ProjectObjectBinding {
  project_name: string | null;
  object_type_api_name: string | null;
  object_type_display_name: string | null;
  version_number: string | null;
}

export interface IV3ProjectObjectBindingCreate {
  project_id: string;
  object_def_id: string;
  used_version_id: string;
  project_display_alias?: string | null;
  is_visible?: boolean;
}

// ==========================================
// Utility Types
// ==========================================

export type DataType =
  | 'STRING'
  | 'INT'
  | 'DOUBLE'
  | 'BOOLEAN'
  | 'DATETIME'
  | 'GEO_POINT'
  | 'JSON'
  | 'VECTOR'
  | 'MEDIA_REF';

export type Stereotype = 'ENTITY' | 'EVENT' | 'DOCUMENT' | 'MEDIA' | 'METRIC';

export type VersionStatus = 'DRAFT' | 'PUBLISHED' | 'DEPRECATED';

export type Cardinality = 'ONE_TO_ONE' | 'ONE_TO_MANY' | 'MANY_TO_ONE' | 'MANY_TO_MANY';
