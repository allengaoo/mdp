/**
 * PreviewPanel - Bottom panel for mapping preview
 */
import React from 'react';
import { Card, Table, Button, Tag, Alert, Space, Tooltip } from 'antd';
import { PlayCircleOutlined, EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

interface PreviewPanelProps {
  columns: string[];
  data: Record<string, any>[];
  loading: boolean;
  warnings?: string[];
  onRunPreview: () => void;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({
  columns,
  data,
  loading,
  warnings,
  onRunPreview,
}) => {
  // Build table columns
  const tableColumns: ColumnsType<any> = columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    width: 150,
    render: (value: any) => {
      // Check if value is a vector (array of numbers)
      if (Array.isArray(value) && value.length > 10 && typeof value[0] === 'number') {
        return (
          <Tooltip
            title={
              <div style={{ maxHeight: 200, overflow: 'auto', fontSize: 11 }}>
                [{value.slice(0, 20).map((v: number) => v.toFixed(4)).join(', ')}
                {value.length > 20 ? `, ... (${value.length} dims)` : ''}]
              </div>
            }
          >
            <Tag color="purple" style={{ cursor: 'pointer' }}>
              <EyeOutlined /> Vector [{value.length}]
            </Tag>
          </Tooltip>
        );
      }
      
      // Handle null/undefined
      if (value === null || value === undefined) {
        return <span style={{ color: '#bfbfbf' }}>null</span>;
      }
      
      // Handle objects
      if (typeof value === 'object') {
        return JSON.stringify(value);
      }
      
      return String(value);
    },
  }));

  return (
    <Card
      title="预览结果"
      size="small"
      extra={
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={onRunPreview}
          loading={loading}
        >
          运行预览
        </Button>
      }
      style={{ height: '100%' }}
      bodyStyle={{ padding: '12px', height: 'calc(100% - 46px)', overflow: 'auto' }}
    >
      {warnings && warnings.length > 0 && (
        <Alert
          type="warning"
          message={
            <Space direction="vertical" size={0}>
              {warnings.map((w, i) => (
                <span key={i}>{w}</span>
              ))}
            </Space>
          }
          style={{ marginBottom: 12 }}
          closable
        />
      )}

      {data.length === 0 && !loading ? (
        <div
          style={{
            textAlign: 'center',
            padding: '40px 0',
            color: '#8c8c8c',
          }}
        >
          点击"运行预览"查看映射转换结果
        </div>
      ) : (
        <Table
          columns={tableColumns}
          dataSource={data.map((row, index) => ({ ...row, _key: index }))}
          rowKey="_key"
          size="small"
          loading={loading}
          pagination={false}
          scroll={{ x: 'max-content' }}
        />
      )}
    </Card>
  );
};

export default PreviewPanel;
