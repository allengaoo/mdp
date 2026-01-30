/**
 * Source Node - Represents a source column from raw table
 */
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { DatabaseOutlined } from '@ant-design/icons';

interface SourceNodeData {
  column: string;
  label?: string;
  dataType?: string;
}

const SourceNode: React.FC<NodeProps<SourceNodeData>> = ({ data, selected }) => {
  return (
    <div
      style={{
        padding: '10px 16px',
        borderRadius: 8,
        border: `2px solid ${selected ? '#1890ff' : '#69b1ff'}`,
        backgroundColor: '#e6f4ff',
        minWidth: 140,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <DatabaseOutlined style={{ color: '#1890ff' }} />
        <div>
          <div style={{ fontWeight: 500, fontSize: 13 }}>{data.column}</div>
          {data.dataType && (
            <div style={{ fontSize: 11, color: '#8c8c8c' }}>{data.dataType}</div>
          )}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#1890ff' }}
      />
    </div>
  );
};

export default SourceNode;
