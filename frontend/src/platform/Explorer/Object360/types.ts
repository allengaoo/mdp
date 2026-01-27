/**
 * Object 360 View Types
 * MDP Platform V3.1 - Low-Code Object Profile
 */

// =============================================================================
// View Configuration Types (from backend)
// =============================================================================

export interface WidgetConfig {
  id: string;
  widget_type: WidgetType;
  data_binding: Record<string, any>;
  view_config?: Record<string, any>;
  position_config?: {
    order?: number;
    height?: number | "auto";
  };
}

export interface ModuleConfig {
  id: string;
  name: string | null;
  layout_config?: {
    width?: number;
    position?: "left" | "center" | "right";
    collapsible?: boolean;
    scrollable?: boolean;
  };
  display_order: number;
  widgets: WidgetConfig[];
}

export interface ViewConfig {
  id: string;
  name: string;
  app_type: string;
  global_config?: {
    object_type?: string;
    theme?: "light" | "dark";
    refresh_interval?: number;
  };
  modules: ModuleConfig[];
}

// =============================================================================
// Widget Types (extensible)
// =============================================================================

export type WidgetType =
  | "PROPERTY_LIST"
  | "MINI_MAP"
  | "TIMELINE"
  | "RELATION_LIST"
  | "MEDIA_CAROUSEL"
  | "AI_INSIGHTS"
  | "STAT_CARD"
  | "CHART"
  | "TABLE"
  | "GALLERY"
  | "SEARCH"
  | "FORM";

// =============================================================================
// Object 360 Data Types
// =============================================================================

export interface TimelineEvent {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  timestamp: string;
  icon?: string;
  color?: string;
  metadata?: Record<string, any>;
}

export interface Relation {
  id: string;
  link_type: string;
  target_id: string;
  target_type: string;
  target_label: string;
  direction: "outgoing" | "incoming";
  properties?: Record<string, any>;
}

export interface SimilarObject {
  id: string;
  object_type: string;
  label: string;
  similarity_score: number;
  properties?: Record<string, any>;
}

export interface Object360Data {
  object_id: string;
  object_type: string;
  properties: Record<string, any>;
  relations: Record<string, Relation[]>;
  timeline_events: TimelineEvent[];
  similar_objects: SimilarObject[];
  media_urls: string[];
  stats: Record<string, any>;
}

// =============================================================================
// Component Props Types
// =============================================================================

export interface WidgetProps<T = any> {
  config: WidgetConfig;
  data: Object360Data;
  objectId: string;
  objectType: string;
  onAction?: (action: string, payload?: any) => void;
}

export interface ModuleProps {
  config: ModuleConfig;
  data: Object360Data;
  objectId: string;
  objectType: string;
  onAction?: (action: string, payload?: any) => void;
}

// =============================================================================
// Widget Registry (for dynamic rendering)
// =============================================================================

export interface WidgetDefinition {
  type: WidgetType;
  name: string;
  icon: string;
  description: string;
  defaultConfig: Partial<WidgetConfig>;
}

export const WIDGET_REGISTRY: Record<WidgetType, WidgetDefinition> = {
  PROPERTY_LIST: {
    type: "PROPERTY_LIST",
    name: "属性列表",
    icon: "profile",
    description: "显示对象的基本属性",
    defaultConfig: {
      data_binding: { fields: [] },
      view_config: { layout: "vertical" },
    },
  },
  MINI_MAP: {
    type: "MINI_MAP",
    name: "迷你地图",
    icon: "environment",
    description: "显示对象的地理位置",
    defaultConfig: {
      data_binding: { lat: "latitude", lon: "longitude" },
      view_config: { zoom: 12 },
    },
  },
  TIMELINE: {
    type: "TIMELINE",
    name: "时间线",
    icon: "history",
    description: "显示对象的活动历史",
    defaultConfig: {
      data_binding: { sources: ["sys_action_log"] },
      view_config: { mode: "left" },
    },
  },
  RELATION_LIST: {
    type: "RELATION_LIST",
    name: "关联列表",
    icon: "apartment",
    description: "显示对象的关联关系",
    defaultConfig: {
      data_binding: { link_types: [] },
      view_config: { showType: true },
    },
  },
  MEDIA_CAROUSEL: {
    type: "MEDIA_CAROUSEL",
    name: "媒体轮播",
    icon: "picture",
    description: "显示关联的图片和视频",
    defaultConfig: {
      data_binding: { link_type: "has_media" },
      view_config: { autoPlay: false },
    },
  },
  AI_INSIGHTS: {
    type: "AI_INSIGHTS",
    name: "AI 分析",
    icon: "robot",
    description: "显示向量相似度分析结果",
    defaultConfig: {
      data_binding: { vector_field: "embedding", top_k: 5 },
      view_config: { showScore: true },
    },
  },
  STAT_CARD: {
    type: "STAT_CARD",
    name: "统计卡片",
    icon: "fund",
    description: "显示统计数据摘要",
    defaultConfig: {
      data_binding: { metrics: [] },
      view_config: { layout: "grid" },
    },
  },
  CHART: {
    type: "CHART",
    name: "图表",
    icon: "bar-chart",
    description: "数据可视化图表",
    defaultConfig: {
      data_binding: { chartType: "line" },
      view_config: {},
    },
  },
  TABLE: {
    type: "TABLE",
    name: "数据表格",
    icon: "table",
    description: "表格形式展示数据",
    defaultConfig: {
      data_binding: { columns: [] },
      view_config: { pagination: true },
    },
  },
  GALLERY: {
    type: "GALLERY",
    name: "图库",
    icon: "appstore",
    description: "图片网格展示",
    defaultConfig: {
      data_binding: {},
      view_config: { columns: 3 },
    },
  },
  SEARCH: {
    type: "SEARCH",
    name: "搜索框",
    icon: "search",
    description: "对象内搜索",
    defaultConfig: {
      data_binding: {},
      view_config: {},
    },
  },
  FORM: {
    type: "FORM",
    name: "表单",
    icon: "form",
    description: "数据录入表单",
    defaultConfig: {
      data_binding: { fields: [] },
      view_config: {},
    },
  },
};
