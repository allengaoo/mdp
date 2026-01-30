/**
 * AMIS Schema Renderer Component
 * MDP Platform V3.1
 * 
 * Renders Baidu AMIS JSON schemas to React components.
 */

import React, { useMemo, useState, useEffect } from 'react';
import { Table, Card, Empty, Alert, Spin } from 'antd';
import ReactECharts from 'echarts-for-react';
import v3Client from '../../api/v3/client';

interface AmisApiConfig {
  /** API endpoint URL (e.g., '/api/v3/sql/run') */
  url: string;
  /** HTTP method (default: 'POST') */
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  /** Request payload/data */
  data?: Record<string, any>;
  /** Query parameters (for GET requests) */
  params?: Record<string, any>;
  /** Data adapter function name (optional) */
  adaptor?: string;
}

interface AmisSchema {
  type: string;
  columns?: Array<{ name: string; label: string }>;
  data?: { items?: any[] } & Record<string, any>;
  config?: Record<string, any>;
  body?: any;
  /** API configuration for dynamic data fetching */
  api?: AmisApiConfig | string;
  [key: string]: any;
}

interface AmisRendererProps {
  schema: AmisSchema | null;
  className?: string;
}

/**
 * Fetcher function for AMIS API calls
 * Handles dynamic data fetching from backend endpoints
 */
const amisFetcher = async (apiConfig: AmisApiConfig | string): Promise<any> => {
  console.log('[AmisRenderer] Fetcher called with config:', apiConfig);
  
  // Normalize API config
  let config: AmisApiConfig;
  if (typeof apiConfig === 'string') {
    config = { url: apiConfig, method: 'POST' };
  } else {
    config = {
      url: apiConfig.url,
      method: apiConfig.method || 'POST',
      data: apiConfig.data,
      params: apiConfig.params,
    };
  }
  
  console.log('[AmisRenderer] Fetcher - Normalized config:', config);
  console.log('[AmisRenderer] Fetcher - URL:', config.url);
  console.log('[AmisRenderer] Fetcher - Method:', config.method);
  console.log('[AmisRenderer] Fetcher - Payload:', config.data || config.params);
  
  try {
    // Use v3Client which already handles auth headers and base URL
    let response;
    
    if (config.method === 'GET') {
      response = await v3Client.get(config.url, {
        params: config.params,
      });
    } else {
      // POST, PUT, DELETE
      response = await v3Client.request({
        method: config.method || 'POST',
        url: config.url,
        data: config.data,
        params: config.params,
      });
    }
    
    console.log('[AmisRenderer] Fetcher - Response status:', response.status);
    console.log('[AmisRenderer] Fetcher - Response data:', response.data);
    
    // Return response data
    // AMIS typically expects: { status: 0, data: {...}, msg: '' }
    // But we'll return raw data and let the component handle it
    return response.data;
  } catch (error: any) {
    console.error('[AmisRenderer] Fetcher - Error:', error);
    console.error('[AmisRenderer] Fetcher - Error response:', error.response?.data);
    
    // Return error in AMIS format
    return {
      status: error.response?.status || 500,
      msg: error.response?.data?.detail || error.message || '请求失败',
      data: null,
    };
  }
};

/**
 * Render AMIS table schema to Ant Design Table
 */
const renderTable = (schema: AmisSchema) => {
  console.log('[AmisRenderer] renderTable - Schema:', schema);
  console.log('[AmisRenderer] renderTable - Columns:', schema.columns);
  console.log('[AmisRenderer] renderTable - Data items count:', schema.data?.items?.length);
  
  const columns = schema.columns?.map((col) => ({
    title: col.label,
    dataIndex: col.name,
    key: col.name,
    ellipsis: true,
  })) || [];

  const dataSource = schema.data?.items?.map((item, idx) => ({
    ...item,
    key: item.id || idx,
  })) || [];
  
  console.log('[AmisRenderer] renderTable - Processed columns:', columns.length);
  console.log('[AmisRenderer] renderTable - Processed dataSource:', dataSource.length);

  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      size="small"
      pagination={{ pageSize: 10, showSizeChanger: true }}
      scroll={{ x: 'max-content' }}
    />
  );
};

/**
 * Render AMIS chart schema to ECharts
 */
const renderChart = (schema: AmisSchema) => {
  console.log('[AmisRenderer] renderChart - Schema:', schema);
  console.log('[AmisRenderer] renderChart - Config:', schema.config);
  console.log('[AmisRenderer] renderChart - Data:', schema.data);
  
  const config = schema.config || {};
  const data = schema.data || {};

  // Merge config with data
  const option = {
    ...config,
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: 300 }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

/**
 * Render AMIS form schema (placeholder for future)
 */
const renderForm = (schema: AmisSchema) => {
  console.log('[AmisRenderer] renderForm - Schema:', schema);
  return (
    <Alert
      message="表单渲染"
      description="表单组件即将支持"
      type="info"
      showIcon
    />
  );
};

/**
 * Main AMIS Renderer Component
 */
export const AmisRenderer: React.FC<AmisRendererProps> = ({ schema, className }) => {
  // State for dynamic data fetched from API
  const [fetchedData, setFetchedData] = useState<any>(null);
  const [fetching, setFetching] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  
  // Debug: Log incoming schema prop
  console.log('[AmisRenderer] Component rendered with schema:', schema);
  console.log('[AmisRenderer] Schema type:', schema?.type);
  console.log('[AmisRenderer] Schema is null?', schema === null);
  console.log('[AmisRenderer] Schema is undefined?', schema === undefined);
  
  if (schema) {
    console.log('[AmisRenderer] Full schema JSON:', JSON.stringify(schema, null, 2));
    console.log('[AmisRenderer] Schema keys:', Object.keys(schema));
    console.log('[AmisRenderer] Schema has API config?', !!schema.api);
    if (schema.api) {
      console.log('[AmisRenderer] API config:', schema.api);
    }
  }
  
  // Fetch data from API if schema contains api config
  useEffect(() => {
    if (!schema || !schema.api) {
      console.log('[AmisRenderer] No API config, skipping fetch');
      return;
    }
    
    const fetchData = async () => {
      setFetching(true);
      setFetchError(null);
      
      try {
        console.log('[AmisRenderer] Starting API fetch...');
        const result = await amisFetcher(schema.api!);
        
        console.log('[AmisRenderer] Fetch completed, result:', result);
        
        // Handle AMIS response format: { status: 0, data: {...}, msg: '' }
        if (result && typeof result === 'object') {
          if (result.status === 0 || result.status === undefined) {
            // Success
            setFetchedData(result.data || result);
          } else {
            // Error response
            setFetchError(result.msg || `API returned status ${result.status}`);
            console.error('[AmisRenderer] API error:', result.msg);
          }
        } else {
          // Direct data
          setFetchedData(result);
        }
      } catch (error: any) {
        console.error('[AmisRenderer] Fetch error:', error);
        setFetchError(error.message || '数据获取失败');
      } finally {
        setFetching(false);
      }
    };
    
    fetchData();
  }, [schema?.api]); // Only re-fetch if API config changes
  
  // Merge fetched data into schema
  const effectiveSchema = useMemo(() => {
    if (!schema) return null;
    
    // If we have fetched data, merge it into schema
    if (fetchedData) {
      console.log('[AmisRenderer] Merging fetched data into schema');
      console.log('[AmisRenderer] Fetched data:', fetchedData);
      
      const merged = { ...schema };
      
      // Handle different data formats
      if (fetchedData.items) {
        // Direct items array
        merged.data = { ...merged.data, items: fetchedData.items };
      } else if (Array.isArray(fetchedData)) {
        // Array of items
        merged.data = { ...merged.data, items: fetchedData };
      } else if (fetchedData.data) {
        // Nested data object
        merged.data = { ...merged.data, ...fetchedData.data };
      } else {
        // Merge all fields
        merged.data = { ...merged.data, ...fetchedData };
      }
      
      console.log('[AmisRenderer] Merged schema:', merged);
      return merged;
    }
    
    return schema;
  }, [schema, fetchedData]);
  
  const content = useMemo(() => {
    console.log('[AmisRenderer] useMemo - Processing schema:', effectiveSchema);
    console.log('[AmisRenderer] useMemo - Fetching:', fetching);
    console.log('[AmisRenderer] useMemo - Fetch error:', fetchError);
    
    // Show loading state while fetching
    if (fetching) {
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" tip="正在加载数据..." />
        </div>
      );
    }
    
    // Show error if fetch failed
    if (fetchError) {
      return (
        <Alert
          message="数据加载失败"
          description={fetchError}
          type="error"
          showIcon
        />
      );
    }
    
    if (!effectiveSchema) {
      console.log('[AmisRenderer] useMemo - Schema is null/undefined, returning Empty');
      return <Empty description="无数据" />;
    }

    console.log('[AmisRenderer] useMemo - Schema type:', effectiveSchema.type);
    console.log('[AmisRenderer] useMemo - Switching on type:', effectiveSchema.type);

    switch (effectiveSchema.type) {
      case 'table':
        console.log('[AmisRenderer] useMemo - Rendering table');
        return renderTable(effectiveSchema);
      case 'chart':
        console.log('[AmisRenderer] useMemo - Rendering chart');
        return renderChart(effectiveSchema);
      case 'form':
        console.log('[AmisRenderer] useMemo - Rendering form');
        return renderForm(effectiveSchema);
      default:
        console.warn('[AmisRenderer] useMemo - Unknown schema type:', effectiveSchema.type);
        console.warn('[AmisRenderer] useMemo - Full schema:', effectiveSchema);
        return (
          <Alert
            message={`未知组件类型: ${effectiveSchema.type}`}
            description={
              <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>
                {JSON.stringify(effectiveSchema, null, 2)}
              </pre>
            }
            type="warning"
          />
        );
    }
  }, [effectiveSchema, fetching, fetchError]);

  return (
    <Card className={className} bodyStyle={{ padding: 16 }}>
      {content}
    </Card>
  );
};

export default AmisRenderer;
