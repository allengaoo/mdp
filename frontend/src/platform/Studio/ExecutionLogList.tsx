/**
 * Execution Log List View component.
 * Connected to real backend API for execution logs.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Table, Tag, Button, Space, Empty, Spin, message, Tooltip, Select } from 'antd';
import { ReloadOutlined, LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { fetchExecutionLogs, IExecutionLog } from '../../api/ontology';

interface ExecutionLogData {
  id: string;
  time: string;
  actionName: string;
  actionId: string;
  status: 'SUCCESS' | 'FAILED';
  duration: number;
  errorMessage?: string | null;
  sourceObjectId?: string | null;
}

const ExecutionLogList: React.FC = () => {
  const [logs, setLogs] = useState<ExecutionLogData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  // Load execution logs
  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchExecutionLogs({
        status: statusFilter,
        limit: 100,
      });
      
      // Transform API response to component data format
      const transformedData: ExecutionLogData[] = data.map((log) => ({
        id: log.id,
        time: log.created_at || new Date().toISOString(),
        actionName: log.action_name,
        actionId: log.action_id || '',
        status: log.status,
        duration: log.duration_ms,
        errorMessage: log.error_message,
        sourceObjectId: null, // API doesn't return this in the interface
      }));
      
      setLogs(transformedData);
    } catch (error: any) {
      console.error('Failed to load execution logs:', error);
      message.error('加载执行日志失败');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  // Format datetime for display
  const formatDateTime = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const columns: ColumnsType<ExecutionLogData> = [
    {
      title: '执行时间',
      dataIndex: 'time',
      key: 'time',
      width: 180,
      render: (time: string) => formatDateTime(time),
      sorter: (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: '行为名称',
      dataIndex: 'actionName',
      key: 'actionName',
      width: 200,
      ellipsis: true,
      render: (name: string, record) => (
        <Tooltip title={record.actionId}>
          <span style={{ fontWeight: 500 }}>{name}</span>
        </Tooltip>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag
          icon={status === 'SUCCESS' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          color={status === 'SUCCESS' ? 'success' : 'error'}
          style={{ borderRadius: 4 }}
        >
          {status === 'SUCCESS' ? '成功' : '失败'}
        </Tag>
      ),
      filters: [
        { text: '成功', value: 'SUCCESS' },
        { text: '失败', value: 'FAILED' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '执行耗时',
      dataIndex: 'duration',
      key: 'duration',
      width: 120,
      render: (duration: number) => (
        <span style={{ color: duration > 1000 ? '#f59e0b' : '#10b981' }}>
          {duration}ms
        </span>
      ),
      sorter: (a, b) => a.duration - b.duration,
    },
    {
      title: '错误信息',
      dataIndex: 'errorMessage',
      key: 'errorMessage',
      ellipsis: true,
      render: (msg: string | null | undefined) =>
        msg ? (
          <Tooltip title={msg}>
            <span style={{ color: '#ef4444' }}>{msg}</span>
          </Tooltip>
        ) : (
          <span style={{ color: '#9ca3af' }}>-</span>
        ),
    },
  ];

  return (
    <div style={{ background: '#fff', padding: '24px', borderRadius: 8 }}>
      {/* Header with filters and refresh */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <span style={{ fontWeight: 500 }}>状态筛选:</span>
          <Select
            style={{ width: 120 }}
            placeholder="全部"
            allowClear
            value={statusFilter}
            onChange={setStatusFilter}
          >
            <Select.Option value="SUCCESS">成功</Select.Option>
            <Select.Option value="FAILED">失败</Select.Option>
          </Select>
        </Space>
        <Space>
          <span style={{ color: '#6b7280', fontSize: 13 }}>
            共 {logs.length} 条记录
          </span>
          <Button
            icon={loading ? <LoadingOutlined /> : <ReloadOutlined />}
            onClick={loadLogs}
            disabled={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* Table */}
      {loading && logs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 32 }} spin />} />
          <div style={{ marginTop: 16, color: '#6b7280' }}>加载执行日志...</div>
        </div>
      ) : logs.length === 0 ? (
        <Empty
          description="暂无执行日志"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          style={{ padding: '60px 0' }}
        />
      ) : (
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 800 }}
          loading={loading}
          size="middle"
        />
      )}
    </div>
  );
};

export default ExecutionLogList;
