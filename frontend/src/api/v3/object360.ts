/**
 * Object 360 View API Client
 * MDP Platform V3.1
 */

import v3Client from "./client";
import type {
  ViewConfig,
  Object360Data,
} from "../../platform/Explorer/Object360/types";

// =============================================================================
// View Configuration API
// =============================================================================

/**
 * Get view configuration for a specific object type.
 * Returns the complete layout config (App -> Modules -> Widgets).
 */
export async function getViewConfig(objectType: string): Promise<ViewConfig> {
  const response = await v3Client.get<ViewConfig>(
    `/object-views/config/${encodeURIComponent(objectType)}`
  );
  return response.data;
}

/**
 * Get list of object types that have 360 view configurations.
 */
export async function getAvailableObjectTypes(): Promise<
  Array<{
    object_type: string;
    view_name: string;
    app_id: string;
  }>
> {
  const response = await v3Client.get(`/object-views/types`);
  return response.data;
}

// =============================================================================
// Object 360 Data API
// =============================================================================

/**
 * Get aggregated 360 data for a specific object.
 * Performs scatter-gather to collect data from multiple sources.
 */
export async function getObject360Data(
  objectId: string,
  objectType: string
): Promise<Object360Data> {
  const response = await v3Client.get<Object360Data>(
    `/objects/${encodeURIComponent(objectId)}/360-data`,
    {
      params: { object_type: objectType },
    }
  );
  return response.data;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Format property value for display.
 */
export function formatPropertyValue(value: any, type?: string): string {
  if (value === null || value === undefined) {
    return "-";
  }

  if (type === "datetime" || value instanceof Date) {
    return new Date(value).toLocaleString("zh-CN");
  }

  if (type === "boolean" || typeof value === "boolean") {
    return value ? "是" : "否";
  }

  if (Array.isArray(value)) {
    return value.join(", ");
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

/**
 * Get display label for a property key.
 */
export function getPropertyLabel(key: string): string {
  const labels: Record<string, string> = {
    id: "ID",
    name: "名称",
    mmsi: "MMSI",
    imo: "IMO",
    country: "国家/地区",
    status: "状态",
    threat_level: "威胁等级",
    speed: "速度",
    heading: "航向",
    latitude: "纬度",
    longitude: "经度",
    created_at: "创建时间",
    updated_at: "更新时间",
    object_type: "对象类型",
  };

  return labels[key] || key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Get color for threat level.
 */
export function getThreatLevelColor(level: string | number): string {
  const colors: Record<string, string> = {
    low: "#52c41a",
    medium: "#faad14",
    high: "#ff4d4f",
    critical: "#cf1322",
    "1": "#52c41a",
    "2": "#73d13d",
    "3": "#faad14",
    "4": "#fa8c16",
    "5": "#ff4d4f",
  };

  return colors[String(level).toLowerCase()] || "#1890ff";
}

/**
 * Get status color.
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: "#52c41a",
    inactive: "#d9d9d9",
    pending: "#faad14",
    error: "#ff4d4f",
    success: "#52c41a",
    failed: "#ff4d4f",
    running: "#1890ff",
  };

  return colors[status?.toLowerCase()] || "#1890ff";
}

export default {
  getViewConfig,
  getAvailableObjectTypes,
  getObject360Data,
  formatPropertyValue,
  getPropertyLabel,
  getThreatLevelColor,
  getStatusColor,
};
