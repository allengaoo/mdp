/**
 * Ontology API client functions.
 */
import apiClient from './axios';

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
// API Functions
// ==========================================

/**
 * Fetch all ontology projects with statistics.
 * @returns List of projects with objectCount and linkCount
 */
export const fetchProjects = async (): Promise<IOntologyProject[]> => {
  const response = await apiClient.get('/meta/projects', {
    params: {
      limit: 100,
    },
  });
  return response.data || [];
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
 */
export const fetchObjectTypes = async (projectId?: string): Promise<IObjectType[]> => {
  const response = await apiClient.get('/meta/object-types', {
    params: {
      limit: 100,
      ...(projectId && { project_id: projectId }),
    },
  });
  const data = response.data || [];
  // Filter by projectId if provided (backend might not support filtering)
  if (projectId) {
    return data.filter((item: IObjectType) => item.project_id === projectId);
  }
  return data;
};

/**
 * Fetch all link types.
 * @returns List of link types
 */
export const fetchLinkTypes = async (): Promise<ILinkType[]> => {
  const response = await apiClient.get('/meta/link-types', {
    params: {
      limit: 100,
    },
  });
  return response.data || [];
};

// ==========================================
// DataSource Interfaces
// ==========================================

export interface IDataSourceTable {
  id: string;
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
  project_id: string;
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
 * Fetch shared properties, optionally filtered by projectId.
 * @param projectId Optional project ID to filter by
 * @returns List of shared properties
 */
export const fetchSharedProperties = async (projectId?: string): Promise<ISharedProperty[]> => {
  const response = await apiClient.get('/meta/shared-properties', {
    params: {
      limit: 100,
      ...(projectId && { project_id: projectId }),
    },
  });
  const data = response.data || [];
  // Filter by projectId if provided (backend might not support filtering)
  if (projectId) {
    return data.filter((item: ISharedProperty) => item.project_id === projectId);
  }
  return data;
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

