/**
 * Graph Analysis API Client
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Provides functions for graph expansion, shortest path, and statistics.
 */

import axiosInstance from "../axios";

// ==========================================
// Types & Interfaces
// ==========================================

export interface IGraphNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    object_type: string;
    icon: string;
    color: string;
    type_label: string;
    is_seed?: boolean;
  };
}

export interface IGraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  animated?: boolean;
  style?: Record<string, unknown>;
  label?: string;
  data?: {
    role?: string;
    properties?: Record<string, unknown>;
    valid_start?: string;
    valid_end?: string;
  };
}

export interface IGraphDTO {
  nodes: IGraphNode[];
  edges: IGraphEdge[];
}

export interface IExpandOptions {
  semantic?: boolean;
  limit?: number;
  depth?: number;
  link_types?: string[];
}

export interface IExpandRequest {
  seed_ids: string[];
  options?: IExpandOptions;
}

export interface IShortestPathRequest {
  source: string;
  target: string;
  max_depth?: number;
}

export interface IShortestPathResponse {
  found: boolean;
  path: string[];
  edges: IGraphEdge[];
  distance: number;
}

export interface ILinkTypeStat {
  source: string;
  target: string;
  count: number;
}

export interface IGraphStats {
  total_links: number;
  unique_nodes: number;
  link_types: ILinkTypeStat[];
}

export interface INodeTypeConfig {
  type: string;
  icon: string;
  color: string;
  label: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Expand graph from seed nodes
 */
export async function expandGraph(
  seedIds: string[],
  options?: IExpandOptions
): Promise<IGraphDTO> {
  const response = await axiosInstance.post<IGraphDTO>("/../v3/graph/expand", {
    seed_ids: seedIds,
    options,
  });
  return response.data;
}

/**
 * Find shortest path between two nodes
 */
export async function findShortestPath(
  source: string,
  target: string,
  maxDepth?: number
): Promise<IShortestPathResponse> {
  const response = await axiosInstance.post<IShortestPathResponse>(
    "/../v3/graph/shortest-path",
    {
      source,
      target,
      max_depth: maxDepth || 10,
    }
  );
  return response.data;
}

/**
 * Get graph statistics
 */
export async function getGraphStats(): Promise<IGraphStats> {
  const response = await axiosInstance.get<IGraphStats>("/../v3/graph/stats");
  return response.data;
}

/**
 * Get neighbors of a specific node
 */
export async function getNodeNeighbors(
  nodeId: string,
  limit?: number,
  includeSemantic?: boolean
): Promise<IGraphDTO> {
  const params = new URLSearchParams();
  if (limit) params.append("limit", limit.toString());
  if (includeSemantic) params.append("include_semantic", "true");

  const response = await axiosInstance.get<IGraphDTO>(
    `/../v3/graph/node/${nodeId}?${params.toString()}`
  );
  return response.data;
}

/**
 * Get available node types and their visual configuration
 */
export async function getNodeTypes(): Promise<{ types: INodeTypeConfig[] }> {
  const response = await axiosInstance.get<{ types: INodeTypeConfig[] }>(
    "/../v3/graph/types"
  );
  return response.data;
}

// ==========================================
// Helper Functions
// ==========================================

/**
 * Get color for a node type
 */
export function getNodeColor(objectType: string): string {
  const colorMap: Record<string, string> = {
    target: "#ff4d4f",
    vessel: "#1890ff",
    aircraft: "#52c41a",
    mission: "#722ed1",
    sensor: "#faad14",
    intel_report: "#13c2c2",
    port: "#eb2f96",
    command_unit: "#fa541c",
    recon_image: "#2f54eb",
    source: "#a0d911",
  };
  return colorMap[objectType] || "#8c8c8c";
}

/**
 * Get icon for a node type
 */
export function getNodeIcon(objectType: string): string {
  const iconMap: Record<string, string> = {
    target: "🎯",
    vessel: "🚢",
    aircraft: "✈️",
    mission: "📋",
    sensor: "📡",
    intel_report: "📄",
    port: "⚓",
    command_unit: "🎖️",
    recon_image: "📷",
    source: "🔍",
  };
  return iconMap[objectType] || "📦";
}

/**
 * Get Chinese label for a node type
 */
export function getNodeTypeLabel(objectType: string): string {
  const labelMap: Record<string, string> = {
    target: "目标",
    vessel: "舰船",
    aircraft: "飞机",
    mission: "任务",
    sensor: "传感器",
    intel_report: "情报",
    port: "港口",
    command_unit: "指挥单位",
    recon_image: "侦察图像",
    source: "情报源",
  };
  return labelMap[objectType] || "对象";
}

/**
 * Convert backend graph data to React Flow format
 */
export function toReactFlowFormat(graphDTO: IGraphDTO): {
  nodes: IGraphNode[];
  edges: IGraphEdge[];
} {
  // Fix node icons and labels (backend sends Unicode, we use local mapping)
  const nodes = graphDTO.nodes.map((node) => ({
    ...node,
    id: String(node.id), // UNIT 3: Ensure ID is always string
    data: {
      ...node.data,
      icon: getNodeIcon(node.data.object_type),
      type_label: getNodeTypeLabel(node.data.object_type),
    },
  }));

  // UNIT 3: Ensure edge IDs, sources, and targets are strings
  const edges = graphDTO.edges.map((edge) => ({
    ...edge,
    id: String(edge.id),
    source: String(edge.source),
    target: String(edge.target),
  }));

  // UNIT 3: Validate ID matching
  const nodeIdSet = new Set(nodes.map(n => n.id));
  const invalidEdges = edges.filter(
    e => !nodeIdSet.has(e.source) || !nodeIdSet.has(e.target)
  );
  
  if (invalidEdges.length > 0) {
    console.warn('[toReactFlowFormat] Found edges with missing nodes:', invalidEdges);
  }

  return { nodes, edges };
}
