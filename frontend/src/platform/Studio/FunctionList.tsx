/**
 * Function Definition List View component.
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import apiClient from '../../api/axios';
import FunctionWizard from './FunctionWizard';
import FunctionEditor from './FunctionEditor';

const { Text } = Typography;

interface FunctionDefinitionData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  code_content?: string;
  bound_object_type_id?: string | null;
  input_params_schema?: Array<{
    name: string;
    type: string;
    required: boolean;
  }>;
  output_type?: string;
  created_at?: string;
  updated_at?: string;
}

interface ObjectTypeData {
  id: string;
  display_name: string;
}

const FunctionList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<FunctionDefinitionData[]>([]);
  const [objectTypes, setObjectTypes] = useState<ObjectTypeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [wizardVisible, setWizardVisible] = useState(false);
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState<FunctionDefinitionData | null>(null);

  // Fetch function definitions from API
  const fetchFunctions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/meta/functions', {
        params: {
          limit: 100,
        },
      });
      setData(response.data || []);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch function definitions');
      // Fallback to mock data
      setData(MOCK_FUNCTIONS);
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
    fetchFunctions();
    fetchObjectTypes();
  }, [projectId]);

  // Get object type name
  const getObjectTypeName = (typeId: string | null | undefined): string => {
    if (!typeId) return 'None';
    const objType = objectTypes.find((ot) => ot.id === typeId);
    return objType ? objType.display_name : 'None';
  };

  // Count parameters
  const countParameters = (func: FunctionDefinitionData): number => {
    return func.input_params_schema?.length || 0;
  };

  // Get return type color
  const getReturnTypeColor = (outputType: string | undefined): string => {
    const colorMap: Record<string, string> = {
      VOID: 'default',
      STRING: 'blue',
      INTEGER: 'orange',
      DOUBLE: 'cyan',
      BOOLEAN: 'green',
      OBJECT: 'purple',
      OBJECT_REF: 'geekblue',
      ARRAY: 'magenta',
    };
    return colorMap[outputType?.toUpperCase() || 'VOID'] || 'default';
  };

  // Handle create success
  const handleCreateSuccess = () => {
    fetchFunctions();
  };

  // Handle edit
  const handleEdit = (record: FunctionDefinitionData) => {
    setSelectedFunction(record);
    setEditorVisible(true);
  };

  // Handle edit success
  const handleEditSuccess = () => {
    fetchFunctions();
  };

  // Handle delete
  const handleDelete = (record: FunctionDefinitionData) => {
    Modal.confirm({
      title: 'Delete Function Definition',
      content: `Are you sure you want to delete "${record.display_name}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await apiClient.delete(`/meta/functions/${record.id}`);
          message.success('Function definition deleted successfully');
          fetchFunctions();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete function definition');
        }
      },
    });
  };

  const columns: ColumnsType<FunctionDefinitionData> = [
    {
      title: 'Function Name',
      key: 'name',
      width: 250,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 600 }}>{record.display_name}</div>
          {record.description && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.description}
            </Text>
          )}
        </div>
      ),
    },
    {
      title: 'Return Type',
      dataIndex: 'output_type',
      key: 'output_type',
      width: 120,
      render: (text: string | undefined) => (
        <Tag color={getReturnTypeColor(text)}>{text || 'VOID'}</Tag>
      ),
    },
    {
      title: 'Parameters',
      key: 'parameters',
      width: 120,
      render: (_, record) => {
        const count = countParameters(record);
        return <Tag color="cyan">{count} Input{count !== 1 ? 's' : ''}</Tag>;
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
        <h2 style={{ margin: 0 }}>Function Definitions</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setWizardVisible(true)}>
          Create Function
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

      <FunctionWizard
        visible={wizardVisible}
        onCancel={() => setWizardVisible(false)}
        onSuccess={handleCreateSuccess}
      />

      {selectedFunction && (
        <FunctionEditor
          visible={editorVisible}
          function={selectedFunction}
          onCancel={() => {
            setEditorVisible(false);
            setSelectedFunction(null);
          }}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
};

// Mock data for fallback
const MOCK_FUNCTIONS: FunctionDefinitionData[] = [
  {
    id: '1',
    api_name: 'calc_strike',
    display_name: 'Calculate Strike Damage',
    description: 'Calculate damage output based on weapon type and target characteristics',
    output_type: 'INTEGER',
    input_params_schema: [
      { name: 'weapon_type', type: 'string', required: true },
      { name: 'target_type', type: 'string', required: true },
    ],
  },
  {
    id: '2',
    api_name: 'check_fuel',
    display_name: 'Check Fighter Fuel Level',
    description: 'Check current fuel level and return status indicator',
    output_type: 'OBJECT',
    input_params_schema: [{ name: 'fighter_id', type: 'string', required: true }],
  },
];

export default FunctionList;
