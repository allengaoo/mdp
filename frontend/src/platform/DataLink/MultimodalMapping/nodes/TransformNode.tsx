/**
 * Transform Node - Represents a transformation function
 */
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { ThunderboltOutlined } from '@ant-design/icons';

interface TransformNodeData {
  function: string;
  label?: string;
}

const TransformNode: React.FC<NodeProps<TransformNodeData>> = ({ data, selected }) => {
  const isVectorTransform = data.function?.includes('embedding');
  
  return (
    <div
      style={{
        padding: '10px 16px',
        borderRadius: 8,
        border: `2px solid ${selected ? '#722ed1' : '#b37feb'}`,
        backgroundColor: '#f9f0ff',
        minWidth: 160,
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#722ed1' }}
      />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <ThunderboltOutlined style={{ color: '#722ed1' }} />
        <div>
          <div style={{ fontWeight: 500, fontSize: 13 }}>
            {data.label || data.function}
          </div>
          {isVectorTransform && (
            <div style={{ fontSize: 11, color: '#722ed1' }}>→ Vector [768]</div>
          )}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#722ed1' }}
      />
    </div>
  );
};

export default TransformNode;
