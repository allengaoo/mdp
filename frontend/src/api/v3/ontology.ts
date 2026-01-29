/**
 * V3 Ontology API Functions - MDP Platform V3.1
 * API client functions for V3.1 metadata-driven architecture.
 */
import v3Client from './client';
import {
  IV3Project,
  IV3ProjectWithStats,
  IV3ProjectCreate,
  IV3ProjectUpdate,
  IV3SharedProperty,
  IV3SharedPropertyCreate,
  IV3SharedPropertyUpdate,
  IV3ObjectTypeFull,
  IV3ObjectTypeCreate,
  IV3ObjectTypeVer,
  IV3ObjectTypeVerCreate,
  IV3ObjectTypeVerUpdate,
  IV3ObjectTypeProperty,
  IV3LinkTypeFull,
  IV3LinkTypeCreate,
  IV3ProjectObjectBindingWithDetails,
  IV3ProjectObjectBindingCreate,
} from './types';

// ==========================================
// Projects API
// ==========================================

/**
 * Fetch all projects.
 */
export const fetchProjects = async (): Promise<IV3Project[]> => {
  const response = await v3Client.get('/projects');
  return response.data || [];
};

/**
 * Fetch all projects with statistics.
 */
export const fetchProjectsWithStats = async (): Promise<IV3ProjectWithStats[]> => {
  const response = await v3Client.get('/projects/with-stats');
  return response.data || [];
};

/**
 * Fetch a single project by ID.
 */
export const fetchProjectById = async (projectId: string): Promise<IV3Project | null> => {
  try {
    const response = await v3Client.get(`/projects/${projectId}`);
    return response.data;
  } catch (error) {
    console.error('[V3] Failed to fetch project:', error);
    return null;
  }
};

/**
 * Create a new project.
 */
export const createProject = async (data: IV3ProjectCreate): Promise<IV3Project> => {
  const response = await v3Client.post('/projects', data);
  return response.data;
};

/**
 * Update an existing project.
 */
export const updateProject = async (
  projectId: string,
  data: IV3ProjectUpdate
): Promise<IV3Project> => {
  const response = await v3Client.patch(`/projects/${projectId}`, data);
  return response.data;
};

/**
 * Delete a project.
 */
export const deleteProject = async (projectId: string): Promise<void> => {
  await v3Client.delete(`/projects/${projectId}`);
};

// ==========================================
// Shared Properties API
// ==========================================

/**
 * Fetch all shared properties.
 */
export const fetchSharedProperties = async (): Promise<IV3SharedProperty[]> => {
  const response = await v3Client.get('/ontology/properties');
  return response.data || [];
};

/**
 * Fetch a shared property by ID.
 */
export const fetchSharedPropertyById = async (propId: string): Promise<IV3SharedProperty | null> => {
  try {
    const response = await v3Client.get(`/ontology/properties/${propId}`);
    return response.data;
  } catch (error) {
    console.error('[V3] Failed to fetch shared property:', error);
    return null;
  }
};

/**
 * Create a new shared property.
 */
export const createSharedProperty = async (
  data: IV3SharedPropertyCreate
): Promise<IV3SharedProperty> => {
  const response = await v3Client.post('/ontology/properties', data);
  return response.data;
};

/**
 * Update a shared property.
 */
export const updateSharedProperty = async (
  propId: string,
  data: IV3SharedPropertyUpdate
): Promise<IV3SharedProperty> => {
  const response = await v3Client.patch(`/ontology/properties/${propId}`, data);
  return response.data;
};

/**
 * Delete a shared property.
 */
export const deleteSharedProperty = async (propId: string): Promise<void> => {
  await v3Client.delete(`/ontology/properties/${propId}`);
};

// ==========================================
// Object Types API
// ==========================================

/**
 * Fetch all object types with full info (definition + current version).
 */
export const fetchObjectTypes = async (): Promise<IV3ObjectTypeFull[]> => {
  const response = await v3Client.get('/ontology/object-types');
  return response.data || [];
};

/**
 * Fetch an object type by ID with full info.
 */
export const fetchObjectTypeById = async (defId: string): Promise<IV3ObjectTypeFull | null> => {
  try {
    const response = await v3Client.get(`/ontology/object-types/${defId}`);
    return response.data;
  } catch (error) {
    console.error('[V3] Failed to fetch object type:', error);
    return null;
  }
};

/**
 * Create a new object type (definition + initial version).
 */
export const createObjectType = async (data: IV3ObjectTypeCreate): Promise<IV3ObjectTypeFull> => {
  const response = await v3Client.post('/ontology/object-types', data);
  return response.data;
};

/**
 * Fetch all versions for an object type.
 */
export const fetchObjectTypeVersions = async (defId: string): Promise<IV3ObjectTypeVer[]> => {
  const response = await v3Client.get(`/ontology/object-types/${defId}/versions`);
  return response.data || [];
};

/**
 * Create a new version for an object type.
 */
export const createObjectTypeVersion = async (
  defId: string,
  data: IV3ObjectTypeVerCreate
): Promise<IV3ObjectTypeVer> => {
  const response = await v3Client.post(`/ontology/object-types/${defId}/versions`, data);
  return response.data;
};

/**
 * Update an object type version.
 */
export const updateObjectTypeVersion = async (
  defId: string,
  verId: string,
  data: IV3ObjectTypeVerUpdate
): Promise<IV3ObjectTypeVer> => {
  const response = await v3Client.patch(`/ontology/object-types/${defId}/versions/${verId}`, data);
  return response.data;
};

/**
 * Fetch properties for an object type (current version).
 */
export const fetchObjectTypeProperties = async (
  defId: string
): Promise<IV3ObjectTypeProperty[]> => {
  const response = await v3Client.get(`/ontology/object-types/${defId}/properties`);
  return response.data || [];
};

/**
 * Bind a property to an object type (current version).
 */
export const bindPropertyToObjectType = async (
  defId: string,
  data: {
    property_def_id: string;
    local_api_name?: string;
    is_primary_key?: boolean;
    is_required?: boolean;
    is_title?: boolean;
    default_value?: string;
    validation_rules?: Record<string, unknown>;
  }
): Promise<void> => {
  await v3Client.post(`/ontology/object-types/${defId}/properties`, data);
};

// ==========================================
// Link Types API
// ==========================================

/**
 * Fetch all link types with full info (definition + current version).
 */
export const fetchLinkTypes = async (): Promise<IV3LinkTypeFull[]> => {
  const response = await v3Client.get('/ontology/link-types');
  return response.data || [];
};

/**
 * Fetch a link type by ID with full info.
 */
export const fetchLinkTypeById = async (defId: string): Promise<IV3LinkTypeFull | null> => {
  try {
    const response = await v3Client.get(`/ontology/link-types/${defId}`);
    return response.data;
  } catch (error) {
    console.error('[V3] Failed to fetch link type:', error);
    return null;
  }
};

/**
 * Create a new link type (definition + initial version).
 */
export const createLinkType = async (
  data: IV3LinkTypeCreate,
  sourceObjectDefId: string,
  targetObjectDefId: string,
  cardinality: string = 'MANY_TO_MANY',
  displayName?: string
): Promise<IV3LinkTypeFull> => {
  const response = await v3Client.post('/ontology/link-types', data, {
    params: {
      source_object_def_id: sourceObjectDefId,
      target_object_def_id: targetObjectDefId,
      cardinality,
      display_name: displayName,
    },
  });
  return response.data;
};

// ==========================================
// Link Mapping API
// ==========================================

export interface ILinkMapping {
  id: string;
  link_def_id: string;
  source_connection_id: string;
  join_table_name: string;
  source_key_column: string;
  target_key_column: string;
  property_mappings: Record<string, string>;
  status: string;
}

export interface ILinkMappingCreate {
  link_def_id: string;
  source_connection_id: string;
  join_table_name: string;
  source_key_column: string;
  target_key_column: string;
  property_mappings?: Record<string, string>;
}

export interface ILinkMappingUpdate {
  join_table_name?: string;
  source_key_column?: string;
  target_key_column?: string;
  property_mappings?: Record<string, string>;
  status?: string;
}

/**
 * Create a new link mapping.
 */
export const createLinkMapping = async (data: ILinkMappingCreate): Promise<ILinkMapping> => {
  const response = await v3Client.post('/mappings/link-mappings', data);
  return response.data;
};

/**
 * Get link mapping by link definition ID.
 */
export const getLinkMappingByDefId = async (linkDefId: string): Promise<ILinkMapping | null> => {
  try {
    const response = await v3Client.get(`/mappings/link-mappings/by-def/${linkDefId}`);
    return response.data;
  } catch (error) {
    // Return null if not found (404)
    return null;
  }
};

/**
 * Update a link mapping.
 */
export const updateLinkMapping = async (
  mappingId: string,
  data: ILinkMappingUpdate
): Promise<ILinkMapping> => {
  const response = await v3Client.put(`/mappings/link-mappings/${mappingId}`, data);
  return response.data;
};

// ==========================================
// Project Object Bindings API
// ==========================================

/**
 * Fetch object bindings for a project.
 */
export const fetchProjectObjects = async (
  projectId: string
): Promise<IV3ProjectObjectBindingWithDetails[]> => {
  const response = await v3Client.get(`/projects/${projectId}/objects`);
  return response.data || [];
};

/**
 * Bind an object type to a project.
 */
export const bindObjectToProject = async (
  projectId: string,
  data: IV3ProjectObjectBindingCreate
): Promise<IV3ProjectObjectBindingWithDetails> => {
  const response = await v3Client.post(`/projects/${projectId}/objects`, data);
  return response.data;
};

/**
 * Remove an object type binding from a project.
 */
export const unbindObjectFromProject = async (
  projectId: string,
  objectDefId: string
): Promise<void> => {
  await v3Client.delete(`/projects/${projectId}/objects/${objectDefId}`);
};

// ==========================================
// Project-scoped Object Types & Link Types API
// ==========================================

/**
 * Fetch object types bound to a specific project.
 * Only returns object types that are associated with the project via ctx_project_object_binding.
 */
export const fetchProjectObjectTypes = async (
  projectId: string
): Promise<IV3ObjectTypeFull[]> => {
  const response = await v3Client.get(`/projects/${projectId}/object-types`);
  return response.data || [];
};

/**
 * Fetch link types related to a specific project.
 * Returns link types where source OR target object type is bound to the project.
 */
export const fetchProjectLinkTypes = async (
  projectId: string
): Promise<IV3LinkTypeFull[]> => {
  const response = await v3Client.get(`/projects/${projectId}/link-types`);
  return response.data || [];
};

/**
 * Fetch shared properties used by a specific project.
 * Returns distinct shared properties that are bound to any object type
 * associated with the project via ctx_project_object_binding.
 */
export const fetchProjectSharedProperties = async (
  projectId: string
): Promise<IV3SharedProperty[]> => {
  const response = await v3Client.get(`/projects/${projectId}/shared-properties`);
  return response.data || [];
};
