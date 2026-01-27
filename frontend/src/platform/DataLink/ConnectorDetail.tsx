/**
 * Connector Detail Page - MDP Platform V3.1
 * 
 * Dashboard for a single connector with tabs:
 * - Overview: Connection info & recent activity
 * - Explorer: Browse source tables (Magritte-like)
 * - Sync Jobs: Manage sync job definitions
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Typography,
  Tabs,
  Card,
  Button,
  Space,
  Descriptions,
  Badge,
  Table,
  Tree,
  Spin,
  Alert,
  Empty,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tag,
  Tooltip,
  Popconfirm,
  Drawer,
} from 'antd';
import type { DataNode } from 'antd/es/tree';
import type { ColumnsType } from 'antd/es/table';
import {
  ArrowLeftOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  TableOutlined,
  ColumnWidthOutlined,
} from '@ant-design/icons';
import {
  fetchConnector,
  exploreSource,
  fetchSyncJobs,
  createSyncJob,
  deleteSyncJob,
  runSyncJob,
  fetchSyncJobLogs,
  IConnectionRead,
  ISourceExplorerResponse,
  ISourceTableInfo,
  ISyncJobWithConnection,
  ISyncJobCreate,
  ISyncRunLogWithJob,
  ConnectorType,
} from '../../api/v3/connectors';
import { CONNECTOR_REGISTRY, getSafeConfigSummary } from './ConnectorConfigRegistry';

const { Title, Text, Paragraph } = Typography;

// Status configurations
const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
  ACTIVE: { color: 'success', icon: <CheckCircleOutlined />, text: '正常' },
  ERROR: { color: 'error', icon: <CloseCircleOutlined />, text: '错误' },
  SUCCESS: { color: 'success', icon: <CheckCircleOutlined />, text: '成功' },
  FAILED: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
  RUNNING: { color: 'processing', icon: <ClockCircleOutlined />, text: '运行中' },
};

// ==========================================
// Overview Tab
// ==========================================

interface OverviewTabProps {
  connector: IConnectionRead;
  connectorDef: any;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ connector, connectorDef }) => {
  const status = statusConfig[connector.status] || statusConfig.ACTIVE;
  const configSummary = getSafeConfigSummary(connector.conn_type, connector.config_json);

  return (
    <div>
      <Card title="连接信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="连接类型">
            <Tag color={connectorDef?.color}>{connectorDef?.label || connector.conn_type}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Badge status={status.color as any} text={status.text} />
          </Descriptions.Item>
          <Descriptions.Item label="连接地址">{configSummary}</Descriptions.Item>
          <Descriptions.Item label="上次测试">
            {connector.last_tested_at
              ? new Date(connector.last_tested_at).toLocaleString()
              : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {connector.created_at ? new Date(connector.created_at).toLocaleString() : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {connector.updated_at ? new Date(connector.updated_at).toLocaleString() : '-'}
          </Descriptions.Item>
        </Descriptions>
        {connector.error_message && (
          <Alert
            type="error"
            message="连接错误"
            description={connector.error_message}
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>
    </div>
  );
};

// ==========================================
// Explorer Tab
// ==========================================

interface ExplorerTabProps {
  connectorId: string;
  connectorType: ConnectorType;
  onCreateJob: (tableInfo: ISourceTableInfo) => void;
}

const ExplorerTab: React.FC<ExplorerTabProps> = ({ connectorId, connectorType, onCreateJob }) => {
  const [loading, setLoading] = useState(true);
  const [explorerData, setExplorerData] = useState<ISourceExplorerResponse | null>(null);
  const [selectedTable, setSelectedTable] = useState<ISourceTableInfo | null>(null);

  const loadExplorer = useCallback(async () => {
    try {
      setLoading(true);
      const data = await exploreSource(connectorId);
      setExplorerData(data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '探索数据源失败');
    } finally {
      setLoading(false);
    }
  }, [connectorId]);

  useEffect(() => {
    loadExplorer();
  }, [loadExplorer]);

  // Build tree data
  const treeData: DataNode[] = explorerData?.tables.map((table) => ({
    key: table.name,
    title: table.name,
    icon: <TableOutlined />,
    children: table.columns?.map((col) => ({
      key: `${table.name}.${col.name}`,
      title: (
        <span>
          {col.name} <Text type="secondary" style={{ fontSize: 12 }}>({col.type})</Text>
        </span>
      ),
      icon: <ColumnWidthOutlined />,
      isLeaf: true,
    })),
  })) || [];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>正在探索数据源...</div>
      </div>
    );
  }

  if (explorerData?.error) {
    return (
      <Alert
        type="error"
        message="探索失败"
        description={explorerData.error}
        showIcon
        action={
          <Button size="small" onClick={loadExplorer}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      {/* Left: Table Tree */}
      <Card
        title={`数据表 (${explorerData?.tables.length || 0})`}
        style={{ flex: 1, minWidth: 300 }}
        extra={
          <Button size="small" icon={<ReloadOutlined />} onClick={loadExplorer}>
            刷新
          </Button>
        }
      >
        {treeData.length > 0 ? (
          <Tree
            showIcon
            defaultExpandAll
            treeData={treeData}
            onSelect={(keys, { node }) => {
              if (!node.isLeaf) {
                const table = explorerData?.tables.find((t) => t.name === node.key);
                setSelectedTable(table || null);
              }
            }}
          />
        ) : (
          <Empty description="暂无数据表" />
        )}
      </Card>

      {/* Right: Table Detail & Actions */}
      <Card title="表详情" style={{ flex: 1 }}>
        {selectedTable ? (
          <div>
            <Descriptions column={1}>
              <Descriptions.Item label="表名">{selectedTable.name}</Descriptions.Item>
              <Descriptions.Item label="列数">
                {selectedTable.columns?.length || 0}
              </Descriptions.Item>
            </Descriptions>

            <Title level={5} style={{ marginTop: 16 }}>
              列信息
            </Title>
            <Table
              size="small"
              dataSource={selectedTable.columns || []}
              columns={[
                { title: '列名', dataIndex: 'name', key: 'name' },
                { title: '类型', dataIndex: 'type', key: 'type' },
                {
                  title: '可空',
                  dataIndex: 'nullable',
                  key: 'nullable',
                  render: (v) => (v ? '是' : '否'),
                },
              ]}
              rowKey="name"
              pagination={false}
            />

            <Button
              type="primary"
              icon={<PlusOutlined />}
              style={{ marginTop: 16 }}
              onClick={() => onCreateJob(selectedTable)}
            >
              创建同步任务
            </Button>
          </div>
        ) : (
          <Empty description="选择左侧表查看详情" />
        )}
      </Card>
    </div>
  );
};

// ==========================================
// Sync Jobs Tab
// ==========================================

interface SyncJobsTabProps {
  connectorId: string;
  onCreateJob: () => void;
}

const SyncJobsTab: React.FC<SyncJobsTabProps> = ({ connectorId, onCreateJob }) => {
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState<ISyncJobWithConnection[]>([]);
  const [runningJobs, setRunningJobs] = useState<Set<string>>(new Set());
  const [logsDrawer, setLogsDrawer] = useState<{ visible: boolean; jobId: string | null }>({
    visible: false,
    jobId: null,
  });
  const [logs, setLogs] = useState<ISyncRunLogWithJob[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  const loadJobs = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchSyncJobs(connectorId);
      setJobs(data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '加载同步任务失败');
    } finally {
      setLoading(false);
    }
  }, [connectorId]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  const handleRun = async (jobId: string) => {
    setRunningJobs((prev) => new Set(prev).add(jobId));
    try {
      await runSyncJob(jobId);
      message.success('同步任务已启动');
      await loadJobs();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '启动失败');
    } finally {
      setRunningJobs((prev) => {
        const next = new Set(prev);
        next.delete(jobId);
        return next;
      });
    }
  };

  const handleDelete = async (jobId: string) => {
    try {
      await deleteSyncJob(jobId);
      message.success('删除成功');
      await loadJobs();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '删除失败');
    }
  };

  const handleShowLogs = async (jobId: string) => {
    setLogsDrawer({ visible: true, jobId });
    setLogsLoading(true);
    try {
      const data = await fetchSyncJobLogs(jobId);
      setLogs(data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '加载日志失败');
    } finally {
      setLogsLoading(false);
    }
  };

  const columns: ColumnsType<ISyncJobWithConnection> = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      render: (name) => <Text strong>{name}</Text>,
    },
    {
      title: '源表',
      key: 'source',
      render: (_, record) => (
        <Text code>{record.source_config.table || record.source_config.query?.slice(0, 30)}</Text>
      ),
    },
    {
      title: '目标表',
      dataIndex: 'target_table',
      key: 'target_table',
      render: (v) => <Text code>{v}</Text>,
    },
    {
      title: '模式',
      dataIndex: 'sync_mode',
      key: 'sync_mode',
      render: (v) => (
        <Tag color={v === 'FULL_OVERWRITE' ? 'blue' : 'green'}>
          {v === 'FULL_OVERWRITE' ? '全量覆盖' : '增量追加'}
        </Tag>
      ),
    },
    {
      title: '上次执行',
      key: 'last_run',
      render: (_, record) => {
        if (!record.last_run_status) return '-';
        const status = statusConfig[record.last_run_status];
        return (
          <Space>
            <Badge status={status?.color as any} text={status?.text} />
            {record.rows_synced !== null && (
              <Text type="secondary">({record.rows_synced} 行)</Text>
            )}
          </Space>
        );
      },
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="立即执行">
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              loading={runningJobs.has(record.id)}
              onClick={() => handleRun(record.id)}
            />
          </Tooltip>
          <Tooltip title="执行日志">
            <Button
              type="text"
              icon={<ClockCircleOutlined />}
              onClick={() => handleShowLogs(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除此同步任务？"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const logColumns: ColumnsType<ISyncRunLogWithJob> = [
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (v) => new Date(v).toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (v) => {
        const s = statusConfig[v];
        return <Badge status={s?.color as any} text={s?.text} />;
      },
    },
    {
      title: '耗时',
      dataIndex: 'duration_ms',
      key: 'duration_ms',
      render: (v) => (v ? `${v}ms` : '-'),
    },
    {
      title: '行数',
      dataIndex: 'rows_affected',
      key: 'rows_affected',
      render: (v) => (v !== null ? v : '-'),
    },
    {
      title: '触发方式',
      dataIndex: 'triggered_by',
      key: 'triggered_by',
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Text type="secondary">管理此连接器的数据同步任务</Text>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadJobs}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={onCreateJob}>
            新建同步任务
          </Button>
        </Space>
      </div>

      <Table
        dataSource={jobs}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={false}
        locale={{ emptyText: '暂无同步任务' }}
      />

      {/* Logs Drawer */}
      <Drawer
        title="执行日志"
        placement="right"
        width={600}
        open={logsDrawer.visible}
        onClose={() => setLogsDrawer({ visible: false, jobId: null })}
      >
        <Table
          dataSource={logs}
          columns={logColumns}
          rowKey="id"
          loading={logsLoading}
          size="small"
          pagination={{ pageSize: 10 }}
          expandable={{
            expandedRowRender: (record) =>
              record.message ? (
                <pre style={{ fontSize: 12, background: '#f5f5f5', padding: 8, margin: 0 }}>
                  {record.message}
                </pre>
              ) : null,
            rowExpandable: (record) => !!record.message,
          }}
        />
      </Drawer>
    </div>
  );
};

// ==========================================
// Main Component
// ==========================================

const ConnectorDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const [loading, setLoading] = useState(true);
  const [connector, setConnector] = useState<IConnectionRead | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [createJobModal, setCreateJobModal] = useState<{
    visible: boolean;
    tableInfo?: ISourceTableInfo;
  }>({ visible: false });
  const [form] = Form.useForm();
  const [creating, setCreating] = useState(false);

  // Load connector
  const loadConnector = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await fetchConnector(id);
      setConnector(data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '加载连接器失败');
      navigate('/data/connectors');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    loadConnector();
  }, [loadConnector]);

  // Open create job modal
  const openCreateJobModal = (tableInfo?: ISourceTableInfo) => {
    form.resetFields();
    if (tableInfo) {
      form.setFieldsValue({
        name: `Sync ${tableInfo.name}`,
        source_config: { table: tableInfo.name },
        target_table: `raw_${tableInfo.name}`,
      });
    }
    setCreateJobModal({ visible: true, tableInfo });
  };

  // Create sync job
  const handleCreateJob = async () => {
    try {
      await form.validateFields();
      setCreating(true);

      const values = form.getFieldsValue();
      const payload: ISyncJobCreate = {
        connection_id: id!,
        name: values.name,
        source_config: values.source_config,
        target_table: values.target_table,
        sync_mode: values.sync_mode || 'FULL_OVERWRITE',
      };

      await createSyncJob(payload);
      message.success('同步任务创建成功');
      setCreateJobModal({ visible: false });
      setActiveTab('sync-jobs');
    } catch (err: any) {
      if (err.errorFields) {
        message.error('请填写所有必填项');
      } else {
        message.error(err.response?.data?.detail || '创建失败');
      }
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!connector) {
    return <Alert type="error" message="连接器不存在" />;
  }

  const connectorDef = CONNECTOR_REGISTRY[connector.conn_type as ConnectorType];

  const tabItems = [
    {
      key: 'overview',
      label: '概览',
      children: <OverviewTab connector={connector} connectorDef={connectorDef} />,
    },
    {
      key: 'explorer',
      label: '数据探索',
      children: (
        <ExplorerTab
          connectorId={id!}
          connectorType={connector.conn_type}
          onCreateJob={openCreateJobModal}
        />
      ),
    },
    {
      key: 'sync-jobs',
      label: '同步任务',
      children: (
        <SyncJobsTab connectorId={id!} onCreateJob={() => openCreateJobModal()} />
      ),
    },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/data/connectors')}
          style={{ marginBottom: 16 }}
        >
          返回列表
        </Button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 8,
                background: connectorDef ? `${connectorDef.color}15` : '#f5f5f5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 24,
                color: connectorDef?.color || '#8c8c8c',
              }}
            >
              {connectorDef && React.createElement(connectorDef.icon)}
            </div>
            <div>
              <Title level={4} style={{ margin: 0 }}>
                {connector.name}
              </Title>
              <Tag color={connectorDef?.color}>{connectorDef?.label || connector.conn_type}</Tag>
            </div>
          </div>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadConnector}>
              刷新
            </Button>
            <Button icon={<EditOutlined />} onClick={() => navigate(`/data/connectors/${id}/edit`)}>
              编辑
            </Button>
          </Space>
        </div>
      </div>

      {/* Tabs */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />

      {/* Create Job Modal */}
      <Modal
        title="创建同步任务"
        open={createJobModal.visible}
        onCancel={() => setCreateJobModal({ visible: false })}
        onOk={handleCreateJob}
        confirmLoading={creating}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="例如: Sync users table" />
          </Form.Item>
          <Form.Item
            name={['source_config', 'table']}
            label="源表名"
            rules={[{ required: true, message: '请输入源表名' }]}
          >
            <Input placeholder="例如: users" />
          </Form.Item>
          <Form.Item
            name="target_table"
            label="目标表名"
            rules={[{ required: true, message: '请输入目标表名' }]}
          >
            <Input placeholder="例如: raw_users" />
          </Form.Item>
          <Form.Item name="sync_mode" label="同步模式" initialValue="FULL_OVERWRITE">
            <Select
              options={[
                { label: '全量覆盖', value: 'FULL_OVERWRITE' },
                { label: '增量追加', value: 'INCREMENTAL' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ConnectorDetail;
