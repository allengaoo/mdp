/**
 * Target Node - Represents a target ontology property
 */
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { AimOutlined } from '@ant-design/icons';

interface TargetNodeData {
  property: string;
  label?: string;
  dataType?: string;
}

const TargetNode: React.FC<NodeProps<TargetNodeData>> = ({ data, selected }) => {
  return (
    <div
      style={{
        padding: '10px 16px',
        borderRadius: 8,
        border: `2px solid ${selected ? '#52c41a' : '#95de64'}`,
        backgroundColor: '#f6ffed',
        minWidth: 140,
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#52c41a' }}
      />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <AimOutlined style={{ color: '#52c41a' }} />
        <div>
          <div style={{ fontWeight: 500, fontSize: 13 }}>{data.property}</div>
          {data.dataType && (
            <div style={{ fontSize: 11, color: '#8c8c8c' }}>{data.dataType}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TargetNode;
