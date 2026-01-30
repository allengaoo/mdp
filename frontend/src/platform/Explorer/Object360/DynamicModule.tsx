/**
 * DynamicModule - Layout Container for Widgets
 * MDP Platform V3.1 - Object 360 View
 * 
 * This component handles the layout of a module section.
 * It renders all widgets within the module based on configuration.
 */

import React from "react";
import { Col, Typography, Collapse, Space, Badge } from "antd";
import {
  ProfileOutlined,
  CompassOutlined,
  BulbOutlined,
  AppstoreOutlined,
} from "@ant-design/icons";
import type { ModuleProps } from "./types";
import WidgetFactory from "./WidgetFactory";

const { Text } = Typography;

// Icon mapping for module names
const MODULE_ICONS: Record<string, React.ReactNode> = {
  Identity: <ProfileOutlined />,
  Context: <CompassOutlined />,
  Intelligence: <BulbOutlined />,
  default: <AppstoreOutlined />,
};

// Get icon for module
const getModuleIcon = (name: string | null): React.ReactNode => {
  if (!name) return MODULE_ICONS.default;
  return MODULE_ICONS[name] || MODULE_ICONS.default;
};

/**
 * DynamicModule Component
 * 
 * Renders a module section (column) with its widgets.
 * Layout is controlled by layout_config from the database.
 */
const DynamicModule: React.FC<ModuleProps> = ({
  config,
  data,
  objectId,
  objectType,
  onAction,
}) => {
  const layoutConfig = config.layout_config || {};
  const width = layoutConfig.width || 8; // Default to 1/3 of 24-column grid
  const collapsible = layoutConfig.collapsible || false;
  const scrollable = layoutConfig.scrollable || false;
  
  // Sort widgets by position_config.order
  const sortedWidgets = [...config.widgets].sort((a, b) => {
    const orderA = a.position_config?.order ?? 999;
    const orderB = b.position_config?.order ?? 999;
    return orderA - orderB;
  });

  // Render widgets
  const renderWidgets = () => (
    <div
      style={{
        height: scrollable ? "100%" : "auto",
        overflowY: scrollable ? "auto" : "visible",
      }}
    >
      {sortedWidgets.map((widgetConfig) => (
        <WidgetFactory
          key={widgetConfig.id}
          config={widgetConfig}
          data={data}
          objectId={objectId}
          objectType={objectType}
          onAction={onAction}
        />
      ))}
      
      {sortedWidgets.length === 0 && (
        <div
          style={{
            padding: 24,
            textAlign: "center",
            color: "#666",
          }}
        >
          <Text type="secondary">此模块暂无组件</Text>
        </div>
      )}
    </div>
  );

  // Module header
  const moduleHeader = (
    <Space>
      {getModuleIcon(config.name)}
      <Text strong>{config.name || "模块"}</Text>
      <Badge
        count={sortedWidgets.length}
        style={{ backgroundColor: "#1890ff" }}
        size="small"
      />
    </Space>
  );

  return (
    <Col
      span={width}
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {collapsible ? (
        <Collapse
          defaultActiveKey={["module"]}
          ghost
          style={{ flex: 1 }}
          items={[
            {
              key: "module",
              label: moduleHeader,
              children: renderWidgets(),
            },
          ]}
        />
      ) : (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Module Title */}
          <div
            style={{
              padding: "12px 16px",
              borderBottom: "1px solid #303030",
              background: "#1f1f1f",
            }}
          >
            {moduleHeader}
          </div>
          
          {/* Module Content */}
          <div
            style={{
              flex: 1,
              padding: 16,
              overflowY: scrollable ? "auto" : "visible",
            }}
          >
            {renderWidgets()}
          </div>
        </div>
      )}
    </Col>
  );
};

export default DynamicModule;
