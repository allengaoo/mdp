/**
 * RelationList Widget - Display Object Relations
 * MDP Platform V3.1 - Object 360 View
 */

import React, { useState } from "react";
import {
  Card,
  Collapse,
  List,
  Space,
  Typography,
  Tag,
  Button,
  Empty,
  Tooltip,
  Badge,
} from "antd";
import {
  ApartmentOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
  LinkOutlined,
  EyeOutlined,
  ExpandOutlined,
} from "@ant-design/icons";
import type { WidgetProps, Relation } from "../types";

const { Text } = Typography;

// Link type labels
const LINK_TYPE_LABELS: Record<string, string> = {
  has_mission: "执行任务",
  corroborated_by: "被佐证",
  detected_by: "被探测",
  docked_at: "停靠港口",
  belongs_to: "隶属于",
  has_recon_image: "侦察影像",
  unknown: "未知关系",
};

// Link type colors
const LINK_TYPE_COLORS: Record<string, string> = {
  has_mission: "blue",
  corroborated_by: "green",
  detected_by: "orange",
  docked_at: "purple",
  belongs_to: "cyan",
  has_recon_image: "magenta",
};

const RelationList: React.FC<WidgetProps> = ({ config, data, onAction }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  
  const title = viewConfig.title || "关联关系";
  const showType = viewConfig.showType !== false;
  const expandable = viewConfig.expandable !== false;
  const linkTypes = dataBinding.link_types as string[] || [];
  
  // With null check
  const relations = data?.relations || {};
  
  // Filter by link types if specified
  const displayRelations = linkTypes.length > 0
    ? Object.fromEntries(
        Object.entries(relations).filter(([type]) => linkTypes.includes(type))
      )
    : relations;
  
  const totalCount = Object.values(displayRelations).reduce(
    (sum, rels) => sum + rels.length,
    0
  );

  // Handle view relation
  const handleViewRelation = (relation: Relation) => {
    onAction?.("view_object", {
      objectId: relation.target_id,
      objectType: relation.target_type,
    });
  };

  // Handle expand in graph
  const handleExpandInGraph = (relation: Relation) => {
    onAction?.("expand_graph", {
      objectId: relation.target_id,
    });
  };

  // Render relation item
  const renderRelationItem = (relation: Relation) => (
    <List.Item
      key={relation.id}
      style={{ padding: "8px 0" }}
      actions={[
        <Tooltip title="查看详情" key="view">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewRelation(relation)}
          />
        </Tooltip>,
        <Tooltip title="在图谱中展开" key="expand">
          <Button
            type="text"
            size="small"
            icon={<ExpandOutlined />}
            onClick={() => handleExpandInGraph(relation)}
          />
        </Tooltip>,
      ]}
    >
      <List.Item.Meta
        avatar={
          relation.direction === "outgoing" ? (
            <ArrowRightOutlined style={{ color: "#1890ff" }} />
          ) : (
            <ArrowLeftOutlined style={{ color: "#52c41a" }} />
          )
        }
        title={
          <Space size={4}>
            <Text ellipsis style={{ maxWidth: 150 }}>
              {relation.target_label}
            </Text>
            {showType && (
              <Tag
                style={{ fontSize: 10, padding: "0 4px" }}
                color={LINK_TYPE_COLORS[relation.link_type]}
              >
                {relation.target_type}
              </Tag>
            )}
          </Space>
        }
        description={
          <Text type="secondary" style={{ fontSize: 11 }}>
            {relation.direction === "outgoing" ? "指向" : "来自"}
          </Text>
        }
      />
    </List.Item>
  );

  // Render relation group
  const renderRelationGroup = (linkType: string, rels: Relation[]) => {
    const label = LINK_TYPE_LABELS[linkType] || linkType;
    const color = LINK_TYPE_COLORS[linkType] || "default";

    return {
      key: linkType,
      label: (
        <Space>
          <LinkOutlined />
          <span>{label}</span>
          <Badge count={rels.length} style={{ backgroundColor: "#1890ff" }} />
        </Space>
      ),
      children: (
        <List
          size="small"
          dataSource={rels}
          renderItem={renderRelationItem}
          style={{ marginTop: -8 }}
        />
      ),
    };
  };

  const collapseItems = Object.entries(displayRelations).map(([type, rels]) =>
    renderRelationGroup(type, rels)
  );

  return (
    <Card
      size="small"
      title={
        <Space>
          <ApartmentOutlined />
          <span>{title}</span>
          {totalCount > 0 && (
            <Tag style={{ marginLeft: 8 }}>{totalCount}</Tag>
          )}
        </Space>
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: {
          padding: collapseItems.length > 0 ? 0 : 16,
          maxHeight: viewConfig.height || "auto",
          overflow: "auto",
        },
      }}
    >
      {collapseItems.length > 0 ? (
        <Collapse
          ghost
          defaultActiveKey={expandable ? [collapseItems[0]?.key] : []}
          items={collapseItems}
          style={{ background: "transparent" }}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无关联数据"
        />
      )}
    </Card>
  );
};

export default RelationList;
