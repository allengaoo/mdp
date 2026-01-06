/**
 * Topology View component using ReactFlow.
 * Displays ontology graph with custom nodes and edges.
 * Fetches data from backend APIs and applies automatic layout using Dagre.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  NodeTypes,
  MarkerType,
  NodeChange,
  EdgeChange,
  applyNodeChanges,
  applyEdgeChanges,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, Typography, Spin, message } from 'antd';
import { fetchObjectTypes, fetchLinkTypes, IObjectType, ILinkType } from '../../api/ontology';
import { getLayoutedElements } from '../../utils/dagreLayout';

const { Text } = Typography;

// Custom Node Component
interface CustomNodeData {
  label: string;
  icon?: string;
  propertyCount: number;
  status?: 'active' | 'inactive';
}

const CustomNode: React.FC<{ data: CustomNodeData }> = ({ data }) => {
  return (
    <Card
      style={{
        width: 180,
        padding: 0,
        borderRadius: 8,
        border: '1px solid #e8e8e8',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        position: 'relative',
      }}
      styles={{ body: { padding: '12px' } }}
    >
      {/* Target Handle (Input) - Top */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ opacity: 0 }}
      />
      
      {/* Source Handle (Output) - Bottom */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ opacity: 0 }}
      />
      
      {data.status === 'active' && (
        <div
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: '#52c41a',
            border: '1px solid #fff',
          }}
        />
      )}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        {data.icon && <span style={{ marginRight: 8, fontSize: 16 }}>{data.icon}</span>}
        <Text strong style={{ fontSize: 14, margin: 0 }}>
          {data.label}
        </Text>
      </div>
      <Text type="secondary" style={{ fontSize: 12 }}>
        {data.propertyCount} Properties
      </Text>
    </Card>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

// Helper function to count properties in property_schema
const countProperties = (propertySchema?: Record<string, any>): number => {
  if (!propertySchema) return 0;
  if (Array.isArray(propertySchema)) {
    return propertySchema.length;
  }
  return Object.keys(propertySchema).length;
};

const TopologyView: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [nodes, setNodes] = useState<Node<CustomNodeData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch data from backend and transform to ReactFlow format
  useEffect(() => {
    const loadTopologyData = async () => {
      if (!projectId) {
        message.warning('Project ID is missing');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);

        // Fetch object types and link types in parallel
        const [objectTypes, linkTypes] = await Promise.all([
          fetchObjectTypes(projectId),
          fetchLinkTypes(),
        ]);

        // Create a map of object IDs for quick lookup
        const objectIdMap = new Set(objectTypes.map((obj) => obj.id));

        console.log('=== Topology Data Transformation Debug ===');
        console.log('ObjectTypes count:', objectTypes.length);
        console.log('LinkTypes count:', linkTypes.length);
        console.log('Object ID Map:', Array.from(objectIdMap));

        // Transform ObjectTypes to ReactFlow Nodes
        const transformedNodes: Node<CustomNodeData>[] = objectTypes.map((obj: IObjectType) => {
          const nodeId = obj.id; // Use UUID as node ID
          console.log(`Node ID created: ${nodeId} (from obj.id), Display: ${obj.display_name}, API: ${obj.api_name}`);
          return {
            id: nodeId,
            type: 'custom',
            position: { x: 0, y: 0 }, // Will be calculated by Dagre
            data: {
              label: obj.display_name || obj.api_name,
              icon: '📦', // Default icon, can be customized later
              propertyCount: countProperties(obj.property_schema),
              status: 'active' as const,
            },
          };
        });

        // Transform LinkTypes to ReactFlow Edges
        // Only include links where both source and target exist in the current project
        const transformedEdges: Edge[] = linkTypes
          .filter((link: ILinkType) => {
            const sourceExists = objectIdMap.has(link.source_type_id);
            const targetExists = objectIdMap.has(link.target_type_id);
            console.log(`Link ${link.display_name || link.api_name}:`);
            console.log(`  - Source ID: ${link.source_type_id}, Exists: ${sourceExists}`);
            console.log(`  - Target ID: ${link.target_type_id}, Exists: ${targetExists}`);
            console.log(`  - Edge Source expecting: ${link.source_type_id}`);
            console.log(`  - Edge Target expecting: ${link.target_type_id}`);
            return sourceExists && targetExists;
          })
          .map((link: ILinkType) => {
            const edge = {
              id: `edge-${link.id}`,
              source: link.source_type_id, // Use UUID from source_type_id
              target: link.target_type_id, // Use UUID from target_type_id
              label: link.display_name || link.api_name,
              type: 'smoothstep',
              animated: false,
              style: { 
                stroke: '#1890ff', 
                strokeWidth: 2,
                strokeDasharray: '5,5' 
              },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#1890ff',
                width: 20,
                height: 20,
              },
            };
            console.log(`Edge created: ${edge.id}`);
            console.log(`  - Source: ${edge.source} (expecting node with this ID)`);
            console.log(`  - Target: ${edge.target} (expecting node with this ID)`);
            console.log(`  - Label: ${edge.label}`);
            return edge;
          });

        console.log('Transformed Nodes count:', transformedNodes.length);
        console.log('Transformed Edges count:', transformedEdges.length);
        console.log('=== End Debug ===');

        // Apply Dagre layout
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          transformedNodes,
          transformedEdges,
          {
            direction: 'TB', // Top to Bottom
            nodeWidth: 180,
            nodeHeight: 50,
          }
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      } catch (error: any) {
        message.error(error.response?.data?.detail || 'Failed to load topology data');
        console.error('Error loading topology:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTopologyData();
  }, [projectId]);

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  }, []);

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  }, []);

  if (loading) {
    return (
      <div
        style={{
          width: '100%',
          height: 'calc(100vh - 112px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#fff',
          borderRadius: 8,
        }}
      >
        <Spin size="large" tip="Loading topology..." />
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div
        style={{
          width: '100%',
          height: 'calc(100vh - 112px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: '#fff',
          borderRadius: 8,
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <Text type="secondary" style={{ fontSize: 16 }}>
          No object types found in this project
        </Text>
        <Text type="secondary" style={{ fontSize: 14 }}>
          Create object types to visualize the topology graph
        </Text>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 'calc(100vh - 112px)', background: '#fff', borderRadius: 8 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        style={{ background: '#fafafa' }}
      >
        <Background color="#e8e8e8" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'custom') {
              return '#1890ff';
            }
            return '#8c8c8c';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
};

export default TopologyView;

