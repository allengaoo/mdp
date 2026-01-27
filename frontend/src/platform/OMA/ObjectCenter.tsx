/**
 * Object Center Page - MDP Platform V3.1
 * 
 * Displays all object type definitions with statistics.
 * Provides search, filtering, and CRUD operations.
 */
import React, { useState, useEffect, useMemo } from 'react';
import {
  Table,
  Button,
  Input,
  Space,
  Tag,
  message,
  Spin,
  Alert,
  Typography,
  Avatar,
  Tooltip,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  CodeSandboxOutlined,
  FileTextOutlined,
  CalendarOutlined,
  PictureOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { fetchObjectDefsWithStats, IV3ObjectDefWithStats } from '../../api/v3/objects';

const { Title, Text } = Typography;

// Stereotype to icon mapping
const stereotypeIcons: Record<string, React.ReactNode> = {
  ENTITY: <CodeSandboxOutlined />,
  EVENT: <CalendarOutlined />,
  DOCUMENT: <FileTextOutlined />,
  MEDIA: <PictureOutlined />,
  METRIC: <BarChartOutlined />,
};

// Status to color mapping
const statusColors: Record<string, string> = {
  DRAFT: 'default',
  PUBLISHED: 'success',
  DEPRECATED: 'warning',
};

const ObjectCenter: React.FC = () => {
  const [data, setData] = useState<IV3ObjectDefWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');

  // Load data from API
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const objects = await fetchObjectDefsWithStats();
      setData(objects);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '加载对象类型列表失败';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter data by search text
  const filteredData = useMemo(() => {
    if (!searchText.trim()) {
      return data;
    }
    const lowerSearch = searchText.toLowerCase();
    return data.filter(
      (item) =>
        item.api_name.toLowerCase().includes(lowerSearch) ||
        (item.display_name && item.display_name.toLowerCase().includes(lowerSearch)) ||
        (item.description && item.description.toLowerCase().includes(lowerSearch))
    );
  }, [data, searchText]);

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  // Handle create new object type
  const handleCreate = () => {
    message.info('新建对象类型功能开发中...');
  };

  // Handle edit
  const handleEdit = (record: IV3ObjectDefWithStats) => {
    message.info(`编辑对象类型: ${record.api_name}`);
  };

  // Handle delete
  const handleDelete = (record: IV3ObjectDefWithStats) => {
    message.info(`删除对象类型: ${record.api_name}`);
  };

  // Table columns definition
  const columns: ColumnsType<IV3ObjectDefWithStats> = [
    {
      title: '对象类型',
      key: 'name',
      width: 280,
      render: (_, record) => (
        <Space>
          <Avatar
            size="small"
            style={{ backgroundColor: '#1890ff' }}
            icon={stereotypeIcons[record.stereotype] || <CodeSandboxOutlined />}
          />
          <div>
            <div style={{ fontWeight: 500 }}>
              {record.display_name || record.api_name}
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.api_name}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'stereotype',
      key: 'stereotype',
      width: 100,
      render: (stereotype: string) => (
        <Tag>{stereotype}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={statusColors[status] || 'default'}>
          {status}
        </Tag>
      ),
    },
    {
      title: '属性数',
      dataIndex: 'property_count',
      key: 'property_count',
      width: 80,
      align: 'center',
      render: (count: number) => (
        <Tooltip title="绑定的属性数量">
          <span>{count}</span>
        </Tooltip>
      ),
    },
    {
      title: '实例数',
      dataIndex: 'instance_count',
      key: 'instance_count',
      width: 80,
      align: 'center',
      render: (count: number) => (
        <Tooltip title="数据实例数量">
          <span>{count}</span>
        </Tooltip>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 160,
      render: (date: string | null) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatDate(date)}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除该对象类型?"
            description="删除后无法恢复"
            onConfirm={() => handleDelete(record)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="删除">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Loading state
  if (loading && data.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#8c8c8c' }}>加载对象类型列表...</div>
      </div>
    );
  }

  // Error state
  if (error && data.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ margin: 0 }}>
            对象中心 (Object Center)
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
            对象中心 (Object Center)
          </Title>
          <Text type="secondary">
            管理和浏览所有对象类型定义
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          新建对象类型
        </Button>
      </div>

      {/* Search & Actions Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <Input
          placeholder="搜索对象类型名称..."
          prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
        <Space>
          <Text type="secondary">
            共 {filteredData.length} 个对象类型
          </Text>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={filteredData}
        rowKey="id"
        loading={loading}
        pagination={{
          defaultPageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        size="middle"
        style={{
          background: '#fff',
          borderRadius: 8,
        }}
      />
    </div>
  );
};

export default ObjectCenter;
