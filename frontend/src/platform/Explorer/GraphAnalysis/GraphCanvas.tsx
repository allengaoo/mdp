/**
 * GraphCanvas - Main Graph Visualization Component
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Features:
 * - React Flow canvas with custom nodes and edges
 * - Context menu for node expansion
 * - Multi-seed support
 * - Dagre/Force-directed layout
 */

import React, {
  useState,
  useCallback,
  useEffect,
  useMemo,
  useRef,
} from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  NodeMouseHandler,
  BackgroundVariant,
} from "reactflow";
import { message, Spin, Dropdown, Menu } from "antd";
import type { MenuProps } from "antd";
import dagre from "dagre";
import "reactflow/dist/style.css";

import ObjectNode from "./ObjectNode";
import {
  expandGraph,
  toReactFlowFormat,
  getNodeColor,
  IGraphNode,
  IGraphEdge,
} from "../../../api/v3/graph";

// Register custom node types
const nodeTypes = {
  objectNode: ObjectNode,
};

// Edge styles
const defaultEdgeOptions = {
  style: { stroke: "#666", strokeWidth: 1.5 },
  labelStyle: { fill: "#aaa", fontSize: 10 },
  labelBgStyle: { fill: "#1f1f1f", fillOpacity: 0.8 },
  labelBgPadding: [4, 2] as [number, number],
  labelBgBorderRadius: 3,
};

// Dagre layout configuration
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  direction: "TB" | "LR" = "TB"
) => {
  console.log('[GraphCanvas] getLayoutedElements called');
  console.log('[GraphCanvas] Layout - Input nodes count:', nodes.length);
  console.log('[GraphCanvas] Layout - Input edges count:', edges.length);
  console.log('[GraphCanvas] Layout - Direction:', direction);
  console.log('[GraphCanvas] Layout - Node IDs:', nodes.map(n => ({ id: n.id, type: typeof n.id })));
  console.log('[GraphCanvas] Layout - Edge sources/targets:', 
    edges.map(e => ({ 
      source: e.source, 
      sourceType: typeof e.source,
      target: e.target,
      targetType: typeof e.target 
    }))
  );
  
  const isHorizontal = direction === "LR";
  dagreGraph.setGraph({ rankdir: direction, nodesep: 80, ranksep: 100 });

  // Check for ID mismatches before adding to dagre
  const nodeIdSet = new Set(nodes.map(n => String(n.id)));
  const edgeSourceIds = edges.map(e => String(e.source));
  const edgeTargetIds = edges.map(e => String(e.target));
  const missingSources = edgeSourceIds.filter(id => !nodeIdSet.has(id));
  const missingTargets = edgeTargetIds.filter(id => !nodeIdSet.has(id));
  
  if (missingSources.length > 0) {
    console.warn('[GraphCanvas] Layout - Missing source nodes:', missingSources);
  }
  if (missingTargets.length > 0) {
    console.warn('[GraphCanvas] Layout - Missing target nodes:', missingTargets);
  }

  nodes.forEach((node) => {
    dagreGraph.setNode(String(node.id), { width: 150, height: 60 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(String(edge.source), String(edge.target));
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(String(node.id));
    if (!nodeWithPosition) {
      console.warn('[GraphCanvas] Layout - Node not found in dagre graph:', node.id);
      return {
        ...node,
        position: { x: 0, y: 0 },
      };
    }
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 75,
        y: nodeWithPosition.y - 30,
      },
    };
  });

  console.log('[GraphCanvas] Layout - Output nodes:', layoutedNodes.slice(0, 3).map(n => ({
    id: n.id,
    position: n.position,
  })));

  return { nodes: layoutedNodes, edges };
};

interface GraphCanvasProps {
  seedIds: string[];
  showSemantic: boolean;
  showHardLinks: boolean;
  layout: "dagre" | "force" | "circular";
  timeRange?: [Date, Date] | null;
  visibleTypes?: Set<string>;
  searchQuery?: string;
  onNodeSelect?: (nodeId: string) => void;
}

// Force-directed layout (simple spring simulation)
const getForceLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  // Simple force-directed positioning
  const nodePositions: { [key: string]: { x: number; y: number } } = {};
  const centerX = 400;
  const centerY = 300;
  
  // Initialize positions randomly around center
  nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / nodes.length;
    const radius = 150 + Math.random() * 100;
    nodePositions[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });
  
  // Simple spring simulation (few iterations)
  for (let iter = 0; iter < 50; iter++) {
    // Repulsion between all nodes
    nodes.forEach((node1) => {
      nodes.forEach((node2) => {
        if (node1.id !== node2.id) {
          const dx = nodePositions[node1.id].x - nodePositions[node2.id].x;
          const dy = nodePositions[node1.id].y - nodePositions[node2.id].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 5000 / (dist * dist);
          nodePositions[node1.id].x += (dx / dist) * force * 0.1;
          nodePositions[node1.id].y += (dy / dist) * force * 0.1;
        }
      });
    });
    
    // Attraction along edges
    edges.forEach((edge) => {
      const source = nodePositions[edge.source];
      const target = nodePositions[edge.target];
      if (source && target) {
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (dist - 150) * 0.05;
        source.x += (dx / dist) * force;
        source.y += (dy / dist) * force;
        target.x -= (dx / dist) * force;
        target.y -= (dy / dist) * force;
      }
    });
  }
  
  const layoutedNodes = nodes.map((node) => ({
    ...node,
    position: nodePositions[node.id] || { x: 0, y: 0 },
  }));
  
  return { nodes: layoutedNodes, edges };
};

// Circular layout
const getCircularLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const centerX = 400;
  const centerY = 300;
  const radius = Math.max(150, nodes.length * 25);
  
  const layoutedNodes = nodes.map((node, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return {
      ...node,
      position: {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      },
    };
  });
  
  return { nodes: layoutedNodes, edges };
};

// Apply layout based on type
const applyLayout = (
  nodes: Node[],
  edges: Edge[],
  layout: "dagre" | "force" | "circular"
) => {
  console.log('[GraphCanvas] applyLayout called with layout type:', layout);
  console.log('[GraphCanvas] applyLayout - Nodes before:', nodes.length);
  console.log('[GraphCanvas] applyLayout - Edges before:', edges.length);
  
  let result;
  switch (layout) {
    case "force":
      console.log('[GraphCanvas] applyLayout - Using force layout');
      result = getForceLayoutedElements(nodes, edges);
      break;
    case "circular":
      console.log('[GraphCanvas] applyLayout - Using circular layout');
      result = getCircularLayoutedElements(nodes, edges);
      break;
    case "dagre":
    default:
      console.log('[GraphCanvas] applyLayout - Using dagre layout');
      result = getLayoutedElements(nodes, edges, "TB");
      break;
  }
  
  console.log('[GraphCanvas] applyLayout - Nodes after:', result.nodes.length);
  console.log('[GraphCanvas] applyLayout - Edges after:', result.edges.length);
  
  return result;
};

const GraphCanvasInner: React.FC<GraphCanvasProps> = ({
  seedIds,
  showSemantic,
  showHardLinks,
  layout,
  timeRange,
  visibleTypes,
  searchQuery,
  onNodeSelect,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    nodeId: string;
  } | null>(null);
  const [rawGraphData, setRawGraphData] = useState<any>(null); // Unit 4: Debug UI
  const [showDebugPanel, setShowDebugPanel] = useState(false); // Unit 4: Debug UI toggle
  
  const expandedNodes = useRef<Set<string>>(new Set());

  // Fetch graph data when seeds change
  useEffect(() => {
    if (seedIds.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const fetchGraph = async () => {
      setLoading(true);
      try {
        console.log('[GraphCanvas] Fetching graph for seedIds:', seedIds);
        
        const result = await expandGraph(seedIds, {
          semantic: showSemantic,
          limit: 50,
        });

        // Debug: Log raw API result
        console.log('[GraphCanvas] ========================================');
        console.log('[GraphCanvas] Raw API result:', result);
        console.log('[GraphCanvas] Raw nodes count:', result.nodes?.length || 0);
        console.log('[GraphCanvas] Raw edges count:', result.edges?.length || 0);
        console.log('[GraphCanvas] Raw nodes:', JSON.stringify(result.nodes, null, 2));
        console.log('[GraphCanvas] Raw edges:', JSON.stringify(result.edges, null, 2));

        const { nodes: graphNodes, edges: graphEdges } =
          toReactFlowFormat(result);

        // Debug: Log after format conversion
        console.log('[GraphCanvas] After toReactFlowFormat:');
        console.log('[GraphCanvas] Graph nodes count:', graphNodes.length);
        console.log('[GraphCanvas] Graph edges count:', graphEdges.length);
        console.log('[GraphCanvas] Graph nodes:', graphNodes);
        console.log('[GraphCanvas] Graph edges:', graphEdges);

        // Convert to React Flow format
        const rfNodes: Node[] = graphNodes.map((n) => ({
          id: String(n.id), // Ensure string type
          type: "objectNode",
          position: n.position,
          data: n.data,
        }));

        const rfEdges: Edge[] = graphEdges.map((e) => ({
          id: String(e.id), // Ensure string type
          source: String(e.source), // Ensure string type
          target: String(e.target), // Ensure string type
          type: e.type === "semantic" ? "default" : "default",
          animated: e.type === "semantic",
          label: e.label,
          style: e.type === "semantic" 
            ? { stroke: "#722ed1", strokeDasharray: "5,5" } 
            : { stroke: getNodeColor(graphNodes.find(n => n.id === e.source)?.data.object_type || "") },
          data: e.data,
        }));

        // Debug: Log ReactFlow format and ID types
        console.log('[GraphCanvas] ReactFlow nodes:', rfNodes);
        console.log('[GraphCanvas] ReactFlow edges:', rfEdges);
        console.log('[GraphCanvas] Node IDs (with types):', 
          rfNodes.map(n => ({ id: n.id, type: typeof n.id, value: n.id }))
        );
        console.log('[GraphCanvas] Edge sources (with types):', 
          rfEdges.map(e => ({ source: e.source, type: typeof e.source, value: e.source }))
        );
        console.log('[GraphCanvas] Edge targets (with types):', 
          rfEdges.map(e => ({ target: e.target, type: typeof e.target, value: e.target }))
        );
        
        // Debug: Check ID matching
        const nodeIdSet = new Set(rfNodes.map(n => String(n.id)));
        const edgeSourceIds = rfEdges.map(e => String(e.source));
        const edgeTargetIds = rfEdges.map(e => String(e.target));
        const missingSourceIds = edgeSourceIds.filter(id => !nodeIdSet.has(id));
        const missingTargetIds = edgeTargetIds.filter(id => !nodeIdSet.has(id));
        
        if (missingSourceIds.length > 0) {
          console.warn('[GraphCanvas] Missing source node IDs:', missingSourceIds);
        }
        if (missingTargetIds.length > 0) {
          console.warn('[GraphCanvas] Missing target node IDs:', missingTargetIds);
        }
        console.log('[GraphCanvas] ID matching check - All sources found:', missingSourceIds.length === 0);
        console.log('[GraphCanvas] ID matching check - All targets found:', missingTargetIds.length === 0);

        // ========================================
        // UNIT 2: Layout Verification
        // ========================================
        // CRITICAL: Layout MUST be applied AFTER data fetch/conversion and BEFORE setNodes/setEdges
        // This ensures nodes have positions before React Flow renders them
        console.log('[GraphCanvas] ========================================');
        console.log('[GraphCanvas] UNIT 2: Layout Verification');
        console.log('[GraphCanvas] Step 1: Data fetched and converted ✓');
        console.log('[GraphCanvas] Step 2: Applying layout NOW (before setNodes)');
        console.log('[GraphCanvas] Applying layout:', layout);
        
        const { nodes: layoutedNodes, edges: layoutedEdges } =
          applyLayout(rfNodes, rfEdges, layout);

        console.log('[GraphCanvas] Step 3: Layout applied ✓');
        console.log('[GraphCanvas] Layouted nodes count:', layoutedNodes.length);
        console.log('[GraphCanvas] Layouted edges count:', layoutedEdges.length);
        console.log('[GraphCanvas] Layouted nodes (first 3):', layoutedNodes.slice(0, 3).map(n => ({
          id: n.id,
          position: n.position,
        })));
        console.log('[GraphCanvas] Step 4: Setting nodes/edges (will trigger render)');
        console.log('[GraphCanvas] ========================================');

        // Store raw data for debugging UI (Unit 4)
        setRawGraphData(result);

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        
        // Track expanded nodes
        seedIds.forEach(id => expandedNodes.current.add(id));
      } catch (error) {
        console.error("Failed to fetch graph:", error);
        message.error("获取图数据失败");
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [seedIds, showSemantic, layout]);
  
  // Re-apply layout when layout type changes
  useEffect(() => {
    if (nodes.length > 0) {
      console.log('[GraphCanvas] Layout type changed, re-applying layout:', layout);
      console.log('[GraphCanvas] Current nodes count:', nodes.length);
      console.log('[GraphCanvas] Current edges count:', edges.length);
      
      const { nodes: layoutedNodes, edges: layoutedEdges } = applyLayout(nodes, edges, layout);
      
      console.log('[GraphCanvas] Re-layout complete - Nodes:', layoutedNodes.length);
      console.log('[GraphCanvas] Re-layout complete - Edges:', layoutedEdges.length);
      
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    }
  }, [layout]);

  // Filter nodes based on visible types and search query
  const filteredNodes = useMemo(() => {
    let result = nodes;
    
    // Filter by visible types
    if (visibleTypes && visibleTypes.size > 0) {
      result = result.filter((node) => {
        const objectType = node.data?.object_type;
        return !objectType || visibleTypes.has(objectType);
      });
    }
    
    // Highlight search matches
    if (searchQuery && searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.map((node) => ({
        ...node,
        data: {
          ...node.data,
          isHighlighted: node.id.toLowerCase().includes(query) ||
                         node.data?.label?.toLowerCase().includes(query),
        },
      }));
    }
    
    return result;
  }, [nodes, visibleTypes, searchQuery]);

  // Get visible node IDs for edge filtering
  const visibleNodeIds = useMemo(() => {
    return new Set(filteredNodes.map((n) => n.id));
  }, [filteredNodes]);

  // Filter edges based on time range, hard links toggle, and visible nodes
  const filteredEdges = useMemo(() => {
    if (!showHardLinks) return [];
    
    let result = edges.filter((edge) => {
      // Only show edges where both nodes are visible
      return visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target);
    });

    // Filter by time range if set
    if (timeRange) {
      result = result.filter((edge) => {
        const data = edge.data as IGraphEdge["data"];
        if (!data?.valid_start || !data?.valid_end) return true;

        const edgeStart = new Date(data.valid_start);
        const edgeEnd = new Date(data.valid_end);

        return edgeStart <= timeRange[1] && edgeEnd >= timeRange[0];
      });
    }
    
    return result;
  }, [edges, timeRange, showHardLinks, visibleNodeIds]);

  // Handle node click
  const onNodeClick: NodeMouseHandler = useCallback(
    (event, node) => {
      onNodeSelect?.(node.id);
    },
    [onNodeSelect]
  );

  // Handle node context menu (right-click)
  const onNodeContextMenu: NodeMouseHandler = useCallback(
    (event, node) => {
      event.preventDefault();
      setContextMenu({
        x: event.clientX,
        y: event.clientY,
        nodeId: node.id,
      });
    },
    []
  );

  // Expand from selected node
  const handleExpandNode = useCallback(
    async (nodeId: string) => {
      if (expandedNodes.current.has(nodeId)) {
        message.info("该节点已展开");
        return;
      }

      setLoading(true);
      try {
        console.log('[GraphCanvas] Expanding node:', nodeId);
        
        const result = await expandGraph([nodeId], {
          semantic: showSemantic,
          limit: 20,
        });

        // Debug: Log expansion result
        console.log('[GraphCanvas] Expand result:', result);
        console.log('[GraphCanvas] Expand - New nodes count:', result.nodes?.length || 0);
        console.log('[GraphCanvas] Expand - New edges count:', result.edges?.length || 0);

        const { nodes: newGraphNodes, edges: newGraphEdges } =
          toReactFlowFormat(result);

        console.log('[GraphCanvas] Expand - After format conversion:');
        console.log('[GraphCanvas] Expand - New graph nodes:', newGraphNodes);
        console.log('[GraphCanvas] Expand - New graph edges:', newGraphEdges);

        // UNIT 3: ID Matching Verification for expansion
        const newNodeIdSet = new Set(newGraphNodes.map(n => String(n.id)));
        const newEdgeSourceIds = newGraphEdges.map(e => String(e.source));
        const newEdgeTargetIds = newGraphEdges.map(e => String(e.target));
        const newMissingSources = newEdgeSourceIds.filter(id => !newNodeIdSet.has(id));
        const newMissingTargets = newEdgeTargetIds.filter(id => !newNodeIdSet.has(id));
        
        if (newMissingSources.length > 0) {
          console.warn('[GraphCanvas] Expand - Missing source node IDs:', newMissingSources);
        }
        if (newMissingTargets.length > 0) {
          console.warn('[GraphCanvas] Expand - Missing target node IDs:', newMissingTargets);
        }
        console.log('[GraphCanvas] Expand - ID matching check - All sources found:', newMissingSources.length === 0);
        console.log('[GraphCanvas] Expand - ID matching check - All targets found:', newMissingTargets.length === 0);

        // Merge with existing data
        const existingNodeIds = new Set(nodes.map((n) => String(n.id)));
        const existingEdgeIds = new Set(edges.map((e) => String(e.id)));

        console.log('[GraphCanvas] Expand - Existing node IDs:', Array.from(existingNodeIds));
        console.log('[GraphCanvas] Expand - Existing edge IDs:', Array.from(existingEdgeIds));

        const addedNodes: Node[] = newGraphNodes
          .filter((n) => !existingNodeIds.has(String(n.id)))
          .map((n) => ({
            id: String(n.id), // Ensure string type
            type: "objectNode",
            position: n.position,
            data: n.data,
          }));

        const addedEdges: Edge[] = newGraphEdges
          .filter((e) => !existingEdgeIds.has(String(e.id)))
          .map((e) => ({
            id: String(e.id), // Ensure string type
            source: String(e.source), // Ensure string type
            target: String(e.target), // Ensure string type
            label: e.label,
            animated: e.type === "semantic",
            style: e.type === "semantic" 
              ? { stroke: "#722ed1", strokeDasharray: "5,5" } 
              : undefined,
            data: e.data,
          }));

        console.log('[GraphCanvas] Expand - Added nodes:', addedNodes.length);
        console.log('[GraphCanvas] Expand - Added edges:', addedEdges.length);
        console.log('[GraphCanvas] Expand - Added node IDs:', addedNodes.map(n => n.id));
        console.log('[GraphCanvas] Expand - Added edge sources/targets:', 
          addedEdges.map(e => ({ source: e.source, target: e.target }))
        );

        if (addedNodes.length === 0 && addedEdges.length === 0) {
          message.info("没有新的关联节点");
        } else {
          // Apply layout to all nodes
          const allNodes = [...nodes, ...addedNodes];
          const allEdges = [...edges, ...addedEdges];
          
          // UNIT 2: Layout verification for expansion
          console.log('[GraphCanvas] Expand - Applying layout to all nodes:', allNodes.length);
          const { nodes: layoutedNodes, edges: layoutedEdges } =
            applyLayout(allNodes, allEdges, layout);

          console.log('[GraphCanvas] Expand - Layouted nodes:', layoutedNodes.length);
          console.log('[GraphCanvas] Expand - Layouted edges:', layoutedEdges.length);

          // Update raw data for debug UI
          setRawGraphData(result);

          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
          message.success(`发现 ${addedNodes.length} 个新节点`);
        }

        expandedNodes.current.add(nodeId);
      } catch (error) {
        console.error("Failed to expand node:", error);
        message.error("展开节点失败");
      } finally {
        setLoading(false);
      }

      setContextMenu(null);
    },
    [nodes, edges, showSemantic, layout]
  );

  // Context menu items
  const menuItems: MenuProps["items"] = contextMenu
    ? [
        {
          key: "expand",
          label: "展开关联",
          onClick: () => handleExpandNode(contextMenu.nodeId),
        },
        {
          key: "details",
          label: "查看详情",
          onClick: () => {
            message.info(`查看 ${contextMenu.nodeId} 详情`);
            setContextMenu(null);
          },
        },
        { type: "divider" },
        {
          key: "hide",
          label: "隐藏节点",
          onClick: () => {
            setNodes((nds) => nds.filter((n) => n.id !== contextMenu?.nodeId));
            setContextMenu(null);
          },
        },
      ]
    : [];

  // Close context menu on click outside
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  if (seedIds.length === 0) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          width: "100%",
          color: "#666",
          flexDirection: "column",
          gap: 16,
          background: "#141414",
        }}
      >
        <span style={{ fontSize: 48 }}>🔍</span>
        <span>选择一个对象开始探索图谱</span>
      </div>
    );
  }

  return (
    <div style={{ height: "100%", width: "100%", position: "relative", display: "flex", flexDirection: "column" }}>
      {loading && (
        <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", zIndex: 10 }}>
          <Spin tip="加载图数据..." />
        </div>
      )}
      <div style={{ flex: 1, width: "100%", position: "relative" }}>
        <ReactFlow
          nodes={filteredNodes}
          edges={filteredEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onNodeContextMenu={onNodeContextMenu}
          nodeTypes={nodeTypes}
          defaultEdgeOptions={defaultEdgeOptions}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
          style={{ background: "#141414" }}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1}
            color="#333"
          />
          <Controls
            style={{ background: "#1f1f1f", borderColor: "#333" }}
          />
          <MiniMap
            nodeColor={(node) => node.data?.color || "#666"}
            maskColor="rgba(0,0,0,0.7)"
            style={{ background: "#1f1f1f" }}
          />
        </ReactFlow>

        {/* Context Menu */}
        {contextMenu && (
          <div
            style={{
              position: "fixed",
              top: contextMenu.y,
              left: contextMenu.x,
              zIndex: 1000,
            }}
          >
            <Menu
              items={menuItems}
              style={{
                background: "#1f1f1f",
                border: "1px solid #333",
                borderRadius: 6,
              }}
            />
          </div>
        )}
      </div>

      {/* UNIT 4: Debug Panel - Raw Graph Data Visualization */}
      <div
        style={{
          borderTop: "1px solid #333",
          background: "#1f1f1f",
          maxHeight: showDebugPanel ? "300px" : "0",
          overflow: "hidden",
          transition: "max-height 0.3s ease",
        }}
      >
        <div
          style={{
            padding: "8px 16px",
            background: "#262626",
            borderBottom: "1px solid #333",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            cursor: "pointer",
          }}
          onClick={() => setShowDebugPanel(!showDebugPanel)}
        >
          <span style={{ color: "#fff", fontSize: "12px", fontWeight: "bold" }}>
            🔍 调试面板 - 原始图数据
          </span>
          <span style={{ color: "#888", fontSize: "12px" }}>
            {showDebugPanel ? "▼" : "▶"}
          </span>
        </div>
        {showDebugPanel && rawGraphData && (
          <div style={{ padding: "16px", overflow: "auto", maxHeight: "250px" }}>
            <pre
              style={{
                margin: 0,
                padding: "12px",
                background: "#141414",
                border: "1px solid #333",
                borderRadius: "4px",
                color: "#a0a0a0",
                fontSize: "11px",
                fontFamily: "monospace",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {JSON.stringify(rawGraphData, null, 2)}
            </pre>
            <div style={{ marginTop: "12px", fontSize: "11px", color: "#888" }}>
              <div>节点数量: {rawGraphData.nodes?.length || 0}</div>
              <div>边数量: {rawGraphData.edges?.length || 0}</div>
              <div style={{ marginTop: "8px" }}>
                <strong>节点ID列表:</strong>{" "}
                {rawGraphData.nodes?.map((n: any) => n.id).join(", ") || "无"}
              </div>
              <div style={{ marginTop: "4px" }}>
                <strong>边连接:</strong>{" "}
                {rawGraphData.edges?.map((e: any) => `${e.source}→${e.target}`).join(", ") || "无"}
              </div>
            </div>
          </div>
        )}
        {showDebugPanel && !rawGraphData && (
          <div style={{ padding: "16px", color: "#888", fontSize: "12px" }}>
            暂无图数据
          </div>
        )}
      </div>
    </div>
  );
};

// Wrap with ReactFlowProvider
const GraphCanvas: React.FC<GraphCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
};

export default GraphCanvas;
