/**
 * Object360Page - Main Object Profile Page Controller
 * MDP Platform V3.1 - Object 360 View
 * 
 * This is the main controller that:
 * 1. Fetches view configuration based on object type
 * 2. Fetches 360 data for the specific object
 * 3. Dynamically renders modules and widgets
 * 
 * Key Design: The layout is NOT hardcoded.
 * If you add a new widget in the database, it will automatically appear.
 */

import React, { useState, useEffect, useCallback } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import {
  Layout,
  Row,
  Spin,
  Typography,
  Space,
  Button,
  Breadcrumb,
  Alert,
  message,
  Tooltip,
  Tag,
} from "antd";
import {
  ArrowLeftOutlined,
  ReloadOutlined,
  SettingOutlined,
  FullscreenOutlined,
  ShareAltOutlined,
  ProfileOutlined,
} from "@ant-design/icons";
import type { ViewConfig, Object360Data } from "./types";
import { getViewConfig, getObject360Data } from "../../../api/v3/object360";
import DynamicModule from "./DynamicModule";

const { Content, Header } = Layout;
const { Title, Text } = Typography;

const Object360Page: React.FC = () => {
  const { objectId: pathObjectId } = useParams<{ objectId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // 优先使用路径参数，其次使用查询参数
  const objectId = pathObjectId || searchParams.get("id") || undefined;
  // Get object type from URL params or default to "Target"
  const objectType = searchParams.get("type") || "Target";
  
  // State
  const [viewConfig, setViewConfig] = useState<ViewConfig | null>(null);
  const [objectData, setObjectData] = useState<Object360Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch view configuration
  const fetchConfig = useCallback(async () => {
    try {
      const config = await getViewConfig(objectType);
      setViewConfig(config);
      return config;
    } catch (err: any) {
      console.error("Failed to fetch view config:", err);
      // Use a default config if none exists
      setViewConfig({
        id: "default",
        name: "Default Object View",
        app_type: "EXPLORER",
        global_config: { object_type: objectType },
        modules: [],
      });
      return null;
    }
  }, [objectType]);

  // Fetch object 360 data
  const fetchData = useCallback(async () => {
    if (!objectId) return;
    
    try {
      const data = await getObject360Data(objectId, objectType);
      setObjectData(data);
    } catch (err: any) {
      console.error("Failed to fetch object data:", err);
      // Use mock data for demo
      setObjectData({
        object_id: objectId,
        object_type: objectType,
        properties: {
          id: objectId,
          name: `${objectType} ${objectId.slice(0, 8)}`,
          status: "active",
          object_type: objectType,
          created_at: new Date().toISOString(),
        },
        relations: {},
        timeline_events: [],
        similar_objects: [],
        media_urls: [],
        stats: { total_relations: 0, total_actions: 0 },
      });
    }
  }, [objectId, objectType]);

  // Initial load
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      
      try {
        await Promise.all([fetchConfig(), fetchData()]);
      } catch (err: any) {
        setError(err.message || "加载失败");
      } finally {
        setLoading(false);
      }
    };
    
    load();
  }, [fetchConfig, fetchData]);

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([fetchConfig(), fetchData()]);
      message.success("数据已刷新");
    } catch (err) {
      message.error("刷新失败");
    } finally {
      setRefreshing(false);
    }
  };

  // Handle widget actions
  const handleAction = useCallback((action: string, payload?: any) => {
    switch (action) {
      case "view_object":
        if (payload?.objectId) {
          navigate(`/explore/object/${payload.objectId}?type=${payload.objectType || objectType}`);
        }
        break;
      case "expand_graph":
        if (payload?.objectId) {
          navigate(`/explore/graph?seed=${payload.objectId}`);
        }
        break;
      default:
        console.log("Unknown action:", action, payload);
    }
  }, [navigate, objectType]);

  // Sort modules by display_order
  const sortedModules = viewConfig?.modules
    ? [...viewConfig.modules].sort((a, b) => a.display_order - b.display_order)
    : [];

  // Loading state
  if (loading) {
    return (
      <div
        style={{
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#141414",
        }}
      >
        <Spin size="large" tip="加载对象视图..." />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          type="error"
          message="加载失败"
          description={error}
          action={
            <Button onClick={handleRefresh}>重试</Button>
          }
        />
      </div>
    );
  }

  return (
    <Layout
      style={{
        margin: "-24px",
        height: "calc(100vh - 48px)",
        width: "calc(100% + 48px)",
        background: "#141414",
      }}
    >
      {/* Header */}
      <Header
        style={{
          background: "#1f1f1f",
          padding: "0 24px",
          height: 56,
          lineHeight: "56px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid #303030",
        }}
      >
        <Space>
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
            style={{ color: "#aaa" }}
          />
          <ProfileOutlined style={{ fontSize: 20, color: "#1890ff" }} />
          <Title level={5} style={{ margin: 0, color: "#fff" }}>
            {viewConfig?.name || "对象详情"}
          </Title>
          <Tag color="blue">{objectType}</Tag>
          <Text type="secondary" style={{ fontSize: 12 }}>
            ID: {objectId?.slice(0, 12)}...
          </Text>
        </Space>
        
        <Space>
          <Tooltip title="刷新">
            <Button
              type="text"
              icon={<ReloadOutlined spin={refreshing} />}
              onClick={handleRefresh}
              style={{ color: "#aaa" }}
            />
          </Tooltip>
          <Tooltip title="分享">
            <Button
              type="text"
              icon={<ShareAltOutlined />}
              onClick={() => {
                navigator.clipboard.writeText(window.location.href);
                message.success("链接已复制");
              }}
              style={{ color: "#aaa" }}
            />
          </Tooltip>
          <Tooltip title="全屏">
            <Button
              type="text"
              icon={<FullscreenOutlined />}
              onClick={() => document.documentElement.requestFullscreen?.()}
              style={{ color: "#aaa" }}
            />
          </Tooltip>
        </Space>
      </Header>

      {/* Main Content */}
      <Content
        style={{
          flex: 1,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Breadcrumb */}
        <div
          style={{
            padding: "8px 24px",
            background: "#1a1a1a",
            borderBottom: "1px solid #303030",
          }}
        >
          <Breadcrumb
            items={[
              { title: <a onClick={() => navigate("/explore")}>探索</a> },
              { title: <a onClick={() => navigate("/explore/search")}>搜索</a> },
              { title: objectType },
              { title: objectId?.slice(0, 8) || "对象" },
            ]}
          />
        </div>

        {/* Dynamic Modules */}
        <div
          style={{
            flex: 1,
            padding: 16,
            overflow: "hidden",
          }}
        >
          {!objectId ? (
            <Alert
              type="warning"
              message="缺少对象 ID"
              description={
                <Space direction="vertical">
                  <Text>
                    请通过 URL 参数指定要查看的对象 ID。
                  </Text>
                  <Text type="secondary">
                    例如: /explore/object360?id=tgt-001&type=Target
                  </Text>
                </Space>
              }
              style={{ maxWidth: 500 }}
            />
          ) : sortedModules.length > 0 && objectData ? (
            <Row
              gutter={16}
              style={{
                height: "100%",
                margin: 0,
              }}
            >
              {sortedModules.map((moduleConfig) => (
                <DynamicModule
                  key={moduleConfig.id}
                  config={moduleConfig}
                  data={objectData}
                  objectId={objectId}
                  objectType={objectType}
                  onAction={handleAction}
                />
              ))}
            </Row>
          ) : sortedModules.length === 0 ? (
            <Alert
              type="info"
              message="无视图配置"
              description={
                <Space direction="vertical">
                  <Text>
                    未找到 "{objectType}" 对象类型的视图配置。
                  </Text>
                  <Text type="secondary">
                    请在 app_definition, app_module, app_widget 表中添加配置。
                  </Text>
                </Space>
              }
              style={{ maxWidth: 500 }}
            />
          ) : (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}>
              <Spin tip="加载数据中..." />
            </div>
          )}
        </div>

        {/* Auto-refresh indicator */}
        {viewConfig?.global_config?.refresh_interval && (
          <div
            style={{
              position: "fixed",
              bottom: 16,
              right: 16,
              background: "rgba(0,0,0,0.6)",
              padding: "4px 8px",
              borderRadius: 4,
              fontSize: 11,
              color: "#666",
            }}
          >
            自动刷新: {viewConfig.global_config.refresh_interval / 1000}s
          </div>
        )}
      </Content>
    </Layout>
  );
};

export default Object360Page;
