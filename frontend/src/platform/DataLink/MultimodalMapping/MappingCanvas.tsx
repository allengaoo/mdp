/**
 * MappingCanvas - React Flow canvas for visual mapping
 */
import React, { useCallback, useRef } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ReactFlowProvider,
  ReactFlowInstance,
} from 'reactflow';
import { message } from 'antd';
import 'reactflow/dist/style.css';

import { nodeTypes } from './nodes';

interface MappingCanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: (nodes: Node[]) => void;
  onEdgesChange: (edges: Edge[]) => void;
  onAddTransform?: (position: { x: number; y: number }) => void;
}

const MappingCanvas: React.FC<MappingCanvasProps> = ({
  nodes: initialNodes,
  edges: initialEdges,
  onNodesChange,
  onEdgesChange,
  onAddTransform,
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = React.useState<ReactFlowInstance | null>(null);

  // Sync state changes to parent
  React.useEffect(() => {
    onNodesChange(nodes);
  }, [nodes]);

  React.useEffect(() => {
    onEdgesChange(edges);
  }, [edges]);

  // Update internal state when props change
  React.useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes]);

  React.useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      // Validate connection
      const sourceNode = nodes.find(n => n.id === params.source);
      const targetNode = nodes.find(n => n.id === params.target);

      if (!sourceNode || !targetNode) return;

      // Prevent invalid connections
      if (sourceNode.type === 'target') {
        message.warning('目标节点不能作为连接源');
        return;
      }
      if (targetNode.type === 'source') {
        message.warning('源节点不能作为连接目标');
        return;
      }

      setEdges((eds) => addEdge({
        ...params,
        id: `edge-${params.source}-${params.target}`,
        animated: sourceNode.type === 'transform',
        style: { stroke: sourceNode.type === 'transform' ? '#722ed1' : '#1890ff' },
      }, eds));
    },
    [nodes, setEdges]
  );

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current || !reactFlowInstance) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const data = event.dataTransfer.getData('application/json');

      if (!data) return;

      const { type, ...nodeData } = JSON.parse(data);
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: nodeData,
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onContextMenu = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      
      if (!reactFlowInstance || !reactFlowWrapper.current) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      onAddTransform?.(position);
    },
    [reactFlowInstance, onAddTransform]
  );

  return (
    <div 
      ref={reactFlowWrapper} 
      style={{ width: '100%', height: '100%' }}
      onContextMenu={onContextMenu}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeInternal}
        onEdgesChange={onEdgesChangeInternal}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        snapToGrid
        snapGrid={[15, 15]}
      >
        <Controls />
        <Background color="#aaa" gap={16} />
      </ReactFlow>
    </div>
  );
};

// Wrap with provider for proper context
const MappingCanvasWithProvider: React.FC<MappingCanvasProps> = (props) => (
  <ReactFlowProvider>
    <MappingCanvas {...props} />
  </ReactFlowProvider>
);

export default MappingCanvasWithProvider;
