/**
 * Link Type Creation Wizard component.
 * Dynamic steps based on Cardinality (2 steps for 1:1/1:N, 3 steps for N:N).
 */
import React, { useState } from 'react';
import {
  Modal,
  Steps,
  Form,
  Input,
  Button,
  Select,
  Alert,
  Table,
  Space,
  Switch,
  message,
} from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import apiClient from '../../api/axios';
import { useParams } from 'react-router-dom';

const { Step } = Steps;
const { TextArea } = Input;

interface ObjectType {
  id: string;
  api_name: string;
  display_name: string;
  property_schema?: Record<string, string>;
}

interface RawTable {
  id: string;
  table_name: string;
  db_type: string;
  columns_schema: Array<{
    name: string;
    type: string;
  }>;
}

interface LinkPropertyMapping {
  column: string;
  displayName: string;
  dataType: string;
  include: boolean;
}

interface LinkTypeWizardProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

// Mock Object Types
const MOCK_OBJECTS: ObjectType[] = [
  {
    id: '10000000-0000-0000-0000-000000000001',
    api_name: 'fighter',
    display_name: 'Fighter',
    property_schema: { id: 'string', callsign: 'string', fuel: 'number' },
  },
  {
    id: '10000000-0000-0000-0000-000000000002',
    api_name: 'target',
    display_name: 'Target',
    property_schema: { id: 'string', name: 'string', threat_level: 'string' },
  },
  {
    id: '10000000-0000-0000-0000-000000000003',
    api_name: 'mission',
    display_name: 'Mission',
    property_schema: { id: 'string', name: 'string', status: 'string' },
  },
  {
    id: '10000000-0000-0000-0000-000000000004',
    api_name: 'intel',
    display_name: 'Intelligence',
    property_schema: { id: 'string', source: 'string', content: 'string' },
  },
  {
    id: '10000000-0000-0000-0000-000000000005',
    api_name: 'base',
    display_name: 'Base',
    property_schema: { id: 'string', name: 'string', location: 'string' },
  },
];

// Mock Raw Tables
const MOCK_RAW_TABLES: RawTable[] = [
  {
    id: 'table_001',
    table_name: 'mission_assignments',
    db_type: 'MySQL',
    columns_schema: [
      { name: 'fighter_id', type: 'varchar' },
      { name: 'mission_id', type: 'varchar' },
      { name: 'role', type: 'varchar' },
      { name: 'assigned_at', type: 'datetime' },
    ],
  },
  {
    id: 'table_002',
    table_name: 'intel_target_join',
    db_type: 'MySQL',
    columns_schema: [
      { name: 'intel_id', type: 'varchar' },
      { name: 'target_id', type: 'varchar' },
      { name: 'relevance', type: 'varchar' },
      { name: 'updated_at', type: 'datetime' },
    ],
  },
  {
    id: 'table_003',
    table_name: 'fighter_base_station',
    db_type: 'MySQL',
    columns_schema: [
      { name: 'fighter_id', type: 'varchar' },
      { name: 'base_id', type: 'varchar' },
      { name: 'assigned_date', type: 'date' },
      { name: 'status', type: 'varchar' },
    ],
  },
];

const CARDINALITY_OPTIONS = [
  { value: 'ONE_TO_ONE', label: '1:1' },
  { value: 'ONE_TO_MANY', label: '1:N' },
  { value: 'MANY_TO_MANY', label: 'N:N' },
];

const DATA_TYPE_OPTIONS = [
  { value: 'String', label: 'String' },
  { value: 'Integer', label: 'Integer' },
  { value: 'Date', label: 'Date' },
  { value: 'DateTime', label: 'DateTime' },
  { value: 'Number', label: 'Number' },
];

const LinkTypeWizard: React.FC<LinkTypeWizardProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [cardinality, setCardinality] = useState<string>('ONE_TO_MANY');
  const [selectedJoinTable, setSelectedJoinTable] = useState<RawTable | null>(null);
  const [linkProperties, setLinkProperties] = useState<LinkPropertyMapping[]>([]);
  const [loading, setLoading] = useState(false);

  // Calculate total steps based on cardinality
  const totalSteps = cardinality === 'MANY_TO_MANY' ? 3 : 2;
  const [currentStep, setCurrentStep] = useState(0);

  // Convert display name to API name
  const convertToApiName = (displayName: string): string => {
    return displayName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  };

  // Handle display name change to auto-fill API name
  const handleDisplayNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const displayName = e.target.value;
    form.setFieldsValue({ api_name: convertToApiName(displayName) });
  };

  // Handle cardinality change
  const handleCardinalityChange = (value: string) => {
    setCardinality(value);
    // Reset step if needed
    if (value !== 'MANY_TO_MANY' && currentStep === 2) {
      setCurrentStep(1);
    }
  };

  // Get source object type
  const getSourceObjectType = (): ObjectType | undefined => {
    const sourceTypeId = form.getFieldValue('source_type_id');
    return MOCK_OBJECTS.find((ot) => ot.id === sourceTypeId);
  };

  // Get target object type
  const getTargetObjectType = (): ObjectType | undefined => {
    const targetTypeId = form.getFieldValue('target_type_id');
    return MOCK_OBJECTS.find((ot) => ot.id === targetTypeId);
  };

  // Get object properties (for FK mapping)
  const getObjectProperties = (objectType: ObjectType | undefined): string[] => {
    if (!objectType || !objectType.property_schema) {
      return ['id']; // Default PK
    }
    return Object.keys(objectType.property_schema);
  };

  // Handle join table selection
  const handleJoinTableSelect = (tableId: string) => {
    const table = MOCK_RAW_TABLES.find((t) => t.id === tableId);
    setSelectedJoinTable(table || null);
    
    if (table) {
      // Get FK columns (used in key mapping)
      const sourceKey = form.getFieldValue('source_key_mapping');
      const targetKey = form.getFieldValue('target_key_mapping');
      const keyColumns = [sourceKey, targetKey].filter(Boolean);
      
      // Initialize link properties from remaining columns
      const propertyColumns = table.columns_schema.filter(
        (col) => !keyColumns.includes(col.name)
      );
      
      const properties: LinkPropertyMapping[] = propertyColumns.map((col) => ({
        column: col.name,
        displayName: col.name,
        dataType: mapColumnTypeToDataType(col.type),
        include: true,
      }));
      setLinkProperties(properties);
    }
  };

  // Map database column type to data type
  const mapColumnTypeToDataType = (dbType: string): string => {
    const typeMap: Record<string, string> = {
      varchar: 'String',
      int: 'Integer',
      datetime: 'DateTime',
      date: 'Date',
      decimal: 'Number',
      float: 'Number',
    };
    return typeMap[dbType.toLowerCase()] || 'String';
  };

  // Handle link property change
  const handleLinkPropertyChange = (
    index: number,
    field: keyof LinkPropertyMapping,
    value: any
  ) => {
    const newProperties = [...linkProperties];
    newProperties[index] = {
      ...newProperties[index],
      [field]: value,
    };
    setLinkProperties(newProperties);
  };

  // Validate current step
  const validateStep = async (): Promise<boolean> => {
    try {
      if (currentStep === 0) {
        await form.validateFields([
          'display_name',
          'api_name',
          'source_type_id',
          'cardinality',
          'target_type_id',
        ]);
        return true;
      } else if (currentStep === 1) {
        if (cardinality === 'MANY_TO_MANY') {
          const joinTableId = form.getFieldValue('join_table_id');
          const sourceKey = form.getFieldValue('source_key_mapping');
          const targetKey = form.getFieldValue('target_key_mapping');
          if (!joinTableId || !sourceKey || !targetKey) {
            message.error('Please complete all join table mappings');
            return false;
          }
        } else {
          const sourceProperty = form.getFieldValue('source_property');
          const targetProperty = form.getFieldValue('target_property');
          if (!sourceProperty || !targetProperty) {
            message.error('Please select both source and target properties');
            return false;
          }
        }
        return true;
      } else if (currentStep === 2) {
        // Step 3 validation (only for N:N)
        const includedProperties = linkProperties.filter((p) => p.include);
        if (includedProperties.length === 0) {
          message.warning('No link properties selected. Continue anyway?');
        }
        return true;
      }
      return true;
    } catch (error) {
      return false;
    }
  };

  // Handle next step
  const handleNext = async () => {
    const isValid = await validateStep();
    if (isValid) {
      setCurrentStep(currentStep + 1);
    }
  };

  // Handle previous step
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // Handle create
  const handleCreate = async () => {
    const isValid = await validateStep();
    if (!isValid) return;

    try {
      setLoading(true);
      const values = form.getFieldsValue();

      const payload = {
        api_name: values.api_name,
        display_name: values.display_name,
        source_type_id: values.source_type_id,
        target_type_id: values.target_type_id,
        cardinality: cardinality,
      };

      await apiClient.post('/meta/link-types', payload);
      message.success('Link type created successfully');
      onSuccess();
      handleCancel();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to create link type');
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    form.resetFields();
    setCurrentStep(0);
    setCardinality('ONE_TO_MANY');
    setSelectedJoinTable(null);
    setLinkProperties([]);
    onCancel();
  };

  // Link property columns for Step 3
  const linkPropertyColumns = [
    {
      title: 'Raw Column Name',
      dataIndex: 'column',
      key: 'column',
      width: 200,
      render: (text: string) => <span style={{ fontFamily: 'monospace' }}>{text}</span>,
    },
    {
      title: 'Logical Display Name',
      key: 'displayName',
      width: 200,
      render: (_: any, record: LinkPropertyMapping, index: number) => (
        <Input
          value={record.displayName}
          onChange={(e) => handleLinkPropertyChange(index, 'displayName', e.target.value)}
          placeholder="Display name"
        />
      ),
    },
    {
      title: 'Data Type',
      key: 'dataType',
      width: 150,
      render: (_: any, record: LinkPropertyMapping, index: number) => (
        <Select
          value={record.dataType}
          onChange={(value) => handleLinkPropertyChange(index, 'dataType', value)}
          style={{ width: '100%' }}
        >
          {DATA_TYPE_OPTIONS.map((opt) => (
            <Select.Option key={opt.value} value={opt.value}>
              {opt.label}
            </Select.Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Include?',
      key: 'include',
      width: 100,
      render: (_: any, record: LinkPropertyMapping, index: number) => (
        <Switch
          checked={record.include}
          onChange={(checked) => handleLinkPropertyChange(index, 'include', checked)}
        />
      ),
    },
  ];

  const isManyToMany = cardinality === 'MANY_TO_MANY';
  const sourceObject = getSourceObjectType();
  const targetObject = getTargetObjectType();

  return (
    <Modal
      title="Create Link Type"
      open={visible}
      onCancel={handleCancel}
      width={1000}
      footer={null}
      destroyOnClose
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="Definition" />
        <Step title={isManyToMany ? 'Join Table & Keys' : 'Connection Mapping'} />
        {isManyToMany && <Step title="Link Properties" />}
      </Steps>

      {/* Step 1: Definition */}
      {currentStep === 0 && (
        <Form form={form} layout="vertical">
          <Form.Item
            name="display_name"
            label="Name"
            rules={[{ required: true, message: 'Please enter name' }]}
          >
            <Input placeholder="e.g., Fighter Participation" onChange={handleDisplayNameChange} />
          </Form.Item>
          <Form.Item
            name="api_name"
            label="API Identifier"
            rules={[{ required: true, message: 'Please enter API identifier' }]}
          >
            <Input placeholder="e.g., participation" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Enter description..." />
          </Form.Item>

          {/* Directional Topology UI */}
          <Form.Item label="Directional Topology" required>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '16px',
                background: '#f5f5f5',
                borderRadius: 8,
              }}
            >
              <Form.Item
                name="source_type_id"
                style={{ flex: 1, marginBottom: 0 }}
                rules={[{ required: true, message: 'Select source' }]}
              >
                <Select placeholder="Source Object" size="large">
                  {MOCK_OBJECTS.map((ot) => (
                    <Select.Option key={ot.id} value={ot.id}>
                      {ot.display_name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <ArrowRightOutlined style={{ fontSize: 20, color: '#1890ff' }} />
              <Form.Item
                name="cardinality"
                style={{ width: 120, marginBottom: 0 }}
                rules={[{ required: true, message: 'Select' }]}
              >
                <Select
                  placeholder="Cardinality"
                  size="large"
                  onChange={handleCardinalityChange}
                >
                  {CARDINALITY_OPTIONS.map((opt) => (
                    <Select.Option key={opt.value} value={opt.value}>
                      {opt.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <ArrowRightOutlined style={{ fontSize: 20, color: '#1890ff' }} />
              <Form.Item
                name="target_type_id"
                style={{ flex: 1, marginBottom: 0 }}
                rules={[{ required: true, message: 'Select target' }]}
              >
                <Select placeholder="Target Object" size="large">
                  {MOCK_OBJECTS.map((ot) => (
                    <Select.Option key={ot.id} value={ot.id}>
                      {ot.display_name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </div>
          </Form.Item>
        </Form>
      )}

      {/* Step 2: Connection Mapping */}
      {currentStep === 1 && (
        <div>
          {!isManyToMany && (
            <div>
              <Alert
                message="Foreign Key Mapping"
                description="Map the source and target object properties for the relationship."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <Form.Item
                  name="source_property"
                  label="Source Object Property"
                  style={{ flex: 1 }}
                  rules={[{ required: true, message: 'Select source property' }]}
                >
                  <Select placeholder="Select property (default: PK)">
                    {getObjectProperties(sourceObject).map((prop) => (
                      <Select.Option key={prop} value={prop}>
                        {prop} {prop === 'id' ? '(PK)' : ''}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  name="target_property"
                  label="Target Object Property (FK)"
                  style={{ flex: 1 }}
                  rules={[{ required: true, message: 'Select target property' }]}
                >
                  <Select placeholder="Select foreign key property">
                    {getObjectProperties(targetObject).map((prop) => (
                      <Select.Option key={prop} value={prop}>
                        {prop}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </div>
            </div>
          )}

          {isManyToMany && (
            <div>
              <Alert
                message="Join Table & Keys"
                description="Select a join table and map the source and target object keys."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              <Form.Item
                name="join_table_id"
                label="Select Join Table"
                rules={[{ required: true, message: 'Please select join table' }]}
              >
                <Select
                  placeholder="Select join table"
                  onChange={handleJoinTableSelect}
                  size="large"
                >
                  {MOCK_RAW_TABLES.map((table) => (
                    <Select.Option key={table.id} value={table.id}>
                      {table.table_name} ({table.db_type})
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              {selectedJoinTable && (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                      Source Key Mapping:
                    </label>
                    <Form.Item
                      name="source_key_mapping"
                      rules={[{ required: true, message: 'Please map source key' }]}
                    >
                      <Select placeholder="Map Source Object PK to Join Table Column">
                        {selectedJoinTable.columns_schema
                          .filter((col) => col.name.includes('_id') || col.name.includes('id'))
                          .map((col) => (
                            <Select.Option key={col.name} value={col.name}>
                              {col.name} ({col.type})
                            </Select.Option>
                          ))}
                      </Select>
                    </Form.Item>
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                      Target Key Mapping:
                    </label>
                    <Form.Item
                      name="target_key_mapping"
                      rules={[{ required: true, message: 'Please map target key' }]}
                    >
                      <Select placeholder="Map Target Object PK to Join Table Column">
                        {selectedJoinTable.columns_schema
                          .filter((col) => col.name.includes('_id') || col.name.includes('id'))
                          .map((col) => (
                            <Select.Option key={col.name} value={col.name}>
                              {col.name} ({col.type})
                            </Select.Option>
                          ))}
                      </Select>
                    </Form.Item>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Step 3: Link Properties (Only for N:N) */}
      {currentStep === 2 && isManyToMany && (
        <div>
          <Alert
            message="Link Properties Mapping"
            description="Define properties that live on the link itself (e.g., 'Role', 'Assigned At'). These are mapped from the remaining columns in the join table."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Table
            columns={linkPropertyColumns}
            dataSource={linkProperties}
            rowKey="column"
            pagination={false}
            size="small"
            style={{ background: '#fff' }}
          />
        </div>
      )}

      {/* Footer Buttons */}
      <div style={{ marginTop: 24, textAlign: 'right' }}>
        <Space>
          {currentStep > 0 && (
            <Button onClick={handlePrev}>Previous</Button>
          )}
          {currentStep < totalSteps - 1 ? (
            <Button type="primary" onClick={handleNext}>
              Next
            </Button>
          ) : (
            <Button type="primary" loading={loading} onClick={handleCreate}>
              Create
            </Button>
          )}
          <Button onClick={handleCancel}>Cancel</Button>
        </Space>
      </div>
    </Modal>
  );
};

export default LinkTypeWizard;
