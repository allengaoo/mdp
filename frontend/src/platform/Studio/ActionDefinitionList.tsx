/**
 * Action Definition List View component.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import apiClient from '../../api/axios';
import ActionWizard from './ActionWizard';
import ActionEditor from './ActionEditor';

const { Text } = Typography;

interface ActionDefinitionData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  backing_function_id?: string;
  target_object_type_id?: string | null;
  operation_type?: string;
  parameters_schema?: Array<{
    name: string;
    api_id: string;
    data_type: string;
    required: boolean;
  }>;
  property_mapping?: Record<string, string>;
  validation_rules?: {
    param_validation?: Array<{ expression: string; error_message: string }>;
    pre_condition?: Array<{ expression: string; error_message: string }>;
    post_condition?: Array<{ expression: string; error_message: string }>;
  };
  created_at?: string;
  updated_at?: string;
}

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

  // Fetch action definitions from API
  const fetchActions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/meta/action-definitions', {
        params: {
          limit: 100,
        },
      });
      setData(response.data || []);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch action definitions');
      // Fallback to mock data
      setData(MOCK_ACTIONS);
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
      setObjectTypes(response.data || []);
    } catch (error: any) {
      console.error('Failed to fetch object types:', error);
    }
  };

  useEffect(() => {
    fetchActions();
    fetchObjectTypes();
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
    fetchActions();
  };

  // Handle edit
  const handleEdit = (record: ActionDefinitionData) => {
    setSelectedAction(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    fetchActions();
  };

  // Handle delete
  const handleDelete = (record: ActionDefinitionData) => {
    Modal.confirm({
      title: 'Delete Action Definition',
      content: `Are you sure you want to delete "${record.display_name}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await apiClient.delete(`/meta/action-definitions/${record.id}`);
          message.success('Action definition deleted successfully');
          fetchActions();
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

// Mock data for fallback
const MOCK_ACTIONS: ActionDefinitionData[] = [
  {
    id: '1',
    api_name: 'execute_strike',
    display_name: 'Execute Strike Action',
    description: 'Execute strike on target with specified weapon',
    target_object_type_id: '10000000-0000-0000-0000-000000000002',
    operation_type: 'function_logic',
    parameters_schema: [
      { name: 'Target ID', api_id: 'target_id', data_type: 'string', required: true },
      { name: 'Weapon Type', api_id: 'weapon_type', data_type: 'string', required: true },
    ],
    validation_rules: {
      param_validation: [
        { expression: 'target_id != null', error_message: 'Target ID is required' },
      ],
      pre_condition: [
        { expression: 'target.status == "Active"', error_message: 'Target must be active' },
      ],
    },
  },
  {
    id: '2',
    api_name: 'refuel',
    display_name: 'Refuel Fighter',
    description: 'Refuel fighter aircraft to specified fuel level',
    target_object_type_id: '10000000-0000-0000-0000-000000000001',
    operation_type: 'update_property',
    parameters_schema: [
      { name: 'Fighter ID', api_id: 'fighter_id', data_type: 'string', required: true },
      { name: 'Fuel Level', api_id: 'fuel_level', data_type: 'number', required: true },
    ],
    property_mapping: {
      fuel_level: 'fuel',
    },
  },
];

export default ActionDefinitionList;
