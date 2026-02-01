/**
 * Action Definition Editor component.
 * Vertical tabs layout for editing existing action definitions.
 * 
 * @todo V3 Migration: This component still uses V1 API.
 * Migrate to V3 when backend Action endpoints are implemented.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
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
  EditOutlined,
  LinkOutlined,
  DisconnectOutlined,
  CodeOutlined,
  PlusOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons';
import apiClient from '../../api/axios';
import { useParams } from 'react-router-dom';
import { 
  fetchProjectObjectTypes, 
  fetchObjectTypeProperties,
  fetchObjectTypes as fetchAllObjectTypes,
  fetchLinkTypes,
  fetchProjectLinkTypes,
} from '../../api/v3/ontology';
import { IV3LinkTypeFull } from '../../api/v3/types';
import { fetchFunctionsForList, IFunctionDef } from '../../api/v3/logic';

const { TextArea } = Input;
const { TabPane } = Tabs;

interface ActionDefinitionData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  target_object_type_id?: string | null;
  link_type_id?: string | null;
  backing_function_id?: string | null;
  operation_type?: string;
  parameters_schema?: Array<{
    name: string;
    api_id: string;
    data_type: string;
    required: boolean;
  }>;
  property_mapping?: Record<string, string>;
  validation_rules?: {
    param_validation?: Array<{ target_field?: string; expression: string; error_message: string }>;
    pre_condition?: Array<{ target_field?: string; expression: string; error_message: string }>;
    post_condition?: Array<{ target_field?: string; expression: string; error_message: string }>;
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
  target_field: string;
  expression: string;
  error_message: string;
}

interface ObjectProperty {
  key: string;
  label: string;
  type: string;
}

interface ObjectTypeData {
  id: string;
  display_name: string;
  api_name: string;
  property_schema?: Record<string, any>;
}

const OPERATION_TYPES = [
  { value: 'update_property', label: 'Update Property', icon: EditOutlined, color: '#1890ff' },
  { value: 'link_objects', label: 'Link Objects', icon: LinkOutlined, color: '#722ed1' },
  { value: 'unlink_objects', label: 'Unlink Objects', icon: DisconnectOutlined, color: '#fa8c16' },
  { value: 'function_logic', label: 'Function Logic', icon: CodeOutlined, color: '#13c2c2' },
];

const ActionEditor: React.FC<ActionEditorProps> = ({ visible, action, onCancel, onSuccess }) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  // Target scope is always 'specific' - removed generic option
  const [selectedOperationType, setSelectedOperationType] = useState<string>('');
  const [objectTypes, setObjectTypes] = useState<ObjectTypeData[]>([]);
  const [selectedObjectType, setSelectedObjectType] = useState<ObjectTypeData | null>(null);
  const [objectProperties, setObjectProperties] = useState<ObjectProperty[]>([]);
  const [linkTypes, setLinkTypes] = useState<IV3LinkTypeFull[]>([]);
  const [selectedLinkType, setSelectedLinkType] = useState<IV3LinkTypeFull | null>(null);
  const [functions, setFunctions] = useState<IFunctionDef[]>([]);
  const [selectedFunction, setSelectedFunction] = useState<IFunctionDef | null>(null);
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
      setSelectedOperationType(action.operation_type || '');
      
      // Set parameters
      if (action.parameters_schema) {
        setParameters(
          action.parameters_schema.map((p: any) => ({
            display_name: p.display_name || p.name || '',
            api_id: p.api_id || '',
            data_type: p.data_type || p.type || 'string',
            required: p.required || false,
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
  // In Ontology Studio (with projectId): only show project-bound object types
  // In Actions & Logic (no projectId): show all object types
  useEffect(() => {
    const loadObjectTypes = async () => {
      try {
        let data: ObjectTypeData[];
        if (projectId) {
          // Ontology Studio context: fetch project-bound object types only
          data = await fetchProjectObjectTypes(projectId);
        } else {
          // Global context (Actions & Logic): fetch all object types
          data = await fetchAllObjectTypes();
        }
        setObjectTypes(data);
        
        // Set selected object type if exists
        if (action?.target_object_type_id) {
          const objType = data.find((ot: ObjectTypeData) => ot.id === action.target_object_type_id);
          setSelectedObjectType(objType || null);
        }
      } catch (error) {
        console.error('Failed to fetch object types:', error);
        setObjectTypes([]);
      }
    };
    if (visible) {
      loadObjectTypes();
    }
  }, [visible, projectId, action]);

  // Fetch link types - for link_objects/unlink_objects operations
  useEffect(() => {
    const loadLinkTypes = async () => {
      try {
        let data: IV3LinkTypeFull[];
        if (projectId) {
          // Ontology Studio context: fetch project-related link types only
          data = await fetchProjectLinkTypes(projectId);
        } else {
          // Global context (Actions & Logic): fetch all link types
          data = await fetchLinkTypes();
        }
        setLinkTypes(data);
        
        // Set selected link type if exists
        if (action?.link_type_id) {
          const linkType = data.find((lt: IV3LinkTypeFull) => lt.id === action.link_type_id);
          setSelectedLinkType(linkType || null);
        }
      } catch (error) {
        console.error('Failed to fetch link types:', error);
        setLinkTypes([]);
      }
    };
    if (visible) {
      loadLinkTypes();
    }
  }, [visible, projectId, action]);

  // Update selected object type when action changes
  useEffect(() => {
    if (action?.target_object_type_id && objectTypes.length > 0) {
      const objType = objectTypes.find((ot) => ot.id === action.target_object_type_id);
      setSelectedObjectType(objType || null);
    }
  }, [action, objectTypes]);

  // Update selected link type when action changes
  useEffect(() => {
    if (action?.link_type_id && linkTypes.length > 0) {
      const linkType = linkTypes.find((lt) => lt.id === action.link_type_id);
      setSelectedLinkType(linkType || null);
    }
  }, [action, linkTypes]);

  // Fetch functions - for function_logic operation
  useEffect(() => {
    const loadFunctions = async () => {
      try {
        const data = await fetchFunctionsForList();
        setFunctions(data);
        
        // Set selected function if exists
        if (action?.backing_function_id) {
          const func = data.find((f: IFunctionDef) => f.id === action.backing_function_id);
          setSelectedFunction(func || null);
        }
      } catch (error) {
        console.error('Failed to fetch functions:', error);
        setFunctions([]);
      }
    };
    if (visible) {
      loadFunctions();
    }
  }, [visible, action]);

  // Update selected function when action changes
  useEffect(() => {
    if (action?.backing_function_id && functions.length > 0) {
      const func = functions.find((f) => f.id === action.backing_function_id);
      setSelectedFunction(func || null);
    }
  }, [action, functions]);

  // Load object properties when selected object type changes
  useEffect(() => {
    const loadObjectProperties = async () => {
      if (!selectedObjectType?.id) {
        setObjectProperties([]);
        return;
      }
      try {
        const properties = await fetchObjectTypeProperties(selectedObjectType.id);
        const props: ObjectProperty[] = properties.map((p: any) => ({
          key: p.api_name || p.id,
          label: p.display_name || p.api_name || p.id,
          type: p.data_type || 'string',
        }));
        setObjectProperties(props);
      } catch (error) {
        console.error('Failed to load object properties:', error);
        setObjectProperties([]);
      }
    };
    loadObjectProperties();
  }, [selectedObjectType]);

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
        target_object_type_id: values.target_object_type_id || null,
        // Add link_type_id for link_objects/unlink_objects operations
        link_type_id: showLinkTypeSelection && selectedLinkType ? selectedLinkType.id : null,
        // Add backing_function_id for function_logic operations
        backing_function_id: showFunctionSelection && selectedFunction ? selectedFunction.id : null,
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
      [type]: [...validationRules[type], { target_field: '', expression: '', error_message: '' }],
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
    selectedObjectType && selectedOperationType === 'update_property';

  // Check if link type selection should be shown
  const showLinkTypeSelection =
    selectedOperationType === 'link_objects' || selectedOperationType === 'unlink_objects';

  // Check if function selection should be shown
  const showFunctionSelection = selectedOperationType === 'function_logic';

  // Handle function change
  const handleFunctionChange = (functionId: string) => {
    const func = functions.find((f) => f.id === functionId);
    setSelectedFunction(func || null);
  };

  // Handle link type change
  const handleLinkTypeChange = (linkTypeId: string) => {
    const linkType = linkTypes.find((lt) => lt.id === linkTypeId);
    setSelectedLinkType(linkType || null);
  };

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

            <Form.Item 
              label="Target Object Type" 
              name="target_object_type_id"
              rules={[{ required: true, message: '请选择目标对象类型' }]}
            >
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
            {/* Link Type Selection - for link_objects/unlink_objects */}
            {showLinkTypeSelection && (
              <div style={{ marginBottom: 24 }}>
                <h4>Link Type Selection</h4>
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  {selectedOperationType === 'link_objects' 
                    ? 'Select the link type to create relationships between objects.'
                    : 'Select the link type to remove relationships between objects.'}
                </p>
                <Select
                  placeholder="Select Link Type"
                  value={selectedLinkType?.id}
                  onChange={handleLinkTypeChange}
                  style={{ width: '100%', marginBottom: 16 }}
                >
                  {linkTypes.map((lt) => {
                    const sourceType = objectTypes.find(ot => ot.id === lt.source_object_def_id);
                    const targetType = objectTypes.find(ot => ot.id === lt.target_object_def_id);
                    return (
                      <Select.Option key={lt.id} value={lt.id}>
                        {lt.display_name} ({sourceType?.display_name || lt.source_type_name || 'Unknown'} → {targetType?.display_name || lt.target_type_name || 'Unknown'})
                      </Select.Option>
                    );
                  })}
                </Select>
                
                {selectedLinkType && (
                  <Card size="small" style={{ background: '#f6f8fa' }}>
                    <p><strong>Source Object Type:</strong> {objectTypes.find(ot => ot.id === selectedLinkType.source_object_def_id)?.display_name || selectedLinkType.source_type_name || 'Unknown'}</p>
                    <p><strong>Target Object Type:</strong> {objectTypes.find(ot => ot.id === selectedLinkType.target_object_def_id)?.display_name || selectedLinkType.target_type_name || 'Unknown'}</p>
                    <p>
                      <strong>Cardinality:</strong>{' '}
                      <span style={{ 
                        color: selectedLinkType.cardinality === 'MANY_TO_MANY' ? '#722ed1' : '#1890ff',
                        fontWeight: 500 
                      }}>
                        {selectedLinkType.cardinality || 'N/A'}
                      </span>
                    </p>
                    {selectedLinkType.cardinality === 'MANY_TO_MANY' && (
                      <p style={{ color: '#722ed1', marginTop: 8, fontSize: 12 }}>
                        <strong>M:N Relation:</strong> Uses join table with keys:{' '}
                        <code style={{ background: '#f0e6ff', padding: '2px 4px', borderRadius: 3 }}>
                          {selectedLinkType.source_key_column || 'source_key'}
                        </code>
                        {' ↔ '}
                        <code style={{ background: '#f0e6ff', padding: '2px 4px', borderRadius: 3 }}>
                          {selectedLinkType.target_key_column || 'target_key'}
                        </code>
                      </p>
                    )}
                  </Card>
                )}
              </div>
            )}

            {/* Function Selection - for function_logic */}
            {showFunctionSelection && (
              <div style={{ marginBottom: 24 }}>
                <h4>Backing Function</h4>
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Select the function that will be executed when this action is triggered.
                </p>
                <Select
                  placeholder="Select Function"
                  value={selectedFunction?.id}
                  onChange={handleFunctionChange}
                  style={{ width: '100%', marginBottom: 16 }}
                  showSearch
                  optionFilterProp="children"
                >
                  {functions.map((fn) => (
                    <Select.Option key={fn.id} value={fn.id}>
                      {fn.display_name} ({fn.api_name})
                    </Select.Option>
                  ))}
                </Select>
                
                {selectedFunction && (
                  <Card size="small" style={{ background: '#f6f8fa' }}>
                    <p><strong>API Name:</strong> <code style={{ background: '#e8e8e8', padding: '2px 6px', borderRadius: 4 }}>{selectedFunction.api_name}</code></p>
                    <p><strong>Output Type:</strong> {selectedFunction.output_type}</p>
                    {selectedFunction.description && (
                      <p><strong>Description:</strong> {selectedFunction.description}</p>
                    )}
                  </Card>
                )}
              </div>
            )}

            <div style={{ marginBottom: 24 }}>
              <h4>Parameter Definitions</h4>
              {showLinkTypeSelection && (
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  For link operations, parameters typically include source and target object IDs.
                </p>
              )}
              {showFunctionSelection && (
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Define input parameters for the action. These will be passed to the backing function.
                </p>
              )}
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
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Define validation rules for action parameters.
                </p>
                <div>
                  {validationRules.param_validation.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Select
                          placeholder="Select Parameter"
                          value={rule.target_field || undefined}
                          onChange={(value) =>
                            updateValidationRule('param_validation', index, 'target_field', value)
                          }
                          style={{ width: '100%' }}
                        >
                          {parameters.map((p) => (
                            <Select.Option key={p.api_id} value={p.api_id}>
                              {p.display_name} ({p.api_id})
                            </Select.Option>
                          ))}
                        </Select>
                        <Input
                          placeholder="Expression (e.g., value > 0, value != null)"
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
                    disabled={parameters.length === 0}
                  >
                    Add Rule
                  </Button>
                  {parameters.length === 0 && (
                    <p style={{ color: '#faad14', marginTop: 8 }}>
                      Please define parameters in Parameters & Mapping tab first.
                    </p>
                  )}
                </div>
              </TabPane>
              <TabPane tab="Pre-condition" key="pre_condition">
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Define conditions that must be true before the action executes (based on object properties).
                </p>
                <div>
                  {validationRules.pre_condition.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Select
                          placeholder="Select Object Property"
                          value={rule.target_field || undefined}
                          onChange={(value) =>
                            updateValidationRule('pre_condition', index, 'target_field', value)
                          }
                          style={{ width: '100%' }}
                        >
                          {objectProperties.map((prop) => (
                            <Select.Option key={prop.key} value={prop.key}>
                              {prop.label} ({prop.type})
                            </Select.Option>
                          ))}
                        </Select>
                        <Input
                          placeholder="Expression (e.g., value == 'Active', value > 0)"
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
                    disabled={objectProperties.length === 0}
                  >
                    Add Rule
                  </Button>
                  {objectProperties.length === 0 && (
                    <p style={{ color: '#faad14', marginTop: 8 }}>
                      No object properties available. Please select a target object type with properties.
                    </p>
                  )}
                </div>
              </TabPane>
              <TabPane tab="Post-condition" key="post_condition">
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Define conditions that must be true after the action executes (based on object properties).
                </p>
                <div>
                  {validationRules.post_condition.map((rule, index) => (
                    <Card key={index} style={{ marginBottom: 16 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Select
                          placeholder="Select Object Property"
                          value={rule.target_field || undefined}
                          onChange={(value) =>
                            updateValidationRule('post_condition', index, 'target_field', value)
                          }
                          style={{ width: '100%' }}
                        >
                          {objectProperties.map((prop) => (
                            <Select.Option key={prop.key} value={prop.key}>
                              {prop.label} ({prop.type})
                            </Select.Option>
                          ))}
                        </Select>
                        <Input
                          placeholder="Expression (e.g., value > 0, value != null)"
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
                    disabled={objectProperties.length === 0}
                  >
                    Add Rule
                  </Button>
                  {objectProperties.length === 0 && (
                    <p style={{ color: '#faad14', marginTop: 8 }}>
                      No object properties available. Please select a target object type with properties.
                    </p>
                  )}
                </div>
              </TabPane>
            </Tabs>
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

export default ActionEditor;

