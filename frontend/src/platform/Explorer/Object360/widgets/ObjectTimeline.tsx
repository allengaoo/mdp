/**
 * ObjectTimeline Widget - Display Activity Timeline
 * MDP Platform V3.1 - Object 360 View
 */

import React from "react";
import { Card, Timeline, Space, Typography, Tag, Empty, Tooltip } from "antd";
import {
  HistoryOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  PlayCircleOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import type { WidgetProps, TimelineEvent } from "../types";

const { Text, Paragraph } = Typography;

// Icon mapping
const ICON_MAP: Record<string, React.ReactNode> = {
  "check-circle": <CheckCircleOutlined />,
  "close-circle": <CloseCircleOutlined />,
  "clock-circle": <ClockCircleOutlined />,
  "exclamation-circle": <ExclamationCircleOutlined />,
  "play-circle": <PlayCircleOutlined />,
  "info-circle": <InfoCircleOutlined />,
};

const ObjectTimeline: React.FC<WidgetProps> = ({ config, data }) => {
  const viewConfig = config.view_config || {};
  
  const title = viewConfig.title || "活动时间线";
  const mode = viewConfig.mode || "left";
  const showIcon = viewConfig.showIcon !== false;
  
  // With null check
  const events = data?.timeline_events || [];

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "刚刚";
    if (diffMins < 60) return `${diffMins} 分钟前`;
    if (diffHours < 24) return `${diffHours} 小时前`;
    if (diffDays < 7) return `${diffDays} 天前`;
    
    return date.toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Get icon for event
  const getIcon = (event: TimelineEvent) => {
    if (!showIcon) return undefined;
    
    const iconKey = event.icon || "info-circle";
    return ICON_MAP[iconKey] || <InfoCircleOutlined />;
  };

  // Get color for event
  const getColor = (event: TimelineEvent) => {
    if (event.color) return event.color;
    
    const status = event.metadata?.status;
    if (status === "SUCCESS") return "#52c41a";
    if (status === "FAILED") return "#ff4d4f";
    return "#1890ff";
  };

  // Render event label
  const renderLabel = (event: TimelineEvent) => (
    <Text type="secondary" style={{ fontSize: 11 }}>
      {formatTime(event.timestamp)}
    </Text>
  );

  // Render event content
  const renderContent = (event: TimelineEvent) => (
    <div style={{ paddingBottom: 8 }}>
      <Space direction="vertical" size={2} style={{ width: "100%" }}>
        <Space>
          <Text strong style={{ fontSize: 13 }}>
            {event.title}
          </Text>
          {event.event_type && (
            <Tag
              style={{
                fontSize: 10,
                padding: "0 4px",
                lineHeight: "16px",
              }}
            >
              {event.event_type}
            </Tag>
          )}
        </Space>
        
        {event.description && (
          <Paragraph
            type="secondary"
            style={{ fontSize: 12, marginBottom: 0 }}
            ellipsis={{ rows: 2, expandable: true }}
          >
            {event.description}
          </Paragraph>
        )}
        
        {event.metadata?.input_params && (
          <Tooltip title={JSON.stringify(event.metadata.input_params, null, 2)}>
            <Text
              type="secondary"
              style={{ fontSize: 11, cursor: "pointer" }}
            >
              查看参数...
            </Text>
          </Tooltip>
        )}
      </Space>
    </div>
  );

  return (
    <Card
      size="small"
      title={
        <Space>
          <HistoryOutlined />
          <span>{title}</span>
          {events.length > 0 && (
            <Tag style={{ marginLeft: 8 }}>{events.length}</Tag>
          )}
        </Space>
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: {
          padding: "12px 16px",
          maxHeight: viewConfig.height || 400,
          overflow: "auto",
        },
      }}
    >
      {events.length > 0 ? (
        <Timeline
          mode={mode as "left" | "right" | "alternate"}
          items={events.map((event) => ({
            key: event.id,
            dot: getIcon(event),
            color: getColor(event),
            label: mode === "alternate" ? renderLabel(event) : undefined,
            children: (
              <div>
                {mode !== "alternate" && (
                  <div style={{ marginBottom: 4 }}>
                    {renderLabel(event)}
                  </div>
                )}
                {renderContent(event)}
              </div>
            ),
          }))}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无活动记录"
        />
      )}
    </Card>
  );
};

export default ObjectTimeline;
