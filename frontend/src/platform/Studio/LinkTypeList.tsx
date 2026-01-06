/**
 * Link Type List View component.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import apiClient from '../../api/axios';
import LinkTypeWizard from './LinkTypeWizard';
import LinkTypeEditor from './LinkTypeEditor';

interface ObjectType {
  id: string;
  api_name: string;
  display_name: string;
}

interface LinkTypeData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  source_type_id: string;
  target_type_id: string;
  cardinality: string;
}

const LinkTypeList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<LinkTypeData[]>([]);
  const [objectTypes, setObjectTypes] = useState<ObjectType[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardVisible, setWizardVisible] = useState(false);
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedLinkType, setSelectedLinkType] = useState<LinkTypeData | null>(null);

  // Fetch link types from API
  const fetchLinkTypes = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/meta/link-types', {
        params: {
          limit: 100,
        },
      });
      setData(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch link types');
    } finally {
      setLoading(false);
    }
  };

  // Fetch object types for display
  const fetchObjectTypes = async () => {
    try {
      const response = await apiClient.get('/meta/object-types', {
        params: {
          limit: 100,
        },
      });
      setObjectTypes(response.data);
    } catch (error: any) {
      // Silently fail, use mock data
      console.error('Failed to fetch object types:', error);
    }
  };

  useEffect(() => {
    fetchLinkTypes();
    fetchObjectTypes();
  }, [projectId]);

  // Get object type display name
  const getObjectTypeName = (typeId: string): string => {
    const objType = objectTypes.find((ot) => ot.id === typeId);
    return objType ? objType.display_name : typeId;
  };

  // Handle create success
  const handleCreateSuccess = () => {
    fetchLinkTypes();
  };

  // Handle edit
  const handleEdit = (record: LinkTypeData) => {
    setSelectedLinkType(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    fetchLinkTypes();
  };

  // Handle delete
  const handleDelete = (record: LinkTypeData) => {
    const sourceName = getObjectTypeName(record.source_type_id);
    const targetName = getObjectTypeName(record.target_type_id);
    
    Modal.confirm({
      title: 'Delete Link Type',
      content: (
        <div>
          <p>Are you sure you want to delete this link type?</p>
          <p style={{ color: '#ff4d4f', marginTop: 8 }}>
            <strong>Warning:</strong> Deleting this Link Type will break the relationship graph
            between <strong>{sourceName}</strong> and <strong>{targetName}</strong>. It will{' '}
            <strong>NOT</strong> delete the underlying data tables.
          </p>
        </div>
      ),
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await apiClient.delete(`/meta/link-types/${record.id}`);
          message.success('Link type deleted successfully');
          fetchLinkTypes();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete link type');
        }
      },
    });
  };

  const columns: ColumnsType<LinkTypeData> = [
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
      render: (text) => <Tag color="green">{text}</Tag>,
    },
    {
      title: 'Source Type',
      key: 'sourceType',
      width: 150,
      render: (_, record) => getObjectTypeName(record.source_type_id),
    },
    {
      title: 'Target Type',
      key: 'targetType',
      width: 150,
      render: (_, record) => getObjectTypeName(record.target_type_id),
    },
    {
      title: 'Cardinality',
      dataIndex: 'cardinality',
      key: 'cardinality',
      width: 150,
      render: (text) => {
        const cardinalityMap: Record<string, string> = {
          'ONE_TO_ONE': '1:1',
          'ONE_TO_MANY': '1:N',
          'MANY_TO_ONE': 'N:1',
          'MANY_TO_MANY': 'M:N',
        };
        return <Tag>{cardinalityMap[text] || text}</Tag>;
      },
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
          Create Link Type
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
      <LinkTypeWizard
        visible={wizardVisible}
        onCancel={() => setWizardVisible(false)}
        onSuccess={handleCreateSuccess}
      />
      <LinkTypeEditor
        visible={editorVisible}
        linkType={selectedLinkType}
        onCancel={() => {
          setEditorVisible(false);
          setSelectedLinkType(null);
        }}
        onSuccess={handleEditSuccess}
      />
    </div>
  );
};

export default LinkTypeList;

