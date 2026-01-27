/**
 * Custom ReactFlow Node for Object Types.
 * Displays object type definition with metadata styling.
 */
import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import {
  CodeSandboxOutlined,
  CalendarOutlined,
  FileTextOutlined,
  PictureOutlined,
  BarChartOutlined,
} from '@ant-design/icons';

// Node data interface
export interface ObjectNodeData {
  label: string;           // display_name or api_name
  apiName: string;         // api_name
  stereotype: string;      // ENTITY, EVENT, DOCUMENT, MEDIA, METRIC
  color?: string | null;   // Custom color
}

// Stereotype to icon mapping
const stereotypeIcons: Record<string, React.ReactNode> = {
  ENTITY: <CodeSandboxOutlined />,
  EVENT: <CalendarOutlined />,
  DOCUMENT: <FileTextOutlined />,
  MEDIA: <PictureOutlined />,
  METRIC: <BarChartOutlined />,
};

// Stereotype to default color mapping
const stereotypeColors: Record<string, string> = {
  ENTITY: '#1890ff',
  EVENT: '#52c41a',
  DOCUMENT: '#faad14',
  MEDIA: '#eb2f96',
  METRIC: '#722ed1',
};

/**
 * Custom node component for Object Type visualization.
 */
const ObjectNode: React.FC<NodeProps<ObjectNodeData>> = ({ data, selected }) => {
  const icon = stereotypeIcons[data.stereotype] || stereotypeIcons.ENTITY;
  const color = data.color || stereotypeColors[data.stereotype] || '#1890ff';

  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: 8,
        background: '#fff',
        border: `2px solid ${selected ? color : '#e8e8e8'}`,
        boxShadow: selected
          ? `0 4px 12px ${color}40`
          : '0 2px 8px rgba(0,0,0,0.08)',
        minWidth: 160,
        transition: 'all 0.2s ease',
      }}
    >
      {/* Input Handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: color,
          width: 8,
          height: 8,
          border: '2px solid #fff',
        }}
      />

      {/* Content */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {/* Icon */}
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 6,
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color,
            fontSize: 16,
          }}
        >
          {icon}
        </div>

        {/* Labels */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontWeight: 600,
              fontSize: 13,
              color: '#262626',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {data.label}
          </div>
          <div
            style={{
              fontSize: 11,
              color: '#8c8c8c',
              fontFamily: 'monospace',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {data.apiName}
          </div>
        </div>
      </div>

      {/* Stereotype Badge */}
      <div
        style={{
          position: 'absolute',
          top: -8,
          right: 8,
          background: color,
          color: '#fff',
          fontSize: 9,
          fontWeight: 600,
          padding: '2px 6px',
          borderRadius: 4,
          textTransform: 'uppercase',
          letterSpacing: 0.5,
        }}
      >
        {data.stereotype}
      </div>

      {/* Output Handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: color,
          width: 8,
          height: 8,
          border: '2px solid #fff',
        }}
      />
    </div>
  );
};

export default memo(ObjectNode);
