/**
 * Mapping API client for MDP Platform V3.1
 * Multimodal data mapping and vector indexing
 */
import v3Client from './client';

// Types
export interface MappingNode {
  id: string;
  type: 'source' | 'transform' | 'target';
  position: { x: number; y: number };
  data: {
    column?: string;      // for source
    function?: string;    // for transform
    property?: string;    // for target
    label?: string;
  };
}

export interface MappingEdge {
  id: string;
  source: string;
  target: string;
}

export interface MappingSpec {
  nodes: MappingNode[];
  edges: MappingEdge[];
}

export interface ObjectMappingDef {
  id: string;
  object_def_id: string;
  source_connection_id: string;
  source_table_name: string;
  mapping_spec: MappingSpec;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  created_at: string;
  updated_at: string;
}

export interface MappingPreviewRequest {
  source_connection_id: string;
  source_table_name: string;
  mapping_spec: MappingSpec;
  limit?: number;
}

export interface MappingPreviewResponse {
  columns: string[];
  data: Record<string, any>[];
  row_count: number;
  warnings?: string[];
}

// API Functions

export async function createMapping(data: {
  object_def_id: string;
  source_connection_id: string;
  source_table_name: string;
  mapping_spec: MappingSpec;
}): Promise<ObjectMappingDef> {
  const response = await v3Client.post('/mappings', data);
  return response.data;
}

export async function listMappings(params?: {
  object_def_id?: string;
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<ObjectMappingDef[]> {
  const response = await v3Client.get('/mappings', { params });
  return response.data;
}

export async function getMapping(mappingId: string): Promise<ObjectMappingDef> {
  const response = await v3Client.get(`/mappings/${mappingId}`);
  return response.data;
}

export async function updateMapping(
  mappingId: string,
  data: Partial<{
    source_table_name: string;
    mapping_spec: MappingSpec;
    status: string;
  }>
): Promise<ObjectMappingDef> {
  const response = await v3Client.put(`/mappings/${mappingId}`, data);
  return response.data;
}

export async function deleteMapping(mappingId: string): Promise<void> {
  await v3Client.delete(`/mappings/${mappingId}`);
}

export async function previewMapping(
  request: MappingPreviewRequest
): Promise<MappingPreviewResponse> {
  const response = await v3Client.post('/mappings/preview', request);
  return response.data;
}

export async function publishMapping(mappingId: string): Promise<ObjectMappingDef> {
  const response = await v3Client.post(`/mappings/${mappingId}/publish`);
  return response.data;
}

// Transform function options
export const TRANSFORM_FUNCTIONS = [
  { value: 'image_embedding_clip', label: 'AI: Image to Vector (CLIP)', outputType: 'vector' },
  { value: 'text_embedding', label: 'AI: Text to Vector', outputType: 'vector' },
  { value: 'to_uppercase', label: 'To Uppercase', outputType: 'string' },
  { value: 'to_lowercase', label: 'To Lowercase', outputType: 'string' },
  { value: 'format_date', label: 'Format Date', outputType: 'date' },
  { value: 'concat', label: 'Concatenate', outputType: 'string' },
];
