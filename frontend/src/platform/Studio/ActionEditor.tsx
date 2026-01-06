/**
 * Action Definition Editor component.
 * Vertical tabs layout for editing existing action definitions.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  Radio,
  Select,
  Table,
  Space,
  Switch,
  Tabs,
  message,
  Card,
  Row,
  Col,
} from 'antd';
import {
  PlusSquareOutlined,
  EditOutlined,
  DeleteOutlined,
  LinkOutlined,
  DisconnectOutlined,
  CodeOutlined,
  PlusOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons';
import apiClient from '../../api/axios';
import { useParams } from 'react-router-dom';

const { TextArea } = Input;
const { TabPane } = Tabs;

interface ActionDefinitionData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
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
}

interface ActionEditorProps {
  visible: boolean;
  action: ActionDefinitionData;
  onCancel: () => void;
  onSuccess: () => void;
}

interface Parameter {
  display_name: string;
  api_id: string;
  data_type: string;
  required: boolean;
}

interface PropertyMapping {
  param_key: string;
  property_key: string;
}

interface ValidationRule {
  expression: string;
  error_message: string;
}

interface ObjectTypeData {
  id: string;
  display_name: string;
  api_name: string;
  property_schema?: Record<string, any>;
}

const OPERATION_TYPES = [
  { value: 'create_object', label: 'Create Object', icon: PlusSquareOutlined, color: '#52c41a' },
  { value: 'update_property', label: 'Update Property', icon: EditOutlined, color: '#1890ff' },
  { value: 'delete_object', label: 'Delete Object', icon: DeleteOutlined, color: '#ff4d4f' },
  { value: 'link_objects', label: 'Link Objects', icon: LinkOutlined, color: '#722ed1' },
  { value: 'unlink_objects', label: 'Unlink Objects', icon: DisconnectOutlined, color: '#fa8c16' },
  { value: 'function_logic', label: 'Function Logic', icon: CodeOutlined, color: '#13c2c2' },
];

const ActionEditor: React.FC<ActionEditorProps> = ({ visible, action, onCancel, onSuccess }) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [targetScope, setTargetScope] = useState<'generic' | 'specific'>('generic');
  const [selectedOperationType, setSelectedOperationType] = useState<string>('');
  const [objectTypes, setObjectTypes] = useState<ObjectTypeData[]>([]);
  const [selectedObjectType, setSelectedObjectType] = useState<ObjectTypeData | null>(null);
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [propertyMappings, setPropertyMappings] = useState<PropertyMapping[]>([]);
  const [validationRules, setValidationRules] = useState<{
    param_validation: ValidationRule[];
    pre_condition: ValidationRule[];
    post_condition: ValidationRule[];
  }>({
    param_validation: [],
    pre_condition: [],
    post_condition: [],
  });

  // Initialize form data
  useEffect(() => {
    if (visible && action) {
      // Set form values
      form.setFieldsValue({
        display_name: action.display_name,
        api_name: action.api_name,
        description: action.description || '',
        target_object_type_id: action.target_object_type_id || undefined,
      });

      // Set state
      setTargetScope(action.target_object_type_id ? 'specific' : 'generic');
      setSelectedOperationType(action.operation_type || '');
      
      // Set parameters
      if (action.parameters_schema) {
        setParameters(
          action.parameters_schema.map((p) => ({
            display_name: p.name,
            api_id: p.api_id,
            data_type: p.data_type,
            required: p.required,
          }))
        );
      }

      // Set property mappings
      if (action.property_mapping) {
        setPropertyMappings(
          Object.entries(action.property_mapping).map(([param_key, property_key]) => ({
            param_key,
            property_key,
          }))
        );
      }

      // Set validation rules
      if (action.validation_rules) {
        setValidationRules({
          param_validation: action.validation_rules.param_validation || [],
          pre_condition: action.validation_rules.pre_condition || [],
          post_condition: action.validation_rules.post_condition || [],
        });
      }
    }
  }, [visible, action, form]);

  // Fetch object types
  useEffect(() => {
    const fetchObjectTypes = async () => {
      try {
        const response = await apiClient.get('/meta/object-types', {
          params: { limit: 100 },
        });
        const filtered = projectId
          ? response.data.filter((ot: ObjectTypeData) => ot.project_id === projectId)
          : response.data;
        setObjectTypes(filtered);
        
        // Set selected object type if exists
        if (action?.target_object_type_id) {
          const objType = filtered.find((ot: ObjectTypeData) => ot.id === action.target_object_type_id);
          setSelectedObjectType(objType || null);
        }
      } catch (error) {
        console.error('Failed to fetch object types:', error);
        setObjectTypes(MOCK_OBJECT_TYPES);
      }
    };
    if (visible) {
      fetchObjectTypes();
    }
  }, [visible, projectId, action]);

  // Update selected object type when target scope changes
  useEffect(() => {
    if (targetScope === 'generic') {
      setSelectedObjectType(null);
      form.setFieldsValue({ target_object_type_id: undefined });
    } else if (action?.target_object_type_id) {
      const objType = objectTypes.find((ot) => ot.id === action.target_object_type_id);
      setSelectedObjectType(objType || null);
    }
  }, [targetScope, form, action, objectTypes]);

  // Get selected object type properties
  const getObjectProperties = (): Array<{ key: string; label: string; type: string }> => {
    if (!selectedObjectType?.property_schema) return [];
    return Object.entries(selectedObjectType.property_schema).map(([key, value]) => ({
      key,
      label: key,
      type: typeof value === 'string' ? value : (value as any).type || 'string',
    }));
  };

  // Handle save
  const handleSave = async () => {
    try {
      const values = form.getFieldsValue();
      
      // Construct payload
      const payload: any = {
        display_name: values.display_name,
        description: values.description || '',
        operation_type: selectedOperationType,
        target_object_type_id: targetScope === 'specific' ? values.target_object_type_id : null,
        parameters_schema: parameters,
        property_mapping: propertyMappings.length > 0 ? propertyMappings.reduce((acc, m) => {
          acc[m.param_key] = m.property_key;
          return acc;
        }, {} as Record<string, string>) : null,
        validation_rules: {
          param_validation: validationRules.param_validation,
          pre_condition: validationRules.pre_condition,
          post_condition: validationRules.post_condition,
        },
      };

      await apiClient.put(`/meta/action-definitions/${action.id}`, payload);
      message.success('Action definition updated successfully');
      onSuccess();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update action definition');
    }
  };

  // Add parameter
  const addParameter = () => {
    setParameters([
      ...parameters,
      { display_name: '', api_id: '', data_type: 'string', required: false },
    ]);
  };

  // Remove parameter
  const removeParameter = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  // Update parameter
  const updateParameter = (index: number, field: keyof Parameter, value: any) => {
    const updated = [...parameters];
    updated[index] = { ...updated[index], [field]: value };
    setParameters(updated);
  };

  // Add property mapping
  const addPropertyMapping = () => {
    setPropertyMappings([...propertyMappings, { param_key: '', property_key: '' }]);
  };

  // Remove property mapping
  const removePropertyMapping = (index: number) => {
    setPropertyMappings(propertyMappings.filter((_, i) => i !== index));
  };

  // Update property mapping
  const updatePropertyMapping = (index: number, field: keyof PropertyMapping, value: string) => {
    const updated = [...propertyMappings];
    updated[index] = { ...updated[index], [field]: value };
    setPropertyMappings(updated);
  };

  // Add validation rule
  const addValidationRule = (type: 'param_validation' | 'pre_condition' | 'post_condition') => {
    setValidationRules({
      ...validationRules,
      [type]: [...validationRules[type], { expression: '', error_message: '' }],
    });
  };

  // Remove validation rule
  const removeValidationRule = (
    type: 'param_validation' | 'pre_condition' | 'post_condition',
    index: number
  ) => {
    setValidationRules({
      ...validationRules,
      [type]: validationRules[type].filter((_, i) => i !== index),
    });
  };

  // Update validation rule
  const updateValidationRule = (
    type: 'param_validation' | 'pre_condition' | 'post_condition',
    index: number,
    field: keyof ValidationRule,
    value: string
  ) => {
    const updated = [...validationRules[type]];
    updated[index] = { ...updated[index], [field]: value };
    setValidationRules({ ...validationRules, [type]: updated });
  };

  // Check if property mapping should be shown
  const showPropertyMapping =
    selectedObjectType &&
    (selectedOperationType === 'create_object' || selectedOperationType === 'update_property');

  const paramColumns = [
    {
      title: 'Display Name',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (_: any, record: Parameter, index: number) => (
        <Input
          value={record.display_name}
          onChange={(e) => updateParameter(index, 'display_name', e.target.value)}
          placeholder="Parameter Name"
        />
      ),
    },
    {
      title: 'API ID',
      dataIndex: 'api_id',
      key: 'api_id',
      render: (_: any, record: Parameter, index: number) => (
        <Input
          value={record.api_id}
          onChange={(e) => updateParameter(index, 'api_id', e.target.value)}
          placeholder="api_id"
          style={{ fontFamily: 'monospace' }}
        />
      ),
    },
    {
      title: 'Data Type',
      dataIndex: 'data_type',
      key: 'data_type',
      render: (_: any, record: Parameter, index: number) => (
        <Select
          value={record.data_type}
          onChange={(value) => updateParameter(index, 'data_type', value)}
          style={{ width: '100%' }}
        >
          <Select.Option value="string">String</Select.Option>
          <Select.Option value="number">Number</Select.Option>
          <Select.Option value="date">Date</Select.Option>
          <Select.Option value="object_ref">Object Ref</Select.Option>
        </Select>
      ),
    },
    {
      title: 'Required?',
      dataIndex: 'required',
      key: 'required',
      render: (_: any, record: Parameter, index: number) => (
        <Switch
          checked={record.required}
          onChange={(checked) => updateParameter(index, 'required', checked)}
        />
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, __: Parameter, index: number) => (
        <Button
          type="link"
          danger
          icon={<MinusCircleOutlined />}
          onClick={() => removeParameter(index)}
        >
          Remove
        </Button>
      ),
    },
  ];

  const mappingColumns = [
    {
      title: 'Parameter (Source)',
      dataIndex: 'param_key',
      key: 'param_key',
      render: (_: any, record: PropertyMapping, index: number) => (
        <Select
          value={record.param_key}
          onChange={(value) => updatePropertyMapping(index, 'param_key', value)}
          style={{ width: '100%' }}
          placeholder="Select Parameter"
        >
          {parameters.map((p) => (
            <Select.Option key={p.api_id} value={p.api_id}>
              {p.display_name} ({p.api_id})
            </Select.Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Object Property (Target)',
      dataIndex: 'property_key',
      key: 'property_key',
      render: (_: any, record: PropertyMapping, index: number) => (
        <Select
          value={record.property_key}
          onChange={(value) => updatePropertyMapping(index, 'property_key', value)}
          style={{ width: '100%' }}
          placeholder="Select Property"
        >
          {getObjectProperties().map((prop) => (
            <Select.Option key={prop.key} value={prop.key}>
              {prop.label} ({prop.type})
            </Select.Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, __: PropertyMapping, index: number) => (
        <Button
          type="link"
          danger
          icon={<MinusCircleOutlined />}
          onClick={() => removePropertyMapping(index)}
        >
          Remove
        </Button>
      ),
    },
  ];

  return (
    <Modal
      title="Edit Action Definition"
      open={visible}
      onCancel={onCancel}
      width={1000}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="save" type="primary" onClick={handleSave}>
          Save Changes
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical">
        <Tabs tabPosition="left" style={{ minHeight: 500 }}>
          {/* Tab 1: Basic Info */}
          <TabPane tab="Basic Info" key="basic">
            <Form.Item
              label="Display Name"
              name="display_name"
              rules={[{ required: true, message: 'Please enter display name' }]}
            >
              <Input placeholder="Action Name" />
            </Form.Item>

            <Form.Item label="API Identifier" name="api_name">
              <Input placeholder="api_identifier" style={{ fontFamily: 'monospace' }} disabled />
            </Form.Item>

            <Form.Item label="Description" name="description">
              <TextArea rows={3} placeholder="Action description" />
            </Form.Item>

            <Form.Item label="Target Scope">
              <Radio.Group
                value={targetScope}
                onChange={(e) => setTargetScope(e.target.value)}
              >
                <Radio value="generic">Generic (通用)</Radio>
                <Radio value="specific">Specific Object</Radio>
              </Radio.Group>
            </Form.Item>

            {targetScope === 'specific' && (
              <Form.Item label="Target Object Type" name="target_object_type_id">
                <Select
                  placeholder="Select Object Type"
                  onChange={(value) => {
                    const objType = objectTypes.find((ot) => ot.id === value);
                    setSelectedObjectType(objType || null);
                  }}
                >
                  {objectTypes.map((ot) => (
                    <Select.Option key={ot.id} value={ot.id}>
                      {ot.display_name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            )}
          </TabPane>

          {/* Tab 2: Operation Type */}
          <TabPane tab="Operation Type" key="operation">
            <div style={{ marginBottom: 16 }}>
              <TextArea
                rows={2}
                value="Select the type of operation this action will perform."
                disabled
                style={{ background: '#f5f5f5' }}
              />
            </div>
            <Row gutter={[16, 16]}>
              {OPERATION_TYPES.map((op) => {
                const Icon = op.icon;
                const isSelected = selectedOperationType === op.value;
                return (
                  <Col span={8} key={op.value}>
                    <Card
                      hoverable
                      style={{
                        border: isSelected ? `2px solid ${op.color}` : '1px solid #d9d9d9',
                        background: isSelected ? '#e6f7ff' : '#fff',
                        cursor: 'pointer',
                        textAlign: 'center',
                      }}
                      onClick={() => setSelectedOperationType(op.value)}
                    >
                      <Icon style={{ fontSize: 32, color: op.color, marginBottom: 8 }} />
                      <div style={{ fontWeight: isSelected ? 600 : 400 }}>{op.label}</div>
                    </Card>
                  </Col>
                );
              })}
            </Row>
          </TabPane>

          {/* Tab 3: Parameters & Mapping */}
          <TabPane tab="Parameters & Mapping" key="parameters">
            <div style={{ marginBottom: 24 }}>
              <h4>Parameter Definitions</h4>
              <Table
                columns={paramColumns}
                dataSource={parameters}
                rowKey={(_, index) => `param-${index}`}
                pagination={false}
                size="small"
                footer={() => (
                  <Button type="dashed" icon={<PlusOutlined />} onClick={addParameter} block>
                    Add Parameter
                  </Button>
                )}
              />
            </div>

            {showPropertyMapping && (
              <div>
                <h4>Property Mapping</h4>
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Map parameters to object properties. Only compatible types are allowed.
                </p>
                <Table
                  columns={mappingColumns}
                  dataSource={propertyMappings}
                  rowKey={(_, index) => `mapping-${index}`}
                  pagination={false}
                  size="small"
                  footer={() => (
                    <Button
                      type="dashed"
                      icon={<PlusOutlined />}
                      onClick={addPropertyMapping}
                      block
                    >
                      Add Mapping
                    </Button>
                  )}
                />
              </div>
            )}
          </TabPane>

          {/* Tab 4: Validations */}
          <TabPane tab="Validations" key="validations">
            <Tabs defaultActiveKey="param_validation">
              <TabPane tab="Param Validation" key="param_validation">
                <div>
                  {validationRules.param_validation.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Input
                          placeholder="Expression (e.g., target_id != null)"
                          value={rule.expression}
                          onChange={(e) =>
                            updateValidationRule('param_validation', index, 'expression', e.target.value)
                          }
                        />
                        <Input
                          placeholder="Error Message"
                          value={rule.error_message}
                          onChange={(e) =>
                            updateValidationRule(
                              'param_validation',
                              index,
                              'error_message',
                              e.target.value
                            )
                          }
                        />
                        <Button
                          type="link"
                          danger
                          icon={<MinusCircleOutlined />}
                          onClick={() => removeValidationRule('param_validation', index)}
                        >
                          Remove Rule
                        </Button>
                      </Space>
                    </Card>
                  ))}
                  <Button
                    type="dashed"
                    icon={<PlusOutlined />}
                    onClick={() => addValidationRule('param_validation')}
                    block
                  >
                    Add Rule
                  </Button>
                </div>
              </TabPane>
              <TabPane tab="Pre-condition" key="pre_condition">
                <div>
                  {validationRules.pre_condition.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Input
                          placeholder="Expression (e.g., object.status == 'Active')"
                          value={rule.expression}
                          onChange={(e) =>
                            updateValidationRule('pre_condition', index, 'expression', e.target.value)
                          }
                        />
                        <Input
                          placeholder="Error Message"
                          value={rule.error_message}
                          onChange={(e) =>
                            updateValidationRule('pre_condition', index, 'error_message', e.target.value)
                          }
                        />
                        <Button
                          type="link"
                          danger
                          icon={<MinusCircleOutlined />}
                          onClick={() => removeValidationRule('pre_condition', index)}
                        >
                          Remove Rule
                        </Button>
                      </Space>
                    </Card>
                  ))}
                  <Button
                    type="dashed"
                    icon={<PlusOutlined />}
                    onClick={() => addValidationRule('pre_condition')}
                    block
                  >
                    Add Rule
                  </Button>
                </div>
              </TabPane>
              <TabPane tab="Post-condition" key="post_condition">
                <div>
                  {validationRules.post_condition.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Input
                          placeholder="Expression (e.g., object.fuel > 0)"
                          value={rule.expression}
                          onChange={(e) =>
                            updateValidationRule('post_condition', index, 'expression', e.target.value)
                          }
                        />
                        <Input
                          placeholder="Error Message"
                          value={rule.error_message}
                          onChange={(e) =>
                            updateValidationRule('post_condition', index, 'error_message', e.target.value)
                          }
                        />
                        <Button
                          type="link"
                          danger
                          icon={<MinusCircleOutlined />}
                          onClick={() => removeValidationRule('post_condition', index)}
                        >
                          Remove Rule
                        </Button>
                      </Space>
                    </Card>
                  ))}
                  <Button
                    type="dashed"
                    icon={<PlusOutlined />}
                    onClick={() => addValidationRule('post_condition')}
                    block
                  >
                    Add Rule
                  </Button>
                </div>
              </TabPane>
            </Tabs>
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

// Mock Object Types
const MOCK_OBJECT_TYPES: ObjectTypeData[] = [
  {
    id: '10000000-0000-0000-0000-000000000001',
    api_name: 'fighter',
    display_name: 'Fighter',
    property_schema: { id: 'string', callsign: 'string', fuel: 'number', status: 'string' },
  },
  {
    id: '10000000-0000-0000-0000-000000000002',
    api_name: 'target',
    display_name: 'Target',
    property_schema: { id: 'string', name: 'string', threat_level: 'string', status: 'string' },
  },
];

export default ActionEditor;

