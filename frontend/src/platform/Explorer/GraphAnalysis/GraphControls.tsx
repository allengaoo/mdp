/**
 * GraphControls - Toolbar and Control Panel
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Features:
 * - Layout algorithm selection (Dagre, Force, Circular)
 * - Search within graph
 * - Toggle link visibility
 */

import React from "react";
import { Space, Button, Select, Input, Tooltip, Switch, Divider } from "antd";
import {
  ApartmentOutlined,
  RadarChartOutlined,
  SearchOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  ReloadOutlined,
  FullscreenOutlined,
  ShareAltOutlined,
} from "@ant-design/icons";

interface GraphControlsProps {
  layout: "dagre" | "force" | "circular";
  onLayoutChange: (layout: "dagre" | "force" | "circular") => void;
  showSemantic: boolean;
  onShowSemanticChange: (show: boolean) => void;
  showHardLinks: boolean;
  onShowHardLinksChange: (show: boolean) => void;
  onSearch?: (query: string) => void;
  onRefresh?: () => void;
  onFullscreen?: () => void;
}

const GraphControls: React.FC<GraphControlsProps> = ({
  layout,
  onLayoutChange,
  showSemantic,
  onShowSemanticChange,
  showHardLinks,
  onShowHardLinksChange,
  onSearch,
  onRefresh,
  onFullscreen,
}) => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "8px 16px",
        background: "#1f1f1f",
        borderBottom: "1px solid #333",
      }}
    >
      {/* Left: Layout & Search */}
      <Space size="middle">
        {/* Layout Selector */}
        <Select
          value={layout}
          onChange={onLayoutChange}
          style={{ width: 120 }}
          options={[
            {
              value: "dagre",
              label: (
                <Space>
                  <ApartmentOutlined /> 层级布局
                </Space>
              ),
            },
            {
              value: "force",
              label: (
                <Space>
                  <RadarChartOutlined /> 力导向
                </Space>
              ),
            },
            {
              value: "circular",
              label: (
                <Space>
                  <span>○</span> 环形布局
                </Space>
              ),
            },
          ]}
        />

        <Divider type="vertical" style={{ height: 24, background: "#444" }} />

        {/* Search */}
        <Input
          placeholder="在图中搜索..."
          prefix={<SearchOutlined style={{ color: "#666" }} />}
          style={{ width: 180 }}
          onPressEnter={(e) => onSearch?.(e.currentTarget.value)}
          allowClear
        />
      </Space>

      {/* Center: Link Toggles */}
      <Space size="large">
        <Space>
          <Tooltip title="显示关系链接（数据库存储的硬链接）">
            <span style={{ color: "#aaa", fontSize: 12 }}>关系链接</span>
          </Tooltip>
          <Switch
            checked={showHardLinks}
            onChange={onShowHardLinksChange}
            size="small"
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
          />
        </Space>

        <Space>
          <Tooltip title="显示语义链接（向量相似度）">
            <span style={{ color: "#aaa", fontSize: 12 }}>语义链接</span>
          </Tooltip>
          <Switch
            checked={showSemantic}
            onChange={onShowSemanticChange}
            size="small"
            checkedChildren={<ShareAltOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
          />
        </Space>
      </Space>

      {/* Right: Actions */}
      <Space>
        <Tooltip title="刷新">
          <Button
            type="text"
            icon={<ReloadOutlined />}
            onClick={onRefresh}
            style={{ color: "#aaa" }}
          />
        </Tooltip>
        <Tooltip title="全屏">
          <Button
            type="text"
            icon={<FullscreenOutlined />}
            onClick={onFullscreen}
            style={{ color: "#aaa" }}
          />
        </Tooltip>
      </Space>
    </div>
  );
};

export default GraphControls;
