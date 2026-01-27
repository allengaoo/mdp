/**
 * Object 360 View Module - Exports
 * MDP Platform V3.1
 */

export { default as Object360Page } from "./Object360Page";
export { default as DynamicModule } from "./DynamicModule";
export { default as WidgetFactory } from "./WidgetFactory";

// Types
export type {
  ViewConfig,
  ModuleConfig,
  WidgetConfig,
  Object360Data,
  WidgetType,
  WidgetProps,
  ModuleProps,
  TimelineEvent,
  Relation,
  SimilarObject,
} from "./types";

// Widgets
export * from "./widgets";
