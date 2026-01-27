/**
 * MiniMap Widget - Display Geographic Location
 * MDP Platform V3.1 - Object 360 View
 * 
 * Note: This is a placeholder implementation.
 * In production, integrate with Leaflet or Mapbox.
 */

import React from "react";
import { Card, Space, Typography, Tag, Tooltip, Empty } from "antd";
import {
  EnvironmentOutlined,
  CompassOutlined,
  AimOutlined,
} from "@ant-design/icons";
import type { WidgetProps } from "../types";

const { Text } = Typography;

const MiniMap: React.FC<WidgetProps> = ({ config, data }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  
  const title = viewConfig.title || "当前位置";
  const zoom = viewConfig.zoom || 12;
  const showTrack = viewConfig.showTrack || false;
  
  // Get lat/lon from data using binding
  const latField = dataBinding.lat || "latitude";
  const lonField = dataBinding.lon || "longitude";
  const headingField = dataBinding.heading || "heading";
  
  // With null check
  const properties = data?.properties || {};
  const lat = properties[latField];
  const lon = properties[lonField];
  const heading = properties[headingField];
  
  const hasLocation = lat !== undefined && lon !== undefined;

  // Format coordinates
  const formatCoord = (value: number, type: "lat" | "lon") => {
    if (value === undefined || value === null) return "-";
    const dir = type === "lat" ? (value >= 0 ? "N" : "S") : (value >= 0 ? "E" : "W");
    return `${Math.abs(value).toFixed(4)}° ${dir}`;
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <EnvironmentOutlined />
          <span>{title}</span>
        </Space>
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: { padding: 0 },
      }}
    >
      {hasLocation ? (
        <>
          {/* Map Placeholder */}
          <div
            style={{
              height: viewConfig.height || 200,
              background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Grid lines for map effect */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                backgroundImage: `
                  linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
                `,
                backgroundSize: "20px 20px",
              }}
            />
            
            {/* Center marker */}
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: "50%",
                background: "rgba(24, 144, 255, 0.3)",
                border: "2px solid #1890ff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                animation: "pulse 2s infinite",
              }}
            >
              <AimOutlined style={{ fontSize: 20, color: "#1890ff" }} />
            </div>
            
            {/* Heading indicator */}
            {heading !== undefined && (
              <Tooltip title={`航向: ${heading}°`}>
                <div
                  style={{
                    position: "absolute",
                    top: 8,
                    right: 8,
                    background: "rgba(0,0,0,0.6)",
                    padding: "4px 8px",
                    borderRadius: 4,
                  }}
                >
                  <CompassOutlined
                    style={{
                      color: "#1890ff",
                      transform: `rotate(${heading}deg)`,
                      transition: "transform 0.3s",
                    }}
                  />
                  <Text style={{ color: "#fff", marginLeft: 4, fontSize: 12 }}>
                    {heading}°
                  </Text>
                </div>
              </Tooltip>
            )}
            
            {/* Zoom indicator */}
            <Tag
              style={{
                position: "absolute",
                bottom: 8,
                left: 8,
                background: "rgba(0,0,0,0.6)",
                border: "none",
                color: "#aaa",
              }}
            >
              Zoom: {zoom}
            </Tag>
          </div>
          
          {/* Coordinates */}
          <div
            style={{
              padding: "8px 12px",
              borderTop: "1px solid #303030",
              display: "flex",
              justifyContent: "space-between",
              fontSize: 12,
            }}
          >
            <Space>
              <Text type="secondary">纬度:</Text>
              <Text copyable={{ text: String(lat) }}>
                {formatCoord(lat, "lat")}
              </Text>
            </Space>
            <Space>
              <Text type="secondary">经度:</Text>
              <Text copyable={{ text: String(lon) }}>
                {formatCoord(lon, "lon")}
              </Text>
            </Space>
          </div>
        </>
      ) : (
        <div style={{ padding: 24 }}>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="无位置数据"
          />
        </div>
      )}
      
      {/* CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(24, 144, 255, 0.4); }
          70% { box-shadow: 0 0 0 20px rgba(24, 144, 255, 0); }
          100% { box-shadow: 0 0 0 0 rgba(24, 144, 255, 0); }
        }
      `}</style>
    </Card>
  );
};

export default MiniMap;
