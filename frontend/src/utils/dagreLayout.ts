/**
 * Dagre layout utility for ReactFlow graphs.
 * Automatically calculates node positions based on graph structure.
 */
import dagre from 'dagre';
import { Node, Edge } from 'reactflow';

export interface DagreLayoutOptions {
  direction?: 'TB' | 'LR' | 'BT' | 'RL'; // Top-Bottom, Left-Right, etc.
  nodeWidth?: number;
  nodeHeight?: number;
  nodeSep?: number; // Horizontal separation between nodes
  rankSep?: number; // Vertical separation between ranks
}

const DEFAULT_OPTIONS: Required<DagreLayoutOptions> = {
  direction: 'TB',
  nodeWidth: 180,
  nodeHeight: 50,
  nodeSep: 50,
  rankSep: 100,
};

/**
 * Apply Dagre layout to ReactFlow nodes and edges.
 * @param nodes ReactFlow nodes (without positions)
 * @param edges ReactFlow edges
 * @param options Layout options
 * @returns Nodes with calculated positions and edges
 */
export function getLayoutedElements(
  nodes: Node[],
  edges: Edge[],
  options: DagreLayoutOptions = {}
): { nodes: Node[]; edges: Edge[] } {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: opts.direction,
    nodesep: opts.nodeSep,
    ranksep: opts.rankSep,
  });

  // Add nodes to dagre graph
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: opts.nodeWidth,
      height: opts.nodeHeight,
    });
  });

  // Add edges to dagre graph
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Calculate layout
  dagre.layout(dagreGraph);

  // Update node positions
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - opts.nodeWidth / 2,
        y: nodeWithPosition.y - opts.nodeHeight / 2,
      },
    };
  });

  return {
    nodes: layoutedNodes,
    edges,
  };
}

