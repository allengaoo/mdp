/**
 * WidgetFactory - Dynamic Widget Renderer
 * MDP Platform V3.1 - Object 360 View
 * 
 * This is the core of the low-code architecture.
 * It dynamically renders widgets based on the widget_type from configuration.
 */

import React from "react";
import { Card, Typography, Empty } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";
import type { WidgetProps, WidgetType, WidgetConfig, Object360Data } from "./types";

// Import all widget components
import {
  PropertiesCard,
  StatCard,
  MiniMap,
  ObjectTimeline,
  RelationList,
  MediaCarousel,
  AIInsights,
} from "./widgets";

const { Text } = Typography;

// Widget component registry
const WIDGET_COMPONENTS: Record<WidgetType, React.FC<WidgetProps>> = {
  PROPERTY_LIST: PropertiesCard,
  STAT_CARD: StatCard,
  MINI_MAP: MiniMap,
  TIMELINE: ObjectTimeline,
  RELATION_LIST: RelationList,
  MEDIA_CAROUSEL: MediaCarousel,
  AI_INSIGHTS: AIInsights,
  // Placeholder for future widgets
  CHART: PlaceholderWidget,
  TABLE: PlaceholderWidget,
  GALLERY: PlaceholderWidget,
  SEARCH: PlaceholderWidget,
  FORM: PlaceholderWidget,
};

// Placeholder widget for unimplemented types
function PlaceholderWidget({ config }: WidgetProps): React.ReactElement {
  return (
    <Card
      size="small"
      style={{ marginBottom: 16 }}
      styles={{ body: { padding: 24 } }}
    >
      <Empty
        image={<QuestionCircleOutlined style={{ fontSize: 32, color: "#666" }} />}
        description={
          <Text type="secondary">
            组件类型 "{config.widget_type}" 尚未实现
          </Text>
        }
      />
    </Card>
  );
}

// WidgetFactory Props
interface WidgetFactoryProps {
  config: WidgetConfig;
  data: Object360Data;
  objectId: string;
  objectType: string;
  onAction?: (action: string, payload?: any) => void;
}

/**
 * WidgetFactory Component
 * 
 * Dynamically renders the appropriate widget based on widget_type.
 * This is the "switcher" that maps configuration to React components.
 * 
 * Adding a new widget type:
 * 1. Create the widget component in ./widgets/
 * 2. Add it to the WIDGET_COMPONENTS registry above
 * 3. The widget will automatically be available for use
 */
const WidgetFactory: React.FC<WidgetFactoryProps> = ({
  config,
  data,
  objectId,
  objectType,
  onAction,
}) => {
  // Get the widget component from registry
  const WidgetComponent = WIDGET_COMPONENTS[config.widget_type];

  if (!WidgetComponent) {
    console.warn(`Unknown widget type: ${config.widget_type}`);
    return (
      <Card
        size="small"
        style={{ marginBottom: 16 }}
        styles={{ body: { padding: 24 } }}
      >
        <Empty
          image={<QuestionCircleOutlined style={{ fontSize: 32, color: "#ff4d4f" }} />}
          description={
            <Text type="danger">
              未知的组件类型: "{config.widget_type}"
            </Text>
          }
        />
      </Card>
    );
  }

  // Render the widget with props
  return (
    <WidgetComponent
      config={config}
      data={data}
      objectId={objectId}
      objectType={objectType}
      onAction={onAction}
    />
  );
};

export default WidgetFactory;

// Export for external use
export { WIDGET_COMPONENTS };
