/**
 * Ontology API client functions.
 * 
 * NOTE: This module now uses V3 API internally with adapters for backward compatibility.
 * For new code, consider using `api/v3/ontology.ts` directly.
 */
import apiClient from './axios';
import * as v3Api from './v3/ontology';
import { adaptProjectToV1, adaptObjectTypesToV1, adaptLinkTypesToV1, adaptSharedPropertiesToV1 } from './v3/adapters';

// ==========================================
// Type Definitions
// ==========================================

export interface IOntologyProject {
  id: string;
  title: string;
  description?: string | null;
  tags: string[];
  objectCount: number;
  linkCount: number;
  updatedAt?: string | null;
}

// ==========================================
// API Functions - Projects (V3 Backend)
// ==========================================

/**
 * Fetch all ontology projects with statistics.
 * @returns List of projects with objectCount and linkCount
 * 
 * @note Now uses V3 API internally with adapter for backward compatibility.
 */
export const fetchProjects = async (): Promise<IOntologyProject[]> => {
  try {
    // Use V3 API with stats and adapt to V1 format
    const v3Projects = await v3Api.fetchProjectsWithStats();
    return v3Projects.map(adaptProjectToV1);
  } catch (error) {
    console.error('[V3 Migration] fetchProjects failed, falling back to V1:', error);
    // Fallback to V1 API if V3 fails (for graceful degradation)
    const response = await apiClient.get('/meta/projects', {
      params: { limit: 100 },
    });
    return response.data || [];
  }
};

/**
 * Fetch a single project by ID.
 * @param projectId Project ID
 * @returns Project with statistics
 * 
 * @note Now uses V3 API internally with adapter for backward compatibility.
 */
export const fetchProjectById = async (projectId: string): Promise<IOntologyProject | null> => {
  try {
    // Use V3 API and adapt to V1 format
    const v3Project = await v3Api.fetchProjectById(projectId);
    if (!v3Project) return null;
    return adaptProjectToV1(v3Project);
  } catch (error) {
    console.error('[V3 Migration] fetchProjectById failed:', error);
    return null;
  }
};

// ==========================================
// Object Type Interfaces
// ==========================================

export interface IObjectType {
  id: string;
  api_name: string;
  display_name: string;
  description?: string | null;
  project_id?: string | null;
  property_schema?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

// ==========================================
// Link Type Interfaces
// ==========================================

export interface ILinkType {
  id: string;
  api_name: string;
  display_name: string;
  description?: string | null;
  source_type_id: string;
  target_type_id: string;
  cardinality: string;
  mapping_config?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Fetch object types, optionally filtered by projectId.
 * @param projectId Optional project ID to filter by
 * @returns List of object types
 * 
 * @note Now uses V3 API internally with adapter for backward compatibility.
 * Note: V3 uses project bindings instead of project_id field, so projectId filter
 * would need to use the project bindings API for accurate filtering.
 */
export const fetchObjectTypes = async (projectId?: string): Promise<IObjectType[]> => {
  try {
    // Use V3 API and adapt to V1 format
    const v3ObjectTypes = await v3Api.fetchObjectTypes();
    const adapted = adaptObjectTypesToV1(v3ObjectTypes);
    
    // Note: V3 doesn't have project_id in object types (uses bindings instead)
    // For now, return all object types. Project filtering would need different approach.
    if (projectId) {
      console.warn('[V3 Migration] projectId filtering not supported in V3 architecture');
    }
    return adapted;
  } catch (error) {
    console.error('[V3 Migration] fetchObjectTypes failed, falling back to V1:', error);
    // Fallback to V1 API
    const response = await apiClient.get('/meta/object-types', {
      params: {
        limit: 100,
        ...(projectId && { project_id: projectId }),
      },
    });
    const data = response.data || [];
    if (projectId) {
      return data.filter((item: IObjectType) => item.project_id === projectId);
    }
    return data;
  }
};

/**
 * Fetch all link types.
 * @returns List of link types
 * 
 * @note Now uses V3 API internally with adapter for backward compatibility.
 */
export const fetchLinkTypes = async (): Promise<ILinkType[]> => {
  try {
    // Use V3 API and adapt to V1 format
    const v3LinkTypes = await v3Api.fetchLinkTypes();
    return adaptLinkTypesToV1(v3LinkTypes);
  } catch (error) {
    console.error('[V3 Migration] fetchLinkTypes failed, falling back to V1:', error);
    // Fallback to V1 API
    const response = await apiClient.get('/meta/link-types', {
      params: { limit: 100 },
    });
    return response.data || [];
  }
};

// ==========================================
// DataSource Interfaces
// ==========================================

export interface IDataSourceTable {
  id: string;
  connection_id?: string; // V3 field
  table_name: string;
  db_type: string;
  columns_schema: Array<{
    name: string;
    type: string;
    length?: number;
    precision?: number;
    scale?: number;
  }> | string; // Can be array or JSON string
  created_at?: string;
}

// ==========================================
// Shared Property Interfaces
// ==========================================

export interface ISharedProperty {
  id: string;
  api_name: string;
  display_name: string;
  data_type: string;
  formatter?: string | null;
  description?: string | null;
  created_at?: string;
}

// ==========================================
// API Functions - DataSources & Shared Properties
// ==========================================

/**
 * Fetch all datasource tables.
 * @returns List of datasource tables
 */
export const fetchDatasources = async (): Promise<IDataSourceTable[]> => {
  const response = await apiClient.get('/meta/datasources', {
    params: {
      limit: 100,
    },
  });
  return response.data || [];
};

/**
 * Fetch all shared properties.
 * @returns List of shared properties
 * 
 * @note Now uses V3 API internally with adapter for backward compatibility.
 */
export const fetchSharedProperties = async (): Promise<ISharedProperty[]> => {
  try {
    // Use V3 API and adapt to V1 format
    const v3Props = await v3Api.fetchSharedProperties();
    return adaptSharedPropertiesToV1(v3Props);
  } catch (error) {
    console.error('[V3 Migration] fetchSharedProperties failed, falling back to V1:', error);
    // Fallback to V1 API
    const response = await apiClient.get('/meta/shared-properties', {
      params: { limit: 100 },
    });
    return response.data || [];
  }
};

// ==========================================
// API Functions - Object Type CRUD
// ==========================================

/**
 * Create a new object type.
 * @param data Object type data
 * @returns Created object type
 */
export const createObjectType = async (data: any): Promise<IObjectType> => {
  const response = await apiClient.post('/meta/object-types', data);
  return response.data;
};

/**
 * Update an existing object type.
 * @param id Object type ID
 * @param data Updated object type data
 * @returns Updated object type
 */
export const updateObjectType = async (id: string, data: any): Promise<IObjectType> => {
  const response = await apiClient.put(`/meta/object-types/${id}`, data);
  return response.data;
};

// ==========================================
// Execution Log Interfaces
// ==========================================

export interface IExecutionLog {
  id: string;
  action_id?: string | null;
  action_name: string;
  user_id?: string | null;
  status: 'SUCCESS' | 'FAILED';
  duration_ms: number;
  error_message?: string | null;
  request_params?: Record<string, any> | null;
  created_at?: string | null;
}

// ==========================================
// API Functions - Execution Logs
// ==========================================

/**
 * Fetch execution logs with optional filters.
 * @param params Optional query parameters for filtering
 * @returns List of execution logs
 */
export const fetchExecutionLogs = async (params?: {
  action_id?: string;
  user_id?: string;
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<IExecutionLog[]> => {
  const response = await apiClient.get('/execute/logs', { params });
  return response.data || [];
};

// ==========================================
// Object Instance Interfaces
// ==========================================

export interface IObjectInstance {
  id: string;
  object_type_id: string;
  properties: Record<string, any>;
  created_at?: string | null;
  updated_at?: string | null;
}

// ==========================================
// API Functions - Object Instances
// ==========================================

/**
 * Fetch object instances by type API name.
 * @param typeApiName Object type API name (e.g., 'fighter', 'target')
 * @param filters Optional JSON filters for properties
 * @returns List of object instances
 */
export const fetchObjectInstances = async (
  typeApiName: string,
  filters?: Record<string, any>
): Promise<IObjectInstance[]> => {
  const params: Record<string, any> = {};
  if (filters) {
    params.filters = JSON.stringify(filters);
  }
  const response = await apiClient.get(`/execute/objects/${typeApiName}`, { params });
  return response.data || [];
};

// ==========================================
// Action Definition Interfaces
// ==========================================

export interface IActionDefinition {
  id: string;
  api_name: string;
  display_name: string;
  backing_function_id: string;
}

export interface IActionRunRequest {
  action_api_name: string;
  source_object_id?: string;
  source_id?: string;
  params?: Record<string, any>;
}

export interface IActionRunResponse {
  success: boolean;
  result: any;
  action_api_name: string;
  source_id: string;
  message?: string;
}

// ==========================================
// API Functions - Action Definitions
// ==========================================

/**
 * Fetch all action definitions.
 * @returns List of action definitions
 */
export const fetchActionDefinitions = async (): Promise<IActionDefinition[]> => {
  const response = await apiClient.get('/meta/actions', {
    params: { limit: 100 },
  });
  return response.data || [];
};

/**
 * Execute a single action.
 * @param actionApiName The api_name of the action to execute
 * @param sourceId The source object instance ID
 * @param params Optional parameters for the action
 * @returns Execution result
 */
export const executeAction = async (
  actionApiName: string,
  sourceId: string,
  params?: Record<string, any>
): Promise<IActionRunResponse> => {
  const response = await apiClient.post('/execute/action/run', {
    action_api_name: actionApiName,
    source_id: sourceId,
    params: params || {},
  });
  return response.data;
};

/**
 * Execute multiple actions in sequence.
 * @param actions Array of action executions
 * @returns Array of execution results
 */
export const executeActionsBatch = async (
  actions: Array<{ actionApiName: string; sourceId: string; params?: Record<string, any> }>
): Promise<IActionRunResponse[]> => {
  const results: IActionRunResponse[] = [];
  for (const action of actions) {
    try {
      const result = await executeAction(action.actionApiName, action.sourceId, action.params);
      results.push(result);
    } catch (error: any) {
      results.push({
        success: false,
        result: null,
        action_api_name: action.actionApiName,
        source_id: action.sourceId,
        message: error.response?.data?.detail || error.message || 'Execution failed',
      });
    }
  }
  return results;
};