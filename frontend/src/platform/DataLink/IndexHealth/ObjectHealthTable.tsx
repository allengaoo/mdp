/**
 * ObjectHealthTable - Main table showing object health status
 */
import React from 'react';
import { Table, Badge, Button, Space, Progress, Tooltip, Typography } from 'antd';
import {
  ReloadOutlined,
  EyeOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { IObjectHealthSummary, HealthStatus } from '../../../api/v3/health';
import { formatLag, getStatusColor } from '../../../api/v3/health';

const { Text } = Typography;

interface ObjectHealthTableProps {
  data: IObjectHealthSummary[];
  loading: boolean;
  onViewDetail: (record: IObjectHealthSummary) => void;
  onReindex: (objectDefId: string) => void;
  reindexing: string | null;
}

const ObjectHealthTable: React.FC<ObjectHealthTableProps> = ({
  data,
  loading,
  onViewDetail,
  onReindex,
  reindexing,
}) => {
  const getStatusBadge = (status: HealthStatus) => {
    const statusMap = {
      HEALTHY: { status: 'success' as const, text: '健康' },
      DEGRADED: { status: 'warning' as const, text: '降级' },
      FAILED: { status: 'error' as const, text: '失败' },
    };
    const config = statusMap[status] || { status: 'default' as const, text: status };
    return <Badge status={config.status} text={config.text} />;
  };

  const columns: ColumnsType<IObjectHealthSummary> = [
    {
      title: '对象类型',
      dataIndex: 'object_def_id',
      key: 'object',
      render: (id: string, record) => (
        <Space>
          <DatabaseOutlined style={{ color: '#1890ff' }} />
          <div>
            <div style={{ fontWeight: 500 }}>
              {record.object_name || id.substring(0, 8)}
            </div>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {id.substring(0, 16)}...
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: HealthStatus) => getStatusBadge(status),
      filters: [
        { text: '健康', value: 'HEALTHY' },
        { text: '降级', value: 'DEGRADED' },
        { text: '失败', value: 'FAILED' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      width: 150,
      render: (rate: number) => (
        <Progress
          percent={rate}
          size="small"
          status={rate >= 95 ? 'success' : rate >= 80 ? 'normal' : 'exception'}
          format={(p) => `${p?.toFixed(1)}%`}
        />
      ),
      sorter: (a, b) => a.success_rate - b.success_rate,
    },
    {
      title: '处理/索引',
      key: 'rows',
      width: 120,
      render: (_, record) => (
        <Tooltip title={`处理: ${record.rows_processed}, 索引: ${record.rows_indexed}`}>
          <span>
            {record.rows_indexed} / {record.rows_processed}
          </span>
        </Tooltip>
      ),
    },
    {
      title: '最后运行',
      dataIndex: 'lag_seconds',
      key: 'lag',
      width: 100,
      render: (lag: number | null) => (
        <Text type={lag && lag > 86400 ? 'danger' : 'secondary'}>
          {formatLag(lag)}
        </Text>
      ),
      sorter: (a, b) => (a.lag_seconds || 0) - (b.lag_seconds || 0),
    },
    {
      title: 'AI 延迟',
      key: 'ai_latency',
      width: 100,
      render: (_, record) => {
        const latency = record.metrics?.ai_latency_avg_ms;
        if (!latency) return <Text type="secondary">N/A</Text>;
        return (
          <Text type={latency > 500 ? 'warning' : undefined}>
            {latency.toFixed(0)} ms
          </Text>
        );
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => onViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="重新索引">
            <Button
              type="text"
              icon={<ReloadOutlined />}
              loading={reindexing === record.object_def_id}
              onClick={() => onReindex(record.object_def_id)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="object_def_id"
      loading={loading}
      pagination={{ pageSize: 10 }}
      size="middle"
    />
  );
};

export default ObjectHealthTable;
