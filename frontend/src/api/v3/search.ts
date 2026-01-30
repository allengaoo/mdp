/**
 * V3 Search API Client
 * MDP Platform - Global Search Module
 * 
 * Provides hybrid search capabilities (text + vector + facets)
 */

import v3Client from './client';

// ==========================================
// Types
// ==========================================

export interface IFacetBucket {
  key: string;
  count: number;
}

export interface IFacet {
  field: string;
  display_name: string;
  buckets: IFacetBucket[];
}

export interface IObjectHit {
  id: string;
  object_type: string;
  object_type_display: string;
  display_name: string;
  score: number;
  properties: Record<string, any>;
  highlights?: Record<string, string[]>;
}

export interface IObjectSearchFilters {
  object_types?: string[];
  properties?: Record<string, string[]>;
  project_id?: string;
}

export interface IObjectSearchRequest {
  query_text?: string;
  query_vector?: number[];
  filters?: IObjectSearchFilters;
  page?: number;
  page_size?: number;
  sort_field?: string;
  sort_order?: 'asc' | 'desc';
}

export interface IObjectSearchResponse {
  hits: IObjectHit[];
  total: number;
  page: number;
  page_size: number;
  facets: IFacet[];
  query_text?: string;
}

export interface ISearchHealthResponse {
  status: string;
  cluster_name?: string;
  version?: string;
  message?: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Search objects using hybrid search (text + vector).
 */
export const searchObjects = async (
  request: IObjectSearchRequest
): Promise<IObjectSearchResponse> => {
  const response = await v3Client.post('/search/objects', request);
  return response.data;
};

/**
 * Get available facets for filtering.
 */
export const getSearchFacets = async (
  objectTypes?: string[]
): Promise<{ facets: IFacet[] }> => {
  const params: Record<string, string> = {};
  if (objectTypes && objectTypes.length > 0) {
    params.object_types = objectTypes.join(',');
  }
  const response = await v3Client.get('/search/objects/facets', { params });
  return response.data;
};

/**
 * Check Elasticsearch health.
 */
export const checkSearchHealth = async (): Promise<ISearchHealthResponse> => {
  const response = await v3Client.get('/search/health');
  return response.data;
};

/**
 * Ensure objects index exists.
 */
export const ensureObjectsIndex = async (): Promise<{ success: boolean; message: string }> => {
  const response = await v3Client.post('/search/objects/ensure-index');
  return response.data;
};

// ==========================================
// Helper Functions
// ==========================================

/**
 * Build filters from facet selections.
 */
export const buildFiltersFromSelections = (
  selections: Record<string, string[]>
): IObjectSearchFilters => {
  const filters: IObjectSearchFilters = {
    properties: {}
  };

  for (const [field, values] of Object.entries(selections)) {
    if (values && values.length > 0) {
      if (field === 'object_type') {
        filters.object_types = values;
      } else {
        // Remove 'properties.' prefix and '_kwd' suffix for display
        const cleanField = field
          .replace(/^properties\./, '')
          .replace(/_kwd$/, '');
        filters.properties![cleanField] = values;
      }
    }
  }

  return filters;
};

/**
 * Get icon for object type.
 */
export const getObjectTypeIcon = (objectType: string): string => {
  const iconMap: Record<string, string> = {
    target: '🎯',
    vessel: '🚢',
    aircraft: '✈️',
    sensor: '📡',
    intel_report: '📄',
    default: '📦'
  };
  return iconMap[objectType] || iconMap.default;
};

/**
 * Get color for object type.
 */
export const getObjectTypeColor = (objectType: string): string => {
  const colorMap: Record<string, string> = {
    target: '#ff4d4f',
    vessel: '#1890ff',
    aircraft: '#52c41a',
    sensor: '#722ed1',
    intel_report: '#faad14',
    default: '#8c8c8c'
  };
  return colorMap[objectType] || colorMap.default;
};
