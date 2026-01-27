/**
 * Global Shared Property List View component.
 * 
 * Displays all shared properties in the global registry (not project-scoped).
 * This is part of the Global Registry (全域资产库) for architects/admins.
 * 
 * @note Uses V3 API: GET /api/v3/ontology/properties (returns all global properties)
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Typography, Alert } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { ISharedProperty } from '../../api/ontology';
import { fetchSharedProperties, deleteSharedProperty } from '../../api/v3/ontology';
import { adaptSharedPropertiesToV1 } from '../../api/v3/adapters';
import SharedPropertyModal from '../Studio/SharedPropertyModal';

const { Title, Text } = Typography;

// Use ISharedProperty from api/ontology.ts
interface SharedPropertyData extends ISharedProperty {
  formatter?: string | null;
  created_at?: string;
}

const GlobalSharedPropertyList: React.FC = () => {
  const [data, setData] = useState<SharedPropertyData[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [selectedProperty, setSelectedProperty] = useState<SharedPropertyData | null>(null);

  // Fetch all shared properties from global API
  const loadSharedProperties = async () => {
    try {
      setLoading(true);
      // Use the global V3 API to get all shared properties
      const v3Properties = await fetchSharedProperties();
      const properties = adaptSharedPropertiesToV1(v3Properties);
      setData(properties as SharedPropertyData[]);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载公共属性失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSharedProperties();
  }, []);

  // Handle create
  const handleCreate = () => {
    setModalMode('create');
    setSelectedProperty(null);
    setModalVisible(true);
  };

  // Handle edit
  const handleEdit = (record: SharedPropertyData) => {
    setModalMode('edit');
    setSelectedProperty(record);
    setModalVisible(true);
  };

  // Handle delete
  const handleDelete = (record: SharedPropertyData) => {
    Modal.confirm({
      title: '删除公共属性',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>确定要删除公共属性 <strong>{record.display_name}</strong> 吗？</p>
          <Alert
            type="warning"
            showIcon
            message="全局影响警告"
            description="删除公共属性会影响所有使用该属性的对象类型。请先执行影响分析。"
            style={{ marginTop: 12 }}
          />
        </div>
      ),
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteSharedProperty(record.id);
          message.success('公共属性已删除');
          loadSharedProperties();
        } catch (error: any) {
          message.error(error.response?.data?.detail || '删除失败');
        }
      },
    });
  };

  // Handle modal success
  const handleModalSuccess = () => {
    loadSharedProperties();
  };

  const columns: ColumnsType<SharedPropertyData> = [
    {
      title: '显示名称',
      dataIndex: 'display_name',
      key: 'display_name',
      width: 150,
    },
    {
      title: 'API 名称',
      dataIndex: 'api_name',
      key: 'api_name',
      width: 150,
      render: (text) => <Tag color="purple">{text}</Tag>,
    },
    {
      title: '数据类型',
      dataIndex: 'data_type',
      key: 'data_type',
      width: 120,
      render: (text) => {
        const typeColors: Record<string, string> = {
          STRING: 'green',
          INT: 'blue',
          DOUBLE: 'cyan',
          BOOLEAN: 'orange',
          DATETIME: 'magenta',
          JSON: 'gold',
        };
        return <Tag color={typeColors[text] || 'default'}>{text}</Tag>;
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => text || <Text type="secondary">-</Text>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => {
        if (!text) return <Text type="secondary">-</Text>;
        return new Date(text).toLocaleString('zh-CN');
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0 }}>
          公共属性 (Shared Properties)
        </Title>
        <Text type="secondary">
          全局属性定义池，可被多个对象类型复用。修改将影响所有引用该属性的对象类型。
        </Text>
      </div>

      {/* Global Warning Banner */}
      <Alert
        message="全域资产库"
        description="您正在管理全局共享属性。此处的修改将影响所有使用这些属性的项目和对象类型。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      {/* Main Content */}
      <div style={{ background: '#fff', padding: '24px', borderRadius: 8 }}>
        <div style={{ marginBottom: 16, textAlign: 'right' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建公共属性
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{ 
            pageSize: 15,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1000 }}
        />
      </div>

      {/* Shared Property Modal (reused from Studio) */}
      <SharedPropertyModal
        visible={modalVisible}
        mode={modalMode}
        property={selectedProperty}
        onCancel={() => {
          setModalVisible(false);
          setSelectedProperty(null);
        }}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
};

export default GlobalSharedPropertyList;
