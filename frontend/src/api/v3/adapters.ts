/**
 * V3 Data Adapters - MDP Platform V3.1
 * Convert V3 API responses to V1-compatible formats for backward compatibility.
 * This allows gradual migration of components without breaking changes.
 */

import {
  IV3Project,
  IV3ProjectWithStats,
  IV3SharedProperty,
  IV3ObjectTypeFull,
  IV3LinkTypeFull,
} from './types';

// Import V1 types for reference
import type { IOntologyProject, IObjectType, ILinkType, ISharedProperty } from '../ontology';

// ==========================================
// Project Adapters
// ==========================================

/**
 * Convert V3 Project to V1 IOntologyProject format.
 * V1 uses: title, tags, objectCount, linkCount, updatedAt
 * V3 uses: name, description, created_at, updated_at
 */
export function adaptProjectToV1(project: IV3Project | IV3ProjectWithStats): IOntologyProject {
  const isWithStats = 'object_count' in project;
  
  return {
    id: project.id,
    title: project.name,
    description: project.description,
    tags: [], // V3 doesn't have tags, default to empty
    objectCount: isWithStats ? (project as IV3ProjectWithStats).object_count : 0,
    linkCount: isWithStats ? (project as IV3ProjectWithStats).link_count : 0,
    updatedAt: project.updated_at,
  };
}

/**
 * Convert array of V3 Projects to V1 format.
 */
export function adaptProjectsToV1(
  projects: (IV3Project | IV3ProjectWithStats)[]
): IOntologyProject[] {
  return projects.map(adaptProjectToV1);
}

// ==========================================
// Shared Property Adapters
// ==========================================

/**
 * Convert V3 SharedProperty to V1 ISharedProperty format.
 * V1 uses: formatter
 * V3 uses: different structure (no formatter)
 */
export function adaptSharedPropertyToV1(prop: IV3SharedProperty): ISharedProperty {
  return {
    id: prop.id,
    api_name: prop.api_name,
    display_name: prop.display_name || prop.api_name,
    data_type: prop.data_type,
    formatter: null, // V3 doesn't have formatter in shared property
    description: prop.description,
    created_at: prop.created_at || undefined,
  };
}

/**
 * Convert array of V3 SharedProperties to V1 format.
 */
export function adaptSharedPropertiesToV1(props: IV3SharedProperty[]): ISharedProperty[] {
  return props.map(adaptSharedPropertyToV1);
}

// ==========================================
// Object Type Adapters
// ==========================================

/**
 * Convert V3 ObjectTypeFull to V1 IObjectType format.
 * V1 uses: property_schema (object)
 * V3 uses: properties (array with detailed binding info)
 */
export function adaptObjectTypeToV1(objType: IV3ObjectTypeFull): IObjectType {
  // Convert properties array to property_schema object
  const propertySchema: Record<string, any> = {};
  
  if (objType.properties && Array.isArray(objType.properties)) {
    objType.properties.forEach((prop) => {
      propertySchema[prop.api_name] = {
        type: prop.data_type,
        display_name: prop.display_name,
        required: prop.is_required,
        is_primary_key: prop.is_primary_key,
        is_title: prop.is_title,
        default_value: prop.default_value,
      };
    });
  }
  
  return {
    id: objType.id,
    api_name: objType.api_name,
    display_name: objType.display_name || objType.api_name,
    description: objType.description,
    project_id: null, // V3 uses project binding instead
    property_schema: propertySchema,
    created_at: undefined, // V3 def has created_at but not in full read
    updated_at: undefined,
  };
}

/**
 * Convert array of V3 ObjectTypes to V1 format.
 */
export function adaptObjectTypesToV1(objTypes: IV3ObjectTypeFull[]): IObjectType[] {
  return objTypes.map(adaptObjectTypeToV1);
}

// ==========================================
// Link Type Adapters
// ==========================================

/**
 * Convert V3 LinkTypeFull to V1 ILinkType format.
 * V1 uses: source_type_id, target_type_id, mapping_config
 * V3 uses: source_object_def_id, target_object_def_id
 */
export function adaptLinkTypeToV1(linkType: IV3LinkTypeFull): ILinkType {
  return {
    id: linkType.id,
    api_name: linkType.api_name,
    display_name: linkType.display_name || linkType.api_name,
    description: null,
    source_type_id: linkType.source_object_def_id || '',
    target_type_id: linkType.target_object_def_id || '',
    cardinality: linkType.cardinality || 'MANY_TO_MANY',
    mapping_config: undefined,
    created_at: undefined,
    updated_at: undefined,
  };
}

/**
 * Convert array of V3 LinkTypes to V1 format.
 */
export function adaptLinkTypesToV1(linkTypes: IV3LinkTypeFull[]): ILinkType[] {
  return linkTypes.map(adaptLinkTypeToV1);
}

// ==========================================
// Unified Fetch Functions with Automatic Adaptation
// ==========================================

import * as v3Api from './ontology';

/**
 * Fetch projects using V3 API, return V1-compatible format.
 */
export async function fetchProjectsCompat(): Promise<IOntologyProject[]> {
  const v3Projects = await v3Api.fetchProjects();
  return adaptProjectsToV1(v3Projects);
}

/**
 * Fetch shared properties using V3 API, return V1-compatible format.
 */
export async function fetchSharedPropertiesCompat(): Promise<ISharedProperty[]> {
  const v3Props = await v3Api.fetchSharedProperties();
  return adaptSharedPropertiesToV1(v3Props);
}

/**
 * Fetch object types using V3 API, return V1-compatible format.
 */
export async function fetchObjectTypesCompat(): Promise<IObjectType[]> {
  const v3Types = await v3Api.fetchObjectTypes();
  return adaptObjectTypesToV1(v3Types);
}

/**
 * Fetch link types using V3 API, return V1-compatible format.
 */
export async function fetchLinkTypesCompat(): Promise<ILinkType[]> {
  const v3Links = await v3Api.fetchLinkTypes();
  return adaptLinkTypesToV1(v3Links);
}
