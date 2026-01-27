/**
 * Shared Property List View component.
 * 
 * @note V3 Migration: Now uses project-scoped V3 API via fetchProjectSharedProperties
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { ISharedProperty } from '../../api/ontology';
import { fetchProjectSharedProperties } from '../../api/v3/ontology';
import { adaptSharedPropertiesToV1 } from '../../api/v3/adapters';
import apiClient from '../../api/axios';
import SharedPropertyModal from './SharedPropertyModal';

// Use ISharedProperty from api/ontology.ts
interface SharedPropertyData extends ISharedProperty {
  // V3 may not have formatter, make it optional
  formatter?: string | null;
  created_at?: string;
}

const SharedPropertyList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<SharedPropertyData[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [selectedProperty, setSelectedProperty] = useState<SharedPropertyData | null>(null);

  // Fetch shared properties from API (now using project-scoped V3 API)
  const loadSharedProperties = async () => {
    if (!projectId) {
      message.error('Project ID is required');
      return;
    }
    
    try {
      setLoading(true);
      // Use the project-scoped V3 API to get shared properties used by this project
      const v3Properties = await fetchProjectSharedProperties(projectId);
      const properties = adaptSharedPropertiesToV1(v3Properties);
      setData(properties as SharedPropertyData[]);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch shared properties');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSharedProperties();
  }, [projectId]);

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
      title: 'Delete Shared Property',
      content: (
        <div>
          <p>Are you sure you want to delete this shared property?</p>
          <p style={{ color: '#ff4d4f', marginTop: 8 }}>
            <strong>Warning:</strong> Deleting a Shared Property will remove the standard
            definition. Any Object Types currently using this property will be decoupled.
          </p>
        </div>
      ),
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          // TODO: Migrate to V3 delete API when available
          await apiClient.delete(`/meta/shared-properties/${record.id}`);
          message.success('Shared property deleted successfully');
          loadSharedProperties();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete shared property');
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
      title: 'Name',
      dataIndex: 'display_name',
      key: 'display_name',
      width: 150,
    },
    {
      title: 'API Name',
      dataIndex: 'api_name',
      key: 'api_name',
      width: 150,
      render: (text) => <Tag color="purple">{text}</Tag>,
    },
    {
      title: 'Data Type',
      dataIndex: 'data_type',
      key: 'data_type',
      width: 120,
    },
    {
      title: 'Formatter',
      dataIndex: 'formatter',
      key: 'formatter',
      width: 150,
      render: (text) => {
        if (!text) return <Tag>-</Tag>;
        // Check if it's JSON (constraints)
        try {
          const parsed = JSON.parse(text);
          return <Tag color="cyan">Constraints</Tag>;
        } catch {
          return <Tag>{text}</Tag>;
        }
      },
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => text || '-',
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDelete(record)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ background: '#fff', padding: '24px', borderRadius: 8 }}>
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreate}
        >
          Create Standard Property
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 1200 }}
      />
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

export default SharedPropertyList;

