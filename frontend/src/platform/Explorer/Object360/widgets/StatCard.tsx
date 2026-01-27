/**
 * StatCard Widget - Display Statistics Summary
 * MDP Platform V3.1 - Object 360 View
 */

import React from "react";
import { Card, Row, Col, Statistic, Space } from "antd";
import {
  FundOutlined,
  NodeIndexOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  EyeOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import type { WidgetProps } from "../types";

// Icon mapping for metrics
const METRIC_ICONS: Record<string, React.ReactNode> = {
  total_relations: <LinkOutlined />,
  total_actions: <ClockCircleOutlined />,
  total_sightings: <EyeOutlined />,
  last_seen_days: <ClockCircleOutlined />,
  threat_score: <AlertOutlined />,
  node_count: <NodeIndexOutlined />,
  default: <FundOutlined />,
};

// Label mapping for metrics
const METRIC_LABELS: Record<string, string> = {
  total_relations: "关联数",
  total_actions: "活动数",
  total_sightings: "目击次数",
  last_seen_days: "最近发现",
  threat_score: "威胁分数",
  node_count: "节点数",
};

// Color mapping for metrics
const METRIC_COLORS: Record<string, string> = {
  total_relations: "#1890ff",
  total_actions: "#52c41a",
  threat_score: "#ff4d4f",
  default: "#666",
};

const StatCard: React.FC<WidgetProps> = ({ config, data }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  
  const title = viewConfig.title || "统计摘要";
  const layout = viewConfig.layout || "grid";
  const columns = viewConfig.columns || 3;
  const metrics = dataBinding.metrics as string[] || [];
  
  // Get stats from data (with null check)
  const stats = data?.stats || {};
  
  // Determine which metrics to show
  const displayMetrics = metrics.length > 0
    ? metrics
    : Object.keys(stats);
  
  // Calculate column span
  const colSpan = Math.floor(24 / Math.min(displayMetrics.length, columns));

  return (
    <Card
      size="small"
      title={
        <Space>
          <FundOutlined />
          <span>{title}</span>
        </Space>
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: { padding: "8px 12px" },
      }}
    >
      <Row gutter={[8, 8]}>
        {displayMetrics.map((metric) => (
          <Col key={metric} span={colSpan}>
            <Statistic
              title={METRIC_LABELS[metric] || metric.replace(/_/g, " ")}
              value={stats[metric] ?? "-"}
              prefix={METRIC_ICONS[metric] || METRIC_ICONS.default}
              valueStyle={{
                color: METRIC_COLORS[metric] || METRIC_COLORS.default,
                fontSize: 20,
              }}
            />
          </Col>
        ))}
        
        {displayMetrics.length === 0 && (
          <Col span={24}>
            <Statistic
              title="关联数"
              value={stats.total_relations ?? 0}
              prefix={<LinkOutlined />}
              valueStyle={{ color: "#1890ff", fontSize: 20 }}
            />
          </Col>
        )}
      </Row>
    </Card>
  );
};

export default StatCard;
