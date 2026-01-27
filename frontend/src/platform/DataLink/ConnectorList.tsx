/**
 * Connector List Page - MDP Platform V3.1
 * 
 * Displays all data connections in a card grid layout.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Button,
  Space,
  Card,
  Row,
  Col,
  Badge,
  Spin,
  Alert,
  Empty,
  message,
  Popconfirm,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  ReloadOutlined,
  SettingOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import {
  fetchConnectors,
  deleteConnector,
  testExistingConnection,
  IConnectionSummary,
  ConnectorType,
} from '../../api/v3/connectors';
import { CONNECTOR_REGISTRY, getSafeConfigSummary } from './ConnectorConfigRegistry';

const { Title, Text } = Typography;

// Status badge mapping
const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
  ACTIVE: { color: 'success', icon: <CheckCircleOutlined />, text: '正常' },
  ERROR: { color: 'error', icon: <CloseCircleOutlined />, text: '错误' },
  TESTING: { color: 'processing', icon: <ClockCircleOutlined />, text: '测试中' },
};

/**
 * Connector Card Component
 */
interface ConnectorCardProps {
  connector: IConnectionSummary;
  onTest: (id: string) => void;
  onDelete: (id: string) => void;
  testing: boolean;
}

const ConnectorCard: React.FC<ConnectorCardProps> = ({
  connector,
  onTest,
  onDelete,
  testing,
}) => {
  const navigate = useNavigate();
  const def = CONNECTOR_REGISTRY[connector.conn_type as ConnectorType];
  const status = statusConfig[connector.status] || statusConfig.ACTIVE;
  const IconComponent = def?.icon;

  const handleClick = () => {
    navigate(`/data/connectors/${connector.id}`);
  };

  return (
    <Card
      hoverable
      onClick={handleClick}
      style={{ height: '100%' }}
      actions={[
        <Tooltip title="测试连接" key="test">
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            loading={testing}
            onClick={(e) => {
              e.stopPropagation();
              onTest(connector.id);
            }}
          />
        </Tooltip>,
        <Tooltip title="设置" key="settings">
          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/data/connectors/${connector.id}`);
            }}
          />
        </Tooltip>,
        <Popconfirm
          key="delete"
          title="确定删除此连接器？"
          description="关联的同步任务也需要先删除"
          onConfirm={(e) => {
            e?.stopPropagation();
            onDelete(connector.id);
          }}
          onCancel={(e) => e?.stopPropagation()}
          okText="删除"
          cancelText="取消"
        >
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => e.stopPropagation()}
            />
          </Tooltip>
        </Popconfirm>,
      ]}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
        {/* Icon */}
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: 8,
            background: def ? `${def.color}15` : '#f5f5f5',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24,
            color: def?.color || '#8c8c8c',
            flexShrink: 0,
          }}
        >
          {IconComponent && <IconComponent />}
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Text strong style={{ fontSize: 16 }}>
              {connector.name}
            </Text>
            <Badge
              status={status.color as any}
              text={
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {status.text}
                </Text>
              }
            />
          </div>

          <div style={{ marginBottom: 8 }}>
            <Text
              type="secondary"
              style={{
                fontSize: 12,
                padding: '2px 8px',
                background: def ? `${def.color}10` : '#f5f5f5',
                borderRadius: 4,
                color: def?.color,
              }}
            >
              {def?.label || connector.conn_type}
            </Text>
          </div>

          {connector.last_tested_at && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              上次测试: {new Date(connector.last_tested_at).toLocaleString()}
            </Text>
          )}
        </div>
      </div>
    </Card>
  );
};

/**
 * Main Connector List Component
 */
const ConnectorList: React.FC = () => {
  const navigate = useNavigate();
  const [connectors, setConnectors] = useState<IConnectionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingIds, setTestingIds] = useState<Set<string>>(new Set());

  // Load connectors
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchConnectors();
      setConnectors(data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '加载连接器列表失败';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Test connection
  const handleTest = async (id: string) => {
    setTestingIds((prev) => new Set(prev).add(id));
    try {
      const result = await testExistingConnection(id);
      if (result.success) {
        message.success(`连接测试成功 (${result.latency_ms}ms)`);
      } else {
        message.error(`连接测试失败: ${result.message}`);
      }
      // Reload to update status
      await loadData();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '测试失败');
    } finally {
      setTestingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  // Delete connection
  const handleDelete = async (id: string) => {
    try {
      await deleteConnector(id);
      message.success('删除成功');
      await loadData();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '删除失败');
    }
  };

  // Loading state
  if (loading && connectors.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#8c8c8c' }}>加载连接器...</div>
      </div>
    );
  }

  // Error state
  if (error && connectors.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ margin: 0 }}>
            连接器管理 (Connector Management)
          </Title>
        </div>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadData}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 24,
        }}
      >
        <div>
          <Title level={4} style={{ margin: 0 }}>
            连接器管理 (Connector Management)
          </Title>
          <Text type="secondary">
            管理外部数据源连接，配置数据同步任务
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/data/connectors/new')}
          >
            新建连接器
          </Button>
        </Space>
      </div>

      {/* Empty state */}
      {connectors.length === 0 ? (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无连接器"
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/data/connectors/new')}
            >
              创建第一个连接器
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {connectors.map((connector) => (
            <Col key={connector.id} xs={24} sm={12} lg={8} xl={6}>
              <ConnectorCard
                connector={connector}
                onTest={handleTest}
                onDelete={handleDelete}
                testing={testingIds.has(connector.id)}
              />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default ConnectorList;
