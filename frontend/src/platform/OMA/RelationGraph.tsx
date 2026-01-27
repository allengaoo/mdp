/**
 * Relation Graph Page - MDP Platform V3.1
 * 
 * Visualizes ontology topology using ReactFlow.
 * Shows object types as nodes and link types as edges.
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Typography, Spin, Alert, Button, Space, Card } from 'antd';
import { ReloadOutlined, FullscreenOutlined } from '@ant-design/icons';
import { fetchOntologyTopology, ITopologyData, ITopologyNode, ITopologyEdge } from '../../api/v3/topology';
import { getLayoutedElements } from '../../utils/dagreLayout';
import ObjectNode, { ObjectNodeData } from './ObjectNode';

const { Title, Text } = Typography;

// Register custom node types
const nodeTypes = {
  objectNode: ObjectNode,
};

// Cardinality to marker style mapping
const cardinalityMarkers: Record<string, { start?: boolean; end?: boolean }> = {
  'ONE_TO_ONE': { end: true },
  'ONE_TO_MANY': { end: true },
  'MANY_TO_ONE': { start: true },
  'MANY_TO_MANY': { start: true, end: true },
};

/**
 * Transform API data to ReactFlow format.
 */
function transformToReactFlow(data: ITopologyData): { nodes: Node<ObjectNodeData>[]; edges: Edge[] } {
  // Transform nodes
  const nodes: Node<ObjectNodeData>[] = data.nodes.map((node: ITopologyNode) => ({
    id: node.id,
    type: 'objectNode',
    position: { x: 0, y: 0 }, // Will be set by dagre
    data: {
      label: node.display_name || node.api_name,
      apiName: node.api_name,
      stereotype: node.stereotype,
      color: node.color,
    },
  }));

  // Transform edges
  const edges: Edge[] = data.edges.map((edge: ITopologyEdge) => {
    const markers = cardinalityMarkers[edge.cardinality || 'ONE_TO_MANY'] || { end: true };
    
    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.display_name || edge.api_name,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#8c8c8c', strokeWidth: 1.5 },
      labelStyle: { fontSize: 11, fill: '#595959' },
      labelBgStyle: { fill: '#fff', fillOpacity: 0.9 },
      labelBgPadding: [4, 6] as [number, number],
      labelBgBorderRadius: 4,
      markerEnd: markers.end ? {
        type: MarkerType.ArrowClosed,
        color: '#8c8c8c',
        width: 16,
        height: 16,
      } : undefined,
      markerStart: markers.start ? {
        type: MarkerType.ArrowClosed,
        color: '#8c8c8c',
        width: 16,
        height: 16,
      } : undefined,
    };
  });

  return { nodes, edges };
}

/**
 * Relation Graph Page Component.
 */
const RelationGraph: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rawData, setRawData] = useState<ITopologyData | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Load data from API
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchOntologyTopology();
      setRawData(data);

      // Transform and layout
      const { nodes: rawNodes, edges: rawEdges } = transformToReactFlow(data);
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        rawNodes,
        rawEdges,
        {
          direction: 'TB',
          nodeWidth: 200,
          nodeHeight: 80,
          nodeSep: 80,
          rankSep: 120,
        }
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '加载拓扑数据失败';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Stats summary
  const stats = useMemo(() => {
    if (!rawData) return null;
    return {
      nodeCount: rawData.nodes.length,
      edgeCount: rawData.edges.length,
    };
  }, [rawData]);

  // Loading state
  if (loading && nodes.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#8c8c8c' }}>加载关系图谱...</div>
      </div>
    );
  }

  // Error state
  if (error && nodes.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ margin: 0 }}>
            关系图谱 (Relation Graph)
          </Title>
        </div>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadData}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  // Empty state
  if (!loading && nodes.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ margin: 0 }}>
            关系图谱 (Relation Graph)
          </Title>
        </div>
        <Card>
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#8c8c8c' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔗</div>
            <div>暂无对象类型或链接类型数据</div>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={loadData}
              style={{ marginTop: 16 }}
            >
              刷新
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <div>
          <Title level={4} style={{ margin: 0 }}>
            关系图谱 (Relation Graph)
          </Title>
          <Text type="secondary">
            可视化展示对象类型及其关联关系
          </Text>
        </div>
        <Space>
          {stats && (
            <Text type="secondary">
              {stats.nodeCount} 个对象类型 · {stats.edgeCount} 个链接关系
            </Text>
          )}
          <Button
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* Graph Container */}
      <div
        style={{
          flex: 1,
          minHeight: 500,
          background: '#fafafa',
          borderRadius: 8,
          border: '1px solid #e8e8e8',
          overflow: 'hidden',
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
          defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        >
          <Background color="#e8e8e8" gap={20} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const data = node.data as ObjectNodeData;
              return data.color || '#1890ff';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
            style={{ background: '#fff' }}
          />
        </ReactFlow>
      </div>

      {/* Legend */}
      <div
        style={{
          marginTop: 12,
          padding: '8px 16px',
          background: '#fff',
          borderRadius: 6,
          border: '1px solid #e8e8e8',
          display: 'flex',
          gap: 24,
          fontSize: 12,
          color: '#8c8c8c',
        }}
      >
        <span>图例:</span>
        <span>
          <span style={{ display: 'inline-block', width: 12, height: 12, background: '#1890ff', borderRadius: 3, marginRight: 4, verticalAlign: 'middle' }} />
          ENTITY
        </span>
        <span>
          <span style={{ display: 'inline-block', width: 12, height: 12, background: '#52c41a', borderRadius: 3, marginRight: 4, verticalAlign: 'middle' }} />
          EVENT
        </span>
        <span>
          <span style={{ display: 'inline-block', width: 12, height: 12, background: '#faad14', borderRadius: 3, marginRight: 4, verticalAlign: 'middle' }} />
          DOCUMENT
        </span>
        <span>
          <span style={{ display: 'inline-block', width: 12, height: 12, background: '#eb2f96', borderRadius: 3, marginRight: 4, verticalAlign: 'middle' }} />
          MEDIA
        </span>
        <span>
          <span style={{ display: 'inline-block', width: 12, height: 12, background: '#722ed1', borderRadius: 3, marginRight: 4, verticalAlign: 'middle' }} />
          METRIC
        </span>
      </div>
    </div>
  );
};

export default RelationGraph;
