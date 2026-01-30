/**
 * Connector Configuration Registry - MDP Platform V3.1
 * 
 * Defines form schemas for different connector types.
 * Enables extensibility without rewriting form components.
 */
import {
  DatabaseOutlined,
  CloudServerOutlined,
  ApiOutlined,
  MessageOutlined,
} from '@ant-design/icons';
import { ConnectorType } from '../../api/v3/connectors';

// ==========================================
// Field Definition Types
// ==========================================

export type FieldType = 'text' | 'number' | 'password' | 'select' | 'textarea';

export interface FieldOption {
  label: string;
  value: string | number;
}

export interface FieldDefinition {
  name: string;
  label: string;
  type?: FieldType;
  required?: boolean;
  default?: string | number | boolean;
  placeholder?: string;
  tooltip?: string;
  options?: FieldOption[];
  min?: number;
  max?: number;
}

export interface ConnectorDefinition {
  label: string;
  icon: React.ComponentType<any>;
  color: string;
  description: string;
  fields: FieldDefinition[];
  testable: boolean;
  explorable: boolean;
}

// ==========================================
// Connector Registry
// ==========================================

export const CONNECTOR_REGISTRY: Record<ConnectorType, ConnectorDefinition> = {
  MYSQL: {
    label: 'MySQL',
    icon: DatabaseOutlined,
    color: '#00758F',
    description: 'Connect to MySQL databases for structured data extraction.',
    testable: true,
    explorable: true,
    fields: [
      {
        name: 'host',
        label: '主机地址',
        type: 'text',
        required: true,
        placeholder: 'localhost',
        default: 'localhost',
      },
      {
        name: 'port',
        label: '端口',
        type: 'number',
        required: true,
        default: 3306,
        min: 1,
        max: 65535,
      },
      {
        name: 'database',
        label: '数据库名',
        type: 'text',
        required: true,
        placeholder: 'my_database',
      },
      {
        name: 'user',
        label: '用户名',
        type: 'text',
        required: true,
        placeholder: 'root',
        default: 'root',
      },
      {
        name: 'password',
        label: '密码',
        type: 'password',
        required: true,
        placeholder: '输入密码',
      },
    ],
  },

  POSTGRES: {
    label: 'PostgreSQL',
    icon: DatabaseOutlined,
    color: '#336791',
    description: 'Connect to PostgreSQL databases with advanced schema support.',
    testable: true,
    explorable: true,
    fields: [
      {
        name: 'host',
        label: '主机地址',
        type: 'text',
        required: true,
        placeholder: 'localhost',
        default: 'localhost',
      },
      {
        name: 'port',
        label: '端口',
        type: 'number',
        required: true,
        default: 5432,
        min: 1,
        max: 65535,
      },
      {
        name: 'database',
        label: '数据库名',
        type: 'text',
        required: true,
        placeholder: 'postgres',
      },
      {
        name: 'user',
        label: '用户名',
        type: 'text',
        required: true,
        placeholder: 'postgres',
        default: 'postgres',
      },
      {
        name: 'password',
        label: '密码',
        type: 'password',
        required: true,
        placeholder: '输入密码',
      },
      {
        name: 'schema',
        label: 'Schema',
        type: 'text',
        required: false,
        placeholder: 'public',
        default: 'public',
        tooltip: '默认使用 public schema',
      },
    ],
  },

  S3: {
    label: 'Amazon S3',
    icon: CloudServerOutlined,
    color: '#FF9900',
    description: 'Connect to S3 buckets for file-based data ingestion.',
    testable: true,
    explorable: false,
    fields: [
      {
        name: 'bucket',
        label: 'Bucket 名称',
        type: 'text',
        required: true,
        placeholder: 'my-bucket',
      },
      {
        name: 'region',
        label: 'AWS Region',
        type: 'select',
        required: true,
        default: 'us-east-1',
        options: [
          { label: 'US East (N. Virginia)', value: 'us-east-1' },
          { label: 'US West (Oregon)', value: 'us-west-2' },
          { label: 'Asia Pacific (Singapore)', value: 'ap-southeast-1' },
          { label: 'Asia Pacific (Tokyo)', value: 'ap-northeast-1' },
          { label: 'China (Beijing)', value: 'cn-north-1' },
          { label: 'China (Ningxia)', value: 'cn-northwest-1' },
        ],
      },
      {
        name: 'access_key',
        label: 'Access Key ID',
        type: 'text',
        required: true,
        placeholder: 'AKIAIOSFODNN7EXAMPLE',
      },
      {
        name: 'secret_key',
        label: 'Secret Access Key',
        type: 'password',
        required: true,
        placeholder: '输入 Secret Key',
      },
      {
        name: 'prefix',
        label: '路径前缀',
        type: 'text',
        required: false,
        placeholder: 'data/raw/',
        tooltip: '可选：限制访问特定路径前缀',
      },
    ],
  },

  KAFKA: {
    label: 'Apache Kafka',
    icon: MessageOutlined,
    color: '#231F20',
    description: 'Connect to Kafka clusters for real-time data streaming.',
    testable: true,
    explorable: false,
    fields: [
      {
        name: 'bootstrap_servers',
        label: 'Bootstrap Servers',
        type: 'text',
        required: true,
        placeholder: 'kafka1:9092,kafka2:9092',
        tooltip: '多个服务器用逗号分隔',
      },
      {
        name: 'security_protocol',
        label: '安全协议',
        type: 'select',
        required: false,
        default: 'PLAINTEXT',
        options: [
          { label: 'PLAINTEXT', value: 'PLAINTEXT' },
          { label: 'SSL', value: 'SSL' },
          { label: 'SASL_PLAINTEXT', value: 'SASL_PLAINTEXT' },
          { label: 'SASL_SSL', value: 'SASL_SSL' },
        ],
      },
      {
        name: 'sasl_mechanism',
        label: 'SASL 机制',
        type: 'select',
        required: false,
        options: [
          { label: 'PLAIN', value: 'PLAIN' },
          { label: 'SCRAM-SHA-256', value: 'SCRAM-SHA-256' },
          { label: 'SCRAM-SHA-512', value: 'SCRAM-SHA-512' },
        ],
      },
      {
        name: 'sasl_username',
        label: 'SASL 用户名',
        type: 'text',
        required: false,
        placeholder: '用户名',
      },
      {
        name: 'sasl_password',
        label: 'SASL 密码',
        type: 'password',
        required: false,
        placeholder: '密码',
      },
    ],
  },

  REST_API: {
    label: 'REST API',
    icon: ApiOutlined,
    color: '#52C41A',
    description: 'Connect to REST APIs for on-demand data fetching.',
    testable: true,
    explorable: false,
    fields: [
      {
        name: 'base_url',
        label: 'Base URL',
        type: 'text',
        required: true,
        placeholder: 'https://api.example.com/v1',
      },
      {
        name: 'auth_type',
        label: '认证方式',
        type: 'select',
        required: true,
        default: 'none',
        options: [
          { label: '无认证', value: 'none' },
          { label: 'API Key', value: 'api_key' },
          { label: 'Bearer Token', value: 'bearer' },
          { label: 'Basic Auth', value: 'basic' },
        ],
      },
      {
        name: 'api_key',
        label: 'API Key',
        type: 'password',
        required: false,
        placeholder: '输入 API Key',
        tooltip: '当认证方式为 API Key 时必填',
      },
      {
        name: 'api_key_header',
        label: 'API Key Header 名称',
        type: 'text',
        required: false,
        placeholder: 'X-API-Key',
        default: 'X-API-Key',
      },
      {
        name: 'bearer_token',
        label: 'Bearer Token',
        type: 'password',
        required: false,
        placeholder: '输入 Token',
        tooltip: '当认证方式为 Bearer Token 时必填',
      },
      {
        name: 'basic_username',
        label: 'Basic Auth 用户名',
        type: 'text',
        required: false,
      },
      {
        name: 'basic_password',
        label: 'Basic Auth 密码',
        type: 'password',
        required: false,
      },
      {
        name: 'timeout_seconds',
        label: '超时时间 (秒)',
        type: 'number',
        required: false,
        default: 30,
        min: 1,
        max: 300,
      },
    ],
  },
};

// ==========================================
// Helper Functions
// ==========================================

/**
 * Get connector definition by type.
 */
export const getConnectorDef = (type: ConnectorType): ConnectorDefinition => {
  return CONNECTOR_REGISTRY[type];
};

/**
 * Get all available connector types.
 */
export const getConnectorTypes = (): ConnectorType[] => {
  return Object.keys(CONNECTOR_REGISTRY) as ConnectorType[];
};

/**
 * Build default config from field definitions.
 */
export const buildDefaultConfig = (type: ConnectorType): Record<string, any> => {
  const def = CONNECTOR_REGISTRY[type];
  const config: Record<string, any> = {};
  
  def.fields.forEach(field => {
    if (field.default !== undefined) {
      config[field.name] = field.default;
    }
  });
  
  return config;
};

/**
 * Validate config against field definitions.
 */
export const validateConfig = (
  type: ConnectorType,
  config: Record<string, any>
): { valid: boolean; errors: string[] } => {
  const def = CONNECTOR_REGISTRY[type];
  const errors: string[] = [];
  
  def.fields.forEach(field => {
    if (field.required && !config[field.name]) {
      errors.push(`${field.label} 是必填项`);
    }
  });
  
  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Get display-safe config (hide sensitive fields).
 */
export const getSafeConfigSummary = (
  type: ConnectorType,
  config: Record<string, any>
): string => {
  const def = CONNECTOR_REGISTRY[type];
  const parts: string[] = [];
  
  // Pick key display fields based on type
  if (type === 'MYSQL' || type === 'POSTGRES') {
    parts.push(`${config.host || 'localhost'}:${config.port || 3306}`);
    if (config.database) parts.push(config.database);
  } else if (type === 'S3') {
    parts.push(`s3://${config.bucket || ''}`);
    if (config.region) parts.push(`(${config.region})`);
  } else if (type === 'KAFKA') {
    parts.push(config.bootstrap_servers || '');
  } else if (type === 'REST_API') {
    parts.push(config.base_url || '');
  }
  
  return parts.join(' / ');
};
