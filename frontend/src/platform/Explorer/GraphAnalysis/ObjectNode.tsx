/**
 * ObjectNode - Custom React Flow Node Component
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Renders object instances as card-like nodes with:
 * - Icon and label
 * - Type indicator
 * - Status glow for seeds
 */

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "reactflow";

interface ObjectNodeData {
  label: string;
  object_type: string;
  icon: string;
  color: string;
  type_label: string;
  is_seed?: boolean;
}

const ObjectNode: React.FC<NodeProps<ObjectNodeData>> = ({ data, selected }) => {
  const { label, icon, color, type_label, is_seed } = data;

  return (
    <div
      style={{
        background: "#1f1f1f",
        border: `2px solid ${selected ? "#1890ff" : color}`,
        borderRadius: 8,
        padding: "8px 12px",
        minWidth: 120,
        boxShadow: is_seed
          ? `0 0 15px ${color}80`
          : selected
          ? "0 0 10px #1890ff80"
          : "0 2px 8px rgba(0,0,0,0.3)",
        transition: "all 0.2s ease",
      }}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: color,
          width: 8,
          height: 8,
          border: "2px solid #1f1f1f",
        }}
      />

      {/* Node Content */}
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 20 }}>{icon}</span>
        <div>
          <div
            style={{
              color: "#fff",
              fontWeight: 500,
              fontSize: 13,
              maxWidth: 120,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {label}
          </div>
          <div
            style={{
              color: color,
              fontSize: 10,
              marginTop: 2,
            }}
          >
            {type_label}
          </div>
        </div>
      </div>

      {/* Seed Badge */}
      {is_seed && (
        <div
          style={{
            position: "absolute",
            top: -6,
            right: -6,
            background: color,
            color: "#000",
            fontSize: 10,
            fontWeight: 600,
            padding: "2px 6px",
            borderRadius: 4,
          }}
        >
          种子
        </div>
      )}

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: color,
          width: 8,
          height: 8,
          border: "2px solid #1f1f1f",
        }}
      />
    </div>
  );
};

export default memo(ObjectNode);
