/**
 * V3 Topology API Functions - MDP Platform V3.1
 * API client functions for ontology topology graph visualization.
 */
import v3Client from './client';

// ==========================================
// Type Definitions
// ==========================================

/**
 * Node data for topology visualization.
 * Maps to: meta_object_type_def JOIN meta_object_type_ver
 */
export interface ITopologyNode {
  id: string;                    // ObjectTypeDef.id
  api_name: string;              // ObjectTypeDef.api_name
  display_name: string | null;   // ObjectTypeVer.display_name
  stereotype: string;            // ObjectTypeDef.stereotype (ENTITY, EVENT, DOCUMENT, MEDIA, METRIC)
  icon: string | null;           // ObjectTypeVer.icon
  color: string | null;          // ObjectTypeVer.color
}

/**
 * Edge data for topology visualization.
 * Maps to: meta_link_type_def JOIN meta_link_type_ver
 */
export interface ITopologyEdge {
  id: string;                    // LinkTypeDef.id
  api_name: string;              // LinkTypeDef.api_name
  display_name: string | null;   // LinkTypeVer.display_name
  source: string;                // LinkTypeVer.source_object_def_id
  target: string;                // LinkTypeVer.target_object_def_id
  cardinality: string | null;    // LinkTypeVer.cardinality (ONE_TO_ONE, ONE_TO_MANY, etc.)
}

/**
 * Complete topology graph data.
 */
export interface ITopologyData {
  nodes: ITopologyNode[];
  edges: ITopologyEdge[];
}

// ==========================================
// API Functions
// ==========================================

/**
 * Fetch ontology topology graph data.
 * 
 * @returns Topology data with nodes (object types) and edges (link types)
 * 
 * @example
 * const topology = await fetchOntologyTopology();
 * console.log(`${topology.nodes.length} nodes, ${topology.edges.length} edges`);
 */
export const fetchOntologyTopology = async (): Promise<ITopologyData> => {
  const response = await v3Client.get('/ontology/topology');
  return response.data || { nodes: [], edges: [] };
};
