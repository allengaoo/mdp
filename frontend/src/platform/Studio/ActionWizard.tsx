/**
 * Action Definition Wizard component.
 * 4-step wizard for creating new action definitions.
 * 
 * @todo V3 Migration: This component still uses V1 API.
 * Migrate to V3 when backend Action endpoints are implemented.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Steps,
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
import { useParams } from 'react-router-dom';
import { 
  fetchProjectObjectTypes, 
  fetchObjectTypeProperties,
  fetchObjectTypes as fetchAllObjectTypes,
  fetchLinkTypes,
  fetchProjectLinkTypes,
} from '../../api/v3/ontology';
import { IV3ObjectTypeFull, IV3LinkTypeFull } from '../../api/v3/types';
import { 
  createActionDefinition, 
  IActionDefinitionCreate, 
  fetchFunctionsForList,
  IFunctionDef,
} from '../../api/v3/logic';

const { TextArea } = Input;
const { Step } = Steps;
const { TabPane } = Tabs;

interface ActionWizardProps {
  visible: boolean;
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
  target_field: string; // Parameter api_id for param_validation, property key for pre/post condition
  expression: string;
  error_message: string;
}

interface ObjectProperty {
  key: string;
  label: string;
  type: string;
}

// Use V3 object type interface
type ObjectTypeData = IV3ObjectTypeFull;

const OPERATION_TYPES = [
  { value: 'update_property', label: 'Update Property', icon: EditOutlined, color: '#1890ff' },
  { value: 'link_objects', label: 'Link Objects', icon: LinkOutlined, color: '#722ed1' },
  { value: 'unlink_objects', label: 'Unlink Objects', icon: DisconnectOutlined, color: '#fa8c16' },
  { value: 'function_logic', label: 'Function Logic', icon: CodeOutlined, color: '#13c2c2' },
];

const ActionWizard: React.FC<ActionWizardProps> = ({ visible, onCancel, onSuccess }) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  // Target scope is always 'specific' - only specific object actions are supported
  const [targetScope] = useState<'specific'>('specific');
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

  // Fetch object types - use V3 API
  // In Ontology Studio: only show project-bound object types
  // In Actions & Logic menu: show all object types (to be implemented separately)
  useEffect(() => {
    const loadObjectTypes = async () => {
      try {
        if (projectId) {
          // Ontology Studio context: fetch project-bound object types only
          const data = await fetchProjectObjectTypes(projectId);
          setObjectTypes(data);
        } else {
          // Global context (Actions & Logic): fetch all object types
          const data = await fetchAllObjectTypes();
          setObjectTypes(data);
        }
      } catch (error) {
        console.error('Failed to fetch object types:', error);
        setObjectTypes([]);
      }
    };
    if (visible) {
      loadObjectTypes();
    }
  }, [visible, projectId]);

  // Fetch link types - for link_objects/unlink_objects operations
  useEffect(() => {
    const loadLinkTypes = async () => {
      try {
        if (projectId) {
          // Ontology Studio context: fetch project-related link types only
          const data = await fetchProjectLinkTypes(projectId);
          setLinkTypes(data);
        } else {
          // Global context (Actions & Logic): fetch all link types
          const data = await fetchLinkTypes();
          setLinkTypes(data);
        }
      } catch (error) {
        console.error('Failed to fetch link types:', error);
        setLinkTypes([]);
      }
    };
    if (visible) {
      loadLinkTypes();
    }
  }, [visible, projectId]);

  // Fetch functions - for function_logic operation
  useEffect(() => {
    const loadFunctions = async () => {
      try {
        const data = await fetchFunctionsForList();
        setFunctions(data);
      } catch (error) {
        console.error('Failed to fetch functions:', error);
        setFunctions([]);
      }
    };
    if (visible) {
      loadFunctions();
    }
  }, [visible]);

  // Fetch object properties when object type is selected - use V3 API
  const loadObjectProperties = async (objectTypeId: string) => {
    try {
      const data = await fetchObjectTypeProperties(objectTypeId);
      const props: ObjectProperty[] = data.map((prop: any) => ({
        key: prop.api_name || prop.local_api_name || prop.property_def_id,
        label: prop.display_name || prop.api_name || prop.local_api_name || prop.property_def_id,
        type: prop.data_type || 'string',
      }));
      setObjectProperties(props);
    } catch (error) {
      console.error('Failed to fetch object properties:', error);
      setObjectProperties([]);
    }
  };

  // Get object properties for rendering (use state instead of computing from property_schema)
  const getObjectProperties = (): ObjectProperty[] => {
    return objectProperties;
  };

  // Handle next step
  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['display_name', 'api_name', 'description']);
        const values = form.getFieldsValue();
        if (targetScope === 'specific' && !values.target_object_type_id) {
          message.error('Please select a target object type');
          return;
        }
        if (targetScope === 'specific') {
          const objType = objectTypes.find((ot) => ot.id === values.target_object_type_id);
          setSelectedObjectType(objType || null);
        }
      } else if (currentStep === 1) {
        if (!selectedOperationType) {
          message.error('Please select an operation type');
          return;
        }
      } else if (currentStep === 2) {
        // Validate based on operation type
        if (selectedOperationType === 'update_property') {
          // update_property requires property mapping
          if (propertyMappings.length === 0) {
            message.error('Please add at least one property mapping for update_property action');
            return;
          }
        } else if (showLinkTypeSelection) {
          // link_objects/unlink_objects require link type selection
          if (!selectedLinkType) {
            message.error('Please select a link type');
            return;
          }
        } else if (showFunctionSelection) {
          // function_logic requires backing function
          if (!selectedFunction) {
            message.error('Please select a backing function');
            return;
          }
        }
        
        // General parameter validation (except for link operations which auto-generate)
        if (parameters.length === 0 && !showLinkTypeSelection) {
          message.warning('No parameters defined. You can add parameters or continue.');
        }
      }
      setCurrentStep(currentStep + 1);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  // Handle previous step
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // Handle finish - create action definition using V3 API
  const handleFinish = async () => {
    try {
      const values = form.getFieldsValue();
      
      // Construct payload for V3 API
      const payload: IActionDefinitionCreate = {
        display_name: values.display_name,
        api_name: values.api_name,
        description: values.description || undefined,
        operation_type: selectedOperationType || undefined,
        target_object_type_id: values.target_object_type_id || undefined,
        // Add link_type_id for link_objects/unlink_objects operations
        link_type_id: showLinkTypeSelection && selectedLinkType ? selectedLinkType.id : undefined,
        // Add backing_function_id for function_logic operations
        backing_function_id: showFunctionSelection && selectedFunction ? selectedFunction.id : undefined,
        // Convert parameters to API format (data_type -> type)
        parameters_schema: parameters.length > 0 
          ? parameters.map(p => ({
              api_id: p.api_id,
              display_name: p.display_name,
              type: p.data_type,
              required: p.required,
            }))
          : undefined,
        property_mapping: propertyMappings.length > 0 
          ? propertyMappings.reduce((acc, m) => {
              acc[m.param_key] = m.property_key;
              return acc;
            }, {} as Record<string, string>) 
          : undefined,
        validation_rules: (validationRules.param_validation.length > 0 || 
                          validationRules.pre_condition.length > 0 || 
                          validationRules.post_condition.length > 0)
          ? {
              param_validation: validationRules.param_validation,
              pre_condition: validationRules.pre_condition,
              post_condition: validationRules.post_condition,
            }
          : undefined,
        // project_id is optional - will be set if in project context
        project_id: projectId || undefined,
      };

      await createActionDefinition(payload);
      message.success('Action definition created successfully');
      onSuccess();  // Close modal first
      handleReset(); // Then reset form for next use
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to create action definition';
      message.error(errorMsg);
      console.error('Create action definition failed:', error);
    }
  };

  // Reset form
  const handleReset = () => {
    form.resetFields();
    setCurrentStep(0);
    setSelectedOperationType('');
    setSelectedObjectType(null);
    setObjectProperties([]);
    setSelectedLinkType(null);
    setSelectedFunction(null);
    setParameters([]);
    setPropertyMappings([]);
    setValidationRules({
      param_validation: [],
      pre_condition: [],
      post_condition: [],
    });
  };

  // Handle cancel
  const handleCancel = () => {
    handleReset();
    onCancel();
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

  // Auto-generate API name from display name
  const handleDisplayNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const displayName = e.target.value;
    const apiName = displayName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    form.setFieldsValue({ api_name: apiName });
  };

  // Check if property mapping should be shown
  const showPropertyMapping =
    selectedObjectType && selectedOperationType === 'update_property';

  // Check if link type selection should be shown
  const showLinkTypeSelection =
    selectedOperationType === 'link_objects' || selectedOperationType === 'unlink_objects';

  // Check if function selection should be shown
  const showFunctionSelection = selectedOperationType === 'function_logic';

  // Handle function selection
  const handleFunctionChange = (functionId: string) => {
    const func = functions.find((f) => f.id === functionId);
    setSelectedFunction(func || null);
    // Note: Parameters can be manually defined for function_logic
    // We don't auto-generate from function schema here
  };

  // Handle link type selection - auto-generate parameters
  const handleLinkTypeChange = (linkTypeId: string) => {
    const linkType = linkTypes.find((lt) => lt.id === linkTypeId);
    setSelectedLinkType(linkType || null);
    
    if (linkType) {
      // Auto-generate source_object_id and target_object_id parameters
      const sourceTypeName = objectTypes.find(ot => ot.id === linkType.source_object_def_id)?.display_name || 'Source';
      const targetTypeName = objectTypes.find(ot => ot.id === linkType.target_object_def_id)?.display_name || 'Target';
      
      setParameters([
        {
          display_name: `${sourceTypeName} ID`,
          api_id: 'source_object_id',
          data_type: 'object_ref',
          required: true,
        },
        {
          display_name: `${targetTypeName} ID`,
          api_id: 'target_object_id',
          data_type: 'object_ref',
          required: true,
        },
      ]);
    }
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
      title="Create Action Definition"
      open={visible}
      onCancel={handleCancel}
      width={900}
      footer={null}
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="Basic Info" />
        <Step title="Operation Type" />
        <Step title="Parameters & Mapping" />
        <Step title="Validations" />
      </Steps>

      <Form form={form} layout="vertical" preserve={true}>
        {/* Step 1: Basic Info - use CSS hiding to preserve form values */}
        <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
            <Form.Item
              label="Display Name"
              name="display_name"
              rules={[{ required: true, message: 'Please enter display name' }]}
            >
              <Input placeholder="Action Name" onChange={handleDisplayNameChange} />
            </Form.Item>

            <Form.Item
              label="API Identifier"
              name="api_name"
              rules={[{ required: true, message: 'Please enter API identifier' }]}
            >
              <Input placeholder="api_identifier" style={{ fontFamily: 'monospace' }} />
            </Form.Item>

            <Form.Item label="Description" name="description">
              <TextArea rows={3} placeholder="Action description" />
            </Form.Item>

            {/* Target Object Type - only specific object actions are supported */}
            <Form.Item
              label="Target Object Type"
              name="target_object_type_id"
              rules={[{ required: true, message: 'Please select target object type' }]}
            >
              <Select 
                placeholder="Select Object Type"
                onChange={(value) => {
                  const objType = objectTypes.find((ot) => ot.id === value);
                  setSelectedObjectType(objType || null);
                  // Fetch object properties from V3 API
                  if (value) {
                    loadObjectProperties(value);
                  } else {
                    setObjectProperties([]);
                  }
                }}
              >
                {objectTypes.map((ot) => (
                  <Select.Option key={ot.id} value={ot.id}>
                    {ot.display_name || ot.api_name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
        </div>

        {/* Step 2: Operation Type - use CSS hiding */}
        <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
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
        </div>

        {/* Step 3: Parameters & Mapping - use CSS hiding */}
        <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
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
                
                {!selectedFunction && (
                  <p style={{ color: '#faad14', marginTop: 8 }}>
                    Please select a backing function to continue.
                  </p>
                )}
              </div>
            )}

            {/* Parameter Definitions */}
            <div style={{ marginBottom: 24 }}>
              <h4>Parameter Definitions</h4>
              {showLinkTypeSelection && (
                <p style={{ color: '#8c8c8c', marginBottom: 16 }}>
                  Parameters are auto-generated based on the selected link type.
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
                footer={!showLinkTypeSelection ? () => (
                  <Button type="dashed" icon={<PlusOutlined />} onClick={addParameter} block>
                    Add Parameter
                  </Button>
                ) : undefined}
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

            {/* Info message for link operations */}
            {showLinkTypeSelection && !selectedLinkType && (
              <p style={{ color: '#faad14', marginTop: 8 }}>
                Please select a link type to continue.
              </p>
            )}
        </div>

        {/* Step 4: Validations - use CSS hiding */}
        <div style={{ display: currentStep === 3 ? 'block' : 'none' }}>
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
                      Please define parameters in Step 3 first.
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
        </div>

        {/* Footer Buttons */}
        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={handleCancel}>Cancel</Button>
          <Space>
            {currentStep > 0 && <Button onClick={handlePrev}>Previous</Button>}
            {currentStep < 3 ? (
              <Button type="primary" onClick={handleNext}>
                Next
              </Button>
            ) : (
              <Button type="primary" onClick={handleFinish}>
                Create
              </Button>
            )}
          </Space>
        </div>
      </Form>
    </Modal>
  );
};

export default ActionWizard;

