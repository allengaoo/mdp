/**
 * V3 Objects API Functions - MDP Platform V3.1
 * API client functions for object type definitions with statistics.
 */
import v3Client from './client';

// ==========================================
// Type Definitions
// ==========================================

/**
 * Object type definition with aggregated statistics.
 * Maps to backend ObjectDefWithStats DTO.
 */
export interface IV3ObjectDefWithStats {
  id: string;
  api_name: string;
  stereotype: string;  // ENTITY, EVENT, DOCUMENT, MEDIA, METRIC
  display_name: string | null;
  description: string | null;
  status: string;  // DRAFT, PUBLISHED, DEPRECATED
  property_count: number;
  instance_count: number;
  created_at: string | null;
  updated_at: string | null;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Fetch all object type definitions with statistics.
 * 
 * @param projectId - Optional project ID to filter by
 * @returns List of object definitions with property_count and instance_count
 * 
 * @example
 * // Get all object types
 * const allObjects = await fetchObjectDefsWithStats();
 * 
 * // Get object types for a specific project
 * const projectObjects = await fetchObjectDefsWithStats('proj-001');
 */
export const fetchObjectDefsWithStats = async (
  projectId?: string
): Promise<IV3ObjectDefWithStats[]> => {
  const params: Record<string, string> = {};
  if (projectId) {
    params.project_id = projectId;
  }
  
  const response = await v3Client.get('/ontology/objects/with-stats', { params });
  return response.data || [];
};

/**
 * Fetch a single object type definition with statistics.
 * 
 * @param defId - Object type definition ID
 * @returns Object definition with statistics or null if not found
 */
export const fetchObjectDefWithStats = async (
  defId: string
): Promise<IV3ObjectDefWithStats | null> => {
  try {
    const allObjects = await fetchObjectDefsWithStats();
    return allObjects.find(obj => obj.id === defId) || null;
  } catch (error) {
    console.error('[V3] Failed to fetch object def with stats:', error);
    return null;
  }
};
