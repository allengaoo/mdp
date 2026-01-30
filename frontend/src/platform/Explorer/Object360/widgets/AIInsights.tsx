/**
 * AIInsights Widget - Display Vector Similarity Analysis
 * MDP Platform V3.1 - Object 360 View
 * 
 * This is the "Full-Modal" differentiator widget that shows
 * similar objects found via Milvus vector search.
 */

import React, { useState } from "react";
import {
  Card,
  List,
  Space,
  Typography,
  Tag,
  Button,
  Progress,
  Empty,
  Modal,
  Descriptions,
  Row,
  Col,
  Tooltip,
  Avatar,
} from "antd";
import {
  RobotOutlined,
  EyeOutlined,
  SwapOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import type { WidgetProps, SimilarObject } from "../types";

const { Text, Title } = Typography;

// Similarity level colors
const getSimilarityColor = (score: number): string => {
  if (score >= 0.95) return "#ff4d4f"; // Critical match
  if (score >= 0.85) return "#fa8c16"; // High match
  if (score >= 0.70) return "#faad14"; // Medium match
  return "#52c41a"; // Low match
};

// Similarity level label
const getSimilarityLabel = (score: number): string => {
  if (score >= 0.95) return "极高相似";
  if (score >= 0.85) return "高度相似";
  if (score >= 0.70) return "中度相似";
  return "低度相似";
};

const AIInsights: React.FC<WidgetProps> = ({ config, data, objectId, objectType, onAction }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  
  const title = viewConfig.title || "AI 智能分析";
  const showScore = viewConfig.showScore !== false;
  const allowCompare = viewConfig.allowCompare !== false;
  
  // With null check
  const similarObjects = data?.similar_objects || [];
  
  const [compareModalVisible, setCompareModalVisible] = useState(false);
  const [selectedObject, setSelectedObject] = useState<SimilarObject | null>(null);

  // Handle view object
  const handleViewObject = (obj: SimilarObject) => {
    onAction?.("view_object", {
      objectId: obj.id,
      objectType: obj.object_type,
    });
  };

  // Handle compare
  const handleCompare = (obj: SimilarObject) => {
    setSelectedObject(obj);
    setCompareModalVisible(true);
  };

  // Render similarity badge
  const renderSimilarityBadge = (score: number) => {
    const percentage = Math.round(score * 100);
    const color = getSimilarityColor(score);
    
    return (
      <Tooltip title={`相似度: ${percentage}%`}>
        <div style={{ width: 48 }}>
          <Progress
            type="circle"
            percent={percentage}
            size={40}
            strokeColor={color}
            format={(percent) => (
              <Text style={{ fontSize: 10, color }}>{percent}%</Text>
            )}
          />
        </div>
      </Tooltip>
    );
  };

  // Render object avatar
  const renderAvatar = (obj: SimilarObject) => {
    const color = getSimilarityColor(obj.similarity_score);
    return (
      <Avatar
        style={{ backgroundColor: color }}
        icon={<ThunderboltOutlined />}
      />
    );
  };

  // Render list item
  const renderItem = (obj: SimilarObject) => (
    <List.Item
      key={obj.id}
      style={{ padding: "12px 0" }}
      actions={[
        <Tooltip title="查看详情" key="view">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewObject(obj)}
          />
        </Tooltip>,
        allowCompare && (
          <Tooltip title="对比分析" key="compare">
            <Button
              type="text"
              size="small"
              icon={<SwapOutlined />}
              onClick={() => handleCompare(obj)}
            />
          </Tooltip>
        ),
      ].filter(Boolean)}
    >
      <List.Item.Meta
        avatar={showScore ? renderSimilarityBadge(obj.similarity_score) : renderAvatar(obj)}
        title={
          <Space>
            <Text ellipsis style={{ maxWidth: 120 }}>
              {obj.label}
            </Text>
            <Tag
              color={getSimilarityColor(obj.similarity_score)}
              style={{ fontSize: 10, padding: "0 4px" }}
            >
              {getSimilarityLabel(obj.similarity_score)}
            </Tag>
          </Space>
        }
        description={
          <Space direction="vertical" size={0}>
            <Text type="secondary" style={{ fontSize: 11 }}>
              类型: {obj.object_type}
            </Text>
            <Text type="secondary" style={{ fontSize: 11 }}>
              ID: {obj.id.slice(0, 12)}...
            </Text>
          </Space>
        }
      />
    </List.Item>
  );

  return (
    <>
      <Card
        size="small"
        title={
          <Space>
            <RobotOutlined />
            <span>{title}</span>
            {similarObjects.length > 0 && (
              <Tag color="blue">{similarObjects.length} 个匹配</Tag>
            )}
          </Space>
        }
        extra={
          similarObjects.length > 0 && (
            <Tooltip title="基于向量相似度的智能分析">
              <ExclamationCircleOutlined style={{ color: "#faad14" }} />
            </Tooltip>
          )
        }
        style={{ marginBottom: 16 }}
        styles={{
          body: {
            padding: similarObjects.length > 0 ? "0 12px" : 16,
            maxHeight: viewConfig.height || "auto",
            overflow: "auto",
          },
        }}
      >
        {similarObjects.length > 0 ? (
          <>
            {/* Alert for high similarity */}
            {similarObjects.some((o) => o.similarity_score >= 0.95) && (
              <div
                style={{
                  padding: "8px 12px",
                  margin: "8px 0",
                  background: "rgba(255, 77, 79, 0.1)",
                  border: "1px solid rgba(255, 77, 79, 0.3)",
                  borderRadius: 4,
                }}
              >
                <Space>
                  <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />
                  <Text style={{ color: "#ff4d4f", fontSize: 12 }}>
                    检测到极高相似度对象，建议进一步核实
                  </Text>
                </Space>
              </div>
            )}
            
            <List
              size="small"
              dataSource={similarObjects}
              renderItem={renderItem}
            />
          </>
        ) : (
          <Empty
            image={<RobotOutlined style={{ fontSize: 48, color: "#666" }} />}
            description={
              <Space direction="vertical" size={0}>
                <Text type="secondary">暂无相似对象</Text>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  向量索引可能尚未建立
                </Text>
              </Space>
            }
          />
        )}
      </Card>

      {/* Comparison Modal */}
      <Modal
        open={compareModalVisible}
        title={
          <Space>
            <SwapOutlined />
            <span>对比分析</span>
          </Space>
        }
        onCancel={() => setCompareModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setCompareModalVisible(false)}>
            关闭
          </Button>,
          <Button
            key="view"
            type="primary"
            icon={<EyeOutlined />}
            onClick={() => {
              if (selectedObject) {
                handleViewObject(selectedObject);
                setCompareModalVisible(false);
              }
            }}
          >
            查看完整详情
          </Button>,
        ]}
        width={800}
      >
        {selectedObject && (
          <Row gutter={24}>
            {/* Current Object */}
            <Col span={12}>
              <Card
                size="small"
                title={
                  <Space>
                    <CheckCircleOutlined style={{ color: "#1890ff" }} />
                    <Text>当前对象</Text>
                  </Space>
                }
              >
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="ID">
                    {objectId}
                  </Descriptions.Item>
                  <Descriptions.Item label="类型">
                    {objectType}
                  </Descriptions.Item>
                  {Object.entries(data?.properties || {}).slice(0, 5).map(([key, value]) => (
                    <Descriptions.Item key={key} label={key}>
                      {String(value)}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              </Card>
            </Col>
            
            {/* Similar Object */}
            <Col span={12}>
              <Card
                size="small"
                title={
                  <Space>
                    <ThunderboltOutlined style={{ color: getSimilarityColor(selectedObject.similarity_score) }} />
                    <Text>相似对象</Text>
                    <Tag color={getSimilarityColor(selectedObject.similarity_score)}>
                      {Math.round(selectedObject.similarity_score * 100)}% 匹配
                    </Tag>
                  </Space>
                }
              >
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="ID">
                    {selectedObject.id}
                  </Descriptions.Item>
                  <Descriptions.Item label="类型">
                    {selectedObject.object_type}
                  </Descriptions.Item>
                  <Descriptions.Item label="标签">
                    {selectedObject.label}
                  </Descriptions.Item>
                  {Object.entries(selectedObject.properties || {}).slice(0, 4).map(([key, value]) => (
                    <Descriptions.Item key={key} label={key}>
                      {String(value)}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              </Card>
            </Col>
          </Row>
        )}
      </Modal>
    </>
  );
};

export default AIInsights;
