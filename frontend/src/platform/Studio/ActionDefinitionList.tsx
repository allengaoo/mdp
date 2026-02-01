/**
 * Action Definition List View component.
 * 
 * Uses V3 API for action management.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { fetchActions, deleteActionDefinition, IActionDefinitionRead } from '../../api/v3/logic';
import { fetchProjectObjectTypes } from '../../api/v3/ontology';
import ActionWizard from './ActionWizard';
import ActionEditor from './ActionEditor';

const { Text } = Typography;

// Use the V3 API type
type ActionDefinitionData = IActionDefinitionRead;

interface ObjectTypeData {
  id: string;
  display_name: string;
}

const ActionDefinitionList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<ActionDefinitionData[]>([]);
  const [objectTypes, setObjectTypes] = useState<ObjectTypeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardVisible, setWizardVisible] = useState(false);
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedAction, setSelectedAction] = useState<ActionDefinitionData | null>(null);

  // Fetch action definitions from V3 API
  const loadActions = async () => {
    try {
      setLoading(true);
      const actions = await fetchActions(projectId);
      setData(actions);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch action definitions');
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch object types for display using V3 API
  const loadObjectTypes = async () => {
    try {
      if (projectId) {
        const types = await fetchProjectObjectTypes(projectId);
        setObjectTypes(types);
      }
    } catch (error: any) {
      console.error('Failed to fetch object types:', error);
    }
  };

  useEffect(() => {
    loadActions();
    loadObjectTypes();
  }, [projectId]);

  // Get object type name
  const getObjectTypeName = (typeId: string | null | undefined): string => {
    if (!typeId) return 'Generic (通用)';
    const objType = objectTypes.find((ot) => ot.id === typeId);
    return objType ? objType.display_name : 'Generic (通用)';
  };

  // Count parameters
  const countParameters = (action: ActionDefinitionData): number => {
    return action.parameters_schema?.length || 0;
  };

  // Count validation rules
  const countValidationRules = (action: ActionDefinitionData): number => {
    if (!action.validation_rules) return 0;
    const rules = action.validation_rules;
    return (
      (rules.param_validation?.length || 0) +
      (rules.pre_condition?.length || 0) +
      (rules.post_condition?.length || 0)
    );
  };

  // Handle create success
  const handleCreateSuccess = () => {
    setWizardVisible(false);
    loadActions();
  };

  // Handle edit
  const handleEdit = (record: ActionDefinitionData) => {
    setSelectedAction(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    loadActions();
  };

  // Handle delete using V3 API
  const handleDelete = (record: ActionDefinitionData) => {
    Modal.confirm({
      title: 'Delete Action Definition',
      content: `Are you sure you want to delete "${record.display_name}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteActionDefinition(record.id);
          message.success('Action definition deleted successfully');
          loadActions();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete action definition');
        }
      },
    });
  };

  const columns: ColumnsType<ActionDefinitionData> = [
    {
      title: 'Name / Description',
      key: 'name',
      width: 300,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500, marginBottom: 4 }}>{record.display_name}</div>
          {record.description && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.description}
            </Text>
          )}
        </div>
      ),
    },
    {
      title: 'API Identifier',
      dataIndex: 'api_name',
      key: 'api_name',
      width: 180,
      render: (text) => (
        <Tag color="orange" style={{ fontFamily: 'monospace' }}>
          {text}
        </Tag>
      ),
    },
    {
      title: 'Target Object',
      key: 'targetObject',
      width: 150,
      render: (_, record) => (
        <Tag color={record.target_object_type_id ? 'blue' : 'default'}>
          {getObjectTypeName(record.target_object_type_id)}
        </Tag>
      ),
    },
    {
      title: 'Stats',
      key: 'stats',
      width: 150,
      render: (_, record) => {
        const paramCount = countParameters(record);
        const ruleCount = countValidationRules(record);
        return (
          <Space>
            <Tag color="cyan">{paramCount} Params</Tag>
            <Tag color="purple">{ruleCount} Rules</Tag>
          </Space>
        );
      },
    },
    {
      title: 'Operations',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)}>
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>Action Definitions</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setWizardVisible(true)}>
          Create Action
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

      <ActionWizard
        visible={wizardVisible}
        onCancel={() => setWizardVisible(false)}
        onSuccess={handleCreateSuccess}
      />

      {selectedAction && (
        <ActionEditor
          visible={editorVisible}
          action={selectedAction}
          onCancel={() => {
            setEditorVisible(false);
            setSelectedAction(null);
          }}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
};

export default ActionDefinitionList;
