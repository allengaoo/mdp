/**
 * Link Type List View component.
 * 
 * @note V3 Migration: Now uses V3 project-scoped API for correct filtering.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { 
  fetchProjectLinkTypes,
  fetchProjectObjectTypes,
} from '../../api/v3/ontology';
import { IV3LinkTypeFull, IV3ObjectTypeFull } from '../../api/v3/types';
import apiClient from '../../api/axios';
import LinkTypeWizard from './LinkTypeWizard';
import LinkTypeEditor from './LinkTypeEditor';

// Use V3 interfaces
interface ObjectType extends IV3ObjectTypeFull {}

// Use V3 LinkTypeFull interface
interface LinkTypeData extends IV3LinkTypeFull {
  // Add compatibility fields if needed or ensure they match
}

const LinkTypeList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<LinkTypeData[]>([]);
  const [objectTypes, setObjectTypes] = useState<ObjectType[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardVisible, setWizardVisible] = useState(false);
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedLinkType, setSelectedLinkType] = useState<LinkTypeData | null>(null);

  // Fetch link types from API (using V3 project-scoped endpoint)
  const loadLinkTypes = async () => {
    if (!projectId) {
      setData([]);
      return;
    }
    
    try {
      setLoading(true);
      // Use V3 project-scoped API to get only link types related to this project
      const linkTypes = await fetchProjectLinkTypes(projectId);
      setData(linkTypes);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch link types');
    } finally {
      setLoading(false);
    }
  };

  // Fetch object types for display (using V3 project-scoped endpoint)
  const loadObjectTypes = async () => {
    if (!projectId) {
      setObjectTypes([]);
      return;
    }
    
    try {
      // Use V3 project-scoped API to get object types for name lookup
      const types = await fetchProjectObjectTypes(projectId);
      setObjectTypes(types);
    } catch (error: any) {
      // Silently fail
      console.error('Failed to fetch object types:', error);
    }
  };

  useEffect(() => {
    loadLinkTypes();
    loadObjectTypes();
  }, [projectId]);

  // Get object type display name (fallback if source_type_name/target_type_name not available)
  const getObjectTypeName = (typeId: string | null): string => {
    if (!typeId) return 'Unknown';
    const objType = objectTypes.find((ot) => ot.id === typeId);
    return objType?.display_name || objType?.api_name || typeId;
  };

  // Handle create success
  const handleCreateSuccess = () => {
    loadLinkTypes();
  };

  // Handle edit
  const handleEdit = (record: LinkTypeData) => {
    setSelectedLinkType(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    loadLinkTypes();
  };

  // Handle delete
  const handleDelete = (record: LinkTypeData) => {
    // V3 provides source_type_name and target_type_name directly
    const sourceName = record.source_type_name || getObjectTypeName(record.source_object_def_id);
    const targetName = record.target_type_name || getObjectTypeName(record.target_object_def_id);
    
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
          // TODO: Migrate to V3 delete API when available
          await apiClient.delete(`/meta/link-types/${record.id}`);
          message.success('Link type deleted successfully');
          loadLinkTypes();
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
      // V3 provides source_type_name directly, fallback to lookup if not available
      render: (_, record) => record.source_type_name || getObjectTypeName(record.source_object_def_id),
    },
    {
      title: 'Target Type',
      key: 'targetType',
      width: 150,
      // V3 provides target_type_name directly, fallback to lookup if not available
      render: (_, record) => record.target_type_name || getObjectTypeName(record.target_object_def_id),
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

