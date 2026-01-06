/**
 * API Payload Type Definitions
 * Strict TypeScript interfaces matching backend Pydantic models.
 * Using snake_case to match API response directly.
 */

// ==========================================
// Nested Property Definitions
// ==========================================

export interface IPropertyDef {
  key: string;
  label: string;
  type: string;
  required?: boolean;
  shared_property_id?: string | null;
}

// ==========================================
// Link Mapping Configuration
// ==========================================

export interface ILinkMappingConfig {
  join_table_id?: string | null;
  source_fk?: string | null;
  target_fk?: string | null;
  [key: string]: any; // Allow additional fields for backward compatibility
}

// ==========================================
// Action Parameter Definition
// ==========================================

export interface IActionParamDef {
  key: string;
  label: string;
  type: string;
}

// ==========================================
// Request Models
// ==========================================

export interface IObjectTypeRequest {
  api_name: string;
  display_name: string;
  project_id?: string | null;
  property_schema: IPropertyDef[];
  description?: string | null;
}

export interface ILinkTypeRequest {
  api_name: string;
  display_name?: string | null;
  source_type_id: string;
  target_type_id: string;
  cardinality: string;
  mapping_config?: ILinkMappingConfig | null;
}

export interface IActionRunRequest {
  action_api_name: string;
  source_object_id?: string | null; // Preferred field name
  source_id?: string | null; // Alias for source_object_id (backward compatibility)
  params?: Record<string, any>;
}

// ==========================================
// Response Models (for reference)
// ==========================================

export interface IActionRunResponse {
  success: boolean;
  result: any;
  action_api_name: string;
  source_id: string;
  message?: string | null;
}

