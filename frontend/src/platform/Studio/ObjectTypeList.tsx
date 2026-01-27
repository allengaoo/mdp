/**
 * Object Type List View component.
 * 
 * @note V3 Migration: Now uses V3 project-scoped API for correct filtering.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { fetchProjectObjectTypes } from '../../api/v3/ontology';
import { IV3ObjectTypeFull } from '../../api/v3/types';
import apiClient from '../../api/axios';
import ObjectTypeWizard from './ObjectTypeWizard';
import ObjectTypeEditor from './ObjectTypeEditor';

// Use V3 ObjectTypeFull interface
interface ObjectTypeData extends IV3ObjectTypeFull {
  // Add any local extensions if needed
}

const ObjectTypeList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<ObjectTypeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardVisible, setWizardVisible] = useState(false);
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedObjectType, setSelectedObjectType] = useState<ObjectTypeData | null>(null);

  // Fetch object types from API (using V3 project-scoped endpoint)
  const loadObjectTypes = async () => {
    if (!projectId) {
      setData([]);
      return;
    }
    
    try {
      setLoading(true);
      // Use V3 project-scoped API to get only object types bound to this project
      const objectTypes = await fetchProjectObjectTypes(projectId);
      setData(objectTypes as ObjectTypeData[]);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch object types');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadObjectTypes();
  }, [projectId]);

  // Handle create success
  const handleCreateSuccess = () => {
    loadObjectTypes();
  };

  // Handle edit
  const handleEdit = (record: ObjectTypeData) => {
    setSelectedObjectType(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    loadObjectTypes();
  };

  // Handle delete
  const handleDelete = (record: ObjectTypeData) => {
    Modal.confirm({
      title: 'Delete Object Type',
      content: (
        <div>
          <p>Are you sure you want to delete this object type?</p>
          <p style={{ color: '#ff4d4f', marginTop: 8 }}>
            <strong>Warning:</strong> This will delete the Ontology definition but will{' '}
            <strong>NOT</strong> delete the underlying raw data. All associated Links and Actions may
            break.
          </p>
        </div>
      ),
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          // TODO: Migrate to V3 delete API when available
          await apiClient.delete(`/meta/object-types/${record.id}`);
          message.success('Object type deleted successfully');
          loadObjectTypes();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete object type');
        }
      },
    });
  };

  const columns: ColumnsType<ObjectTypeData> = [
    {
      title: 'Name',
      dataIndex: 'display_name',
      key: 'display_name',
      width: 200,
    },
    {
      title: 'API Name',
      dataIndex: 'api_name',
      key: 'api_name',
      width: 150,
      render: (text) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Last Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (text) => (text ? new Date(text).toLocaleString() : '-'),
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
          onClick={() => setWizardVisible(true)}
        >
          Create Object Type
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 1000 }}
      />
      <ObjectTypeWizard
        visible={wizardVisible}
        onCancel={() => setWizardVisible(false)}
        onSuccess={handleCreateSuccess}
      />
      <ObjectTypeEditor
        visible={editorVisible}
        objectType={selectedObjectType}
        onCancel={() => {
          setEditorVisible(false);
          setSelectedObjectType(null);
        }}
        onSuccess={handleEditSuccess}
      />
    </div>
  );
};

export default ObjectTypeList;

