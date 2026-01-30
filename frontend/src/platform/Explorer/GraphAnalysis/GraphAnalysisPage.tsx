/**
 * GraphAnalysisPage - Main Graph Analysis Workspace
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Palantir-style immersive graph exploration with:
 * - Dark theme
 * - Left sidebar for legend and options
 * - Main canvas for graph visualization
 * - Bottom time filter panel
 */

import React, { useState, useCallback, useEffect } from "react";
import {
  Layout,
  Typography,
  Space,
  Input,
  Button,
  Card,
  Tag,
  List,
  Checkbox,
  Divider,
  message,
  Statistic,
  Row,
  Col,
} from "antd";
import {
  SearchOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ClusterOutlined,
} from "@ant-design/icons";

import GraphCanvas from "./GraphCanvas";
import GraphControls from "./GraphControls";
import TimeFilter from "./TimeFilter";
import {
  getGraphStats,
  getNodeTypeLabel,
  getNodeColor,
  getNodeIcon,
  IGraphStats,
} from "../../../api/v3/graph";

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

// Node type configuration for legend
const NODE_TYPES = [
  "target",
  "vessel",
  "aircraft",
  "mission",
  "sensor",
  "intel_report",
  "port",
  "command_unit",
  "recon_image",
  "source",
];

const GraphAnalysisPage: React.FC = () => {
  // State
  const [seedIds, setSeedIds] = useState<string[]>([]);
  const [seedInput, setSeedInput] = useState("");
  const [showSemantic, setShowSemantic] = useState(false);
  const [showHardLinks, setShowHardLinks] = useState(true);
  const [layout, setLayout] = useState<"dagre" | "force" | "circular">("dagre");
  const [timeRange, setTimeRange] = useState<[Date, Date] | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [stats, setStats] = useState<IGraphStats | null>(null);
  const [visibleTypes, setVisibleTypes] = useState<Set<string>>(
    new Set(NODE_TYPES)
  );
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Load stats on mount
  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await getGraphStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to load stats:", error);
      }
    };
    loadStats();
  }, []);

  // Handle adding seed
  const handleAddSeed = useCallback(() => {
    if (!seedInput.trim()) return;

    const newSeeds = seedInput
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s && !seedIds.includes(s));

    if (newSeeds.length > 0) {
      setSeedIds([...seedIds, ...newSeeds]);
      message.success(`添加了 ${newSeeds.length} 个种子节点`);
    }
    setSeedInput("");
  }, [seedInput, seedIds]);

  // Handle removing seed
  const handleRemoveSeed = useCallback((id: string) => {
    setSeedIds((prev) => prev.filter((s) => s !== id));
  }, []);

  // Toggle node type visibility
  const toggleTypeVisibility = useCallback((type: string) => {
    setVisibleTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  }, []);

  // Refresh graph
  const handleRefresh = useCallback(() => {
    // Force re-render by resetting seeds
    const currentSeeds = [...seedIds];
    setSeedIds([]);
    setTimeout(() => setSeedIds(currentSeeds), 100);
  }, [seedIds]);

  // Handle search
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      message.info(`搜索: ${query}`);
    }
  }, []);

  // Handle fullscreen
  const handleFullscreen = useCallback(() => {
    const elem = document.documentElement;
    if (!isFullscreen) {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  }, [isFullscreen]);

  return (
    <Layout
      style={{
        // 抵消 MainLayout 的 margin 和 padding
        margin: "-24px",
        height: "calc(100vh - 48px)",
        width: "calc(100% + 48px)",
        background: "#141414",
      }}
    >
      {/* Left Sidebar */}
      <Sider
        width={280}
        style={{
          background: "#1f1f1f",
          borderRight: "1px solid #333",
          overflow: "auto",
        }}
      >
        <div style={{ padding: 16 }}>
          {/* Header */}
          <Space align="center" style={{ marginBottom: 16 }}>
            <BranchesOutlined style={{ fontSize: 20, color: "#1890ff" }} />
            <Title level={5} style={{ margin: 0, color: "#fff" }}>
              图谱分析
            </Title>
          </Space>

          {/* Stats */}
          {stats && (
            <Card
              size="small"
              style={{
                background: "#141414",
                border: "1px solid #333",
                marginBottom: 16,
              }}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title={<Text style={{ color: "#666" }}>节点数</Text>}
                    value={stats.unique_nodes}
                    prefix={<NodeIndexOutlined />}
                    valueStyle={{ color: "#1890ff", fontSize: 18 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title={<Text style={{ color: "#666" }}>链接数</Text>}
                    value={stats.total_links}
                    prefix={<ClusterOutlined />}
                    valueStyle={{ color: "#52c41a", fontSize: 18 }}
                  />
                </Col>
              </Row>
            </Card>
          )}

          {/* Seed Input */}
          <div style={{ marginBottom: 16 }}>
            <Text style={{ color: "#aaa", fontSize: 12 }}>添加种子节点</Text>
            <Input.Search
              placeholder="输入节点ID (如 tgt-001)"
              value={seedInput}
              onChange={(e) => setSeedInput(e.target.value)}
              onSearch={handleAddSeed}
              enterButton={<SearchOutlined />}
              style={{ marginTop: 4 }}
            />
          </div>

          {/* Current Seeds */}
          {seedIds.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <Text style={{ color: "#aaa", fontSize: 12 }}>当前种子</Text>
              <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 4 }}>
                {seedIds.map((id) => (
                  <Tag
                    key={id}
                    closable
                    onClose={() => handleRemoveSeed(id)}
                    color="blue"
                  >
                    {id}
                  </Tag>
                ))}
              </div>
            </div>
          )}

          <Divider style={{ borderColor: "#333", margin: "12px 0" }} />

          {/* Node Type Legend */}
          <Text style={{ color: "#aaa", fontSize: 12 }}>对象类型</Text>
          <List
            size="small"
            dataSource={NODE_TYPES}
            style={{ marginTop: 8 }}
            renderItem={(type) => (
              <List.Item
                style={{
                  padding: "4px 0",
                  borderBottom: "none",
                  opacity: visibleTypes.has(type) ? 1 : 0.4,
                  cursor: "pointer",
                }}
                onClick={() => toggleTypeVisibility(type)}
              >
                <Space>
                  <Checkbox checked={visibleTypes.has(type)} />
                  <span style={{ fontSize: 16 }}>{getNodeIcon(type)}</span>
                  <Text style={{ color: getNodeColor(type) }}>
                    {getNodeTypeLabel(type)}
                  </Text>
                </Space>
              </List.Item>
            )}
          />

          <Divider style={{ borderColor: "#333", margin: "12px 0" }} />

          {/* Edge Type Legend */}
          <Text style={{ color: "#aaa", fontSize: 12 }}>链接类型</Text>
          <div style={{ marginTop: 8 }}>
            <Space direction="vertical" size="small">
              <Space>
                <div
                  style={{
                    width: 24,
                    height: 2,
                    background: "#666",
                    display: "inline-block",
                  }}
                />
                <Text style={{ color: "#888", fontSize: 12 }}>关系链接</Text>
              </Space>
              <Space>
                <div
                  style={{
                    width: 24,
                    height: 2,
                    background: "#722ed1",
                    display: "inline-block",
                    backgroundImage:
                      "repeating-linear-gradient(90deg, #722ed1 0, #722ed1 4px, transparent 4px, transparent 8px)",
                  }}
                />
                <Text style={{ color: "#888", fontSize: 12 }}>语义链接</Text>
              </Space>
            </Space>
          </div>
        </div>
      </Sider>

      {/* Main Content */}
      <Layout style={{ background: "#141414", display: "flex", flexDirection: "column" }}>
        {/* Controls */}
        <GraphControls
          layout={layout}
          onLayoutChange={setLayout}
          showSemantic={showSemantic}
          onShowSemanticChange={setShowSemantic}
          showHardLinks={showHardLinks}
          onShowHardLinksChange={setShowHardLinks}
          onSearch={handleSearch}
          onRefresh={handleRefresh}
          onFullscreen={handleFullscreen}
        />

        {/* Graph Canvas */}
        <Content style={{ position: "relative", overflow: "hidden", flex: 1, minHeight: 0 }}>
          <GraphCanvas
            seedIds={seedIds}
            showSemantic={showSemantic}
            showHardLinks={showHardLinks}
            layout={layout}
            timeRange={timeRange}
            visibleTypes={visibleTypes}
            searchQuery={searchQuery}
            onNodeSelect={setSelectedNode}
          />
        </Content>

        {/* Time Filter */}
        <TimeFilter value={timeRange} onChange={setTimeRange} />
      </Layout>
    </Layout>
  );
};

export default GraphAnalysisPage;
