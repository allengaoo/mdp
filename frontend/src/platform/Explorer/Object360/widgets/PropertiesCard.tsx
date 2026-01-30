/**
 * PropertiesCard Widget - Display Object Properties
 * MDP Platform V3.1 - Object 360 View
 */

import React from "react";
import { Card, Descriptions, Tag, Tooltip, Typography, Space } from "antd";
import {
  InfoCircleOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import type { WidgetProps } from "../types";
import {
  formatPropertyValue,
  getPropertyLabel,
  getThreatLevelColor,
  getStatusColor,
} from "../../../../api/v3/object360";

const { Text } = Typography;

const PropertiesCard: React.FC<WidgetProps> = ({ config, data }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  const fields = dataBinding.fields as string[] || [];
  
  const title = viewConfig.title || "基本信息";
  const layout = viewConfig.layout || "vertical";
  const labelWidth = viewConfig.labelWidth || 100;
  
  // Get properties to display (with null check)
  const properties = data?.properties || {};
  
  // Filter fields if specified, otherwise show all
  const displayFields = fields.length > 0
    ? fields.filter((f) => f in properties)
    : Object.keys(properties);

  // Render value with special formatting
  const renderValue = (key: string, value: any) => {
    // Handle special fields
    if (key === "threat_level") {
      return (
        <Tag color={getThreatLevelColor(value)}>
          {formatPropertyValue(value)}
        </Tag>
      );
    }

    if (key === "status") {
      return (
        <Tag color={getStatusColor(value)}>
          {formatPropertyValue(value)}
        </Tag>
      );
    }

    if (key === "country") {
      return (
        <Space>
          <span>{formatPropertyValue(value)}</span>
        </Space>
      );
    }

    // Handle copyable fields (ID, MMSI, IMO)
    if (["id", "mmsi", "imo"].includes(key)) {
      return (
        <Text copyable={{ icon: <CopyOutlined style={{ fontSize: 12 }} /> }}>
          {formatPropertyValue(value)}
        </Text>
      );
    }

    // Default formatting
    return <Text>{formatPropertyValue(value)}</Text>;
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <InfoCircleOutlined />
          <span>{title}</span>
        </Space>
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: { padding: "12px 16px" },
      }}
    >
      <Descriptions
        column={1}
        size="small"
        layout={layout as "horizontal" | "vertical"}
        labelStyle={{
          width: labelWidth,
          color: "#666",
          fontSize: 12,
        }}
        contentStyle={{
          fontSize: 13,
        }}
      >
        {displayFields.map((field) => (
          <Descriptions.Item
            key={field}
            label={
              <Tooltip title={field}>
                {getPropertyLabel(field)}
              </Tooltip>
            }
          >
            {renderValue(field, properties[field])}
          </Descriptions.Item>
        ))}
      </Descriptions>
      
      {displayFields.length === 0 && (
        <Text type="secondary" style={{ fontSize: 12 }}>
          暂无属性数据
        </Text>
      )}
    </Card>
  );
};

export default PropertiesCard;
