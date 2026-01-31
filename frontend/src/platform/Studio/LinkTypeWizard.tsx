/**
 * Link Type Creation Wizard component.
 * Dynamic steps based on Cardinality (2 steps for 1:1/1:N, 3 steps for N:N).
 * 
 * @note V3 Migration: Now uses V3 API for create operations.
 */
import React, { useState, useEffect } from 'react';
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
  Spin,
} from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import { createLinkType } from '../../api/v3/ontology';
import { useParams } from 'react-router-dom';
import { fetchObjectTypes, fetchDatasources } from '../../api/ontology';

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
  connection_id?: string; // V3 field: link to sys_connection
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
  isRequired?: boolean; // FK and PK columns are required
  columnType?: 'PK' | 'FK'; // Column type for display
}

interface LinkTypeWizardProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

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
  
  // API data state
  const [objectTypes, setObjectTypes] = useState<ObjectType[]>([]);
  const [rawTables, setRawTables] = useState<RawTable[]>([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataError, setDataError] = useState<string | null>(null);

  // Load object types and datasources when wizard opens
  useEffect(() => {
    if (visible) {
      loadData();
    }
  }, [visible, projectId]);

  const loadData = async () => {
    setDataLoading(true);
    setDataError(null);
    
    try {
      const [objectTypesData, datasourcesData] = await Promise.all([
        fetchObjectTypes(projectId),
        fetchDatasources(),
      ]);
      
      // Convert to component's interface format
      const convertedObjectTypes: ObjectType[] = objectTypesData.map((ot) => ({
        id: ot.id,
        api_name: ot.api_name,
        display_name: ot.display_name,
        property_schema: ot.property_schema as Record<string, string> | undefined,
      }));
      
      // Parse columns_schema if it's a string
      const convertedTables: RawTable[] = datasourcesData.map((ds) => {
        let columnsSchema = ds.columns_schema;
        if (typeof columnsSchema === 'string') {
          try {
            columnsSchema = JSON.parse(columnsSchema);
          } catch {
            columnsSchema = [];
          }
        }
        return {
          id: ds.id,
          connection_id: ds.connection_id, // Preserve connection_id for N:N mapping
          table_name: ds.table_name,
          db_type: ds.db_type,
          columns_schema: Array.isArray(columnsSchema) ? columnsSchema : [],
        };
      });
      
      setObjectTypes(convertedObjectTypes);
      setRawTables(convertedTables);
    } catch (error) {
      console.error('Failed to load data:', error);
      setDataError('加载数据失败，请检查网络连接后重试');
    } finally {
      setDataLoading(false);
    }
  };

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
    return objectTypes.find((ot) => ot.id === sourceTypeId);
  };

  // Get target object type
  const getTargetObjectType = (): ObjectType | undefined => {
    const targetTypeId = form.getFieldValue('target_type_id');
    return objectTypes.find((ot) => ot.id === targetTypeId);
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
    const table = rawTables.find((t) => t.id === tableId);
    setSelectedJoinTable(table || null);
    
    if (table) {
      // Reset key mappings when join table changes
      form.setFieldsValue({
        source_key_mapping: undefined,
        target_key_mapping: undefined,
      });
      // Initialize link properties with all columns (will be filtered after key mapping selection)
      updateLinkProperties(table, undefined, undefined);
    }
  };

  // Update link properties based on selected key mappings
  const updateLinkProperties = (table: RawTable, sourceKey?: string, targetKey?: string) => {
    if (!table) return;
    
    // Get FK columns and PK column
    const fkColumns = [sourceKey, targetKey].filter(Boolean) as string[];
    const pkColumn = 'id'; // Primary key column name
    
    // Include all columns, but mark FK and PK columns as required (non-editable)
    const properties: LinkPropertyMapping[] = table.columns_schema.map((col) => {
      const isFk = fkColumns.includes(col.name);
      const isPk = col.name === pkColumn;
      const isRequired = isFk || isPk;
      
      return {
        column: col.name,
        displayName: col.name,
        dataType: mapColumnTypeToDataType(col.type),
        include: true, // All columns default to include
        isRequired, // Mark FK and PK columns as required (cannot be toggled off)
        columnType: isPk ? 'PK' : isFk ? 'FK' : undefined, // Column type for display
      };
    });
    setLinkProperties(properties);
  };

  // Handle source key mapping change
  const handleSourceKeyChange = (value: string) => {
    const targetKey = form.getFieldValue('target_key_mapping');
    if (selectedJoinTable) {
      updateLinkProperties(selectedJoinTable, value, targetKey);
    }
  };

  // Handle target key mapping change
  const handleTargetKeyChange = (value: string) => {
    const sourceKey = form.getFieldValue('source_key_mapping');
    if (selectedJoinTable) {
      updateLinkProperties(selectedJoinTable, sourceKey, value);
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
          // First validate join table selection
          await form.validateFields(['join_table_id']);
          
          // Only validate key mappings if a join table is selected (which means the fields are rendered)
          if (selectedJoinTable) {
            await form.validateFields(['source_key_mapping', 'target_key_mapping']);
          } else {
            message.error('Please select a join table first');
            return false;
          }
        } else {
          // Validate non-N:N relationships
          await form.validateFields(['source_property', 'target_property']);
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

  // Handle create (using V3 API)
  const handleCreate = async () => {
    const isValid = await validateStep();
    if (!isValid) return;

    // Get all form values first
    const values = form.getFieldsValue();
    
    // Debug: log form values
    console.log('[LinkTypeWizard] Form values:', values);
    console.log('[LinkTypeWizard] Cardinality:', cardinality);

    // Validate required fields before API call
    if (!values.source_type_id || !values.target_type_id) {
      message.error('Source and target object types are required');
      console.error('[LinkTypeWizard] Missing source_type_id or target_type_id');
      return;
    }
    if (!values.api_name) {
      message.error('API name is required');
      console.error('[LinkTypeWizard] Missing api_name');
      return;
    }

    try {
      setLoading(true);

      // Use V3 API for creation
      console.log('[LinkTypeWizard] Calling createLinkType API...');
      const result = await createLinkType(
        {
          api_name: values.api_name,
          description: values.description || null,
        },
        values.source_type_id,
        values.target_type_id,
        cardinality,
        values.display_name || values.api_name
      );
      console.log('[LinkTypeWizard] API response:', result);
      
      message.success('Link type created successfully');
      onSuccess();
      handleCancel();
    } catch (error: any) {
      console.error('[LinkTypeWizard] API error:', error);
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error format
        const errorMsg = detail.map((d: any) => `${d.loc?.join('.')}: ${d.msg}`).join('; ');
        message.error(errorMsg || 'Validation failed');
      } else {
        message.error(detail || 'Failed to create link type');
      }
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
      width: 180,
      render: (text: string, record: LinkPropertyMapping) => (
        <Space>
          <span style={{ fontFamily: 'monospace' }}>{text}</span>
          {record.columnType && (
            <span style={{ 
              fontSize: 10, 
              padding: '2px 6px', 
              borderRadius: 4,
              backgroundColor: record.columnType === 'PK' ? '#722ed1' : '#1890ff',
              color: '#fff',
              fontWeight: 500,
            }}>
              {record.columnType}
            </span>
          )}
        </Space>
      ),
    },
    {
      title: 'Logical Display Name',
      key: 'displayName',
      width: 180,
      render: (_: any, record: LinkPropertyMapping, index: number) => (
        <Input
          value={record.displayName}
          onChange={(e) => handleLinkPropertyChange(index, 'displayName', e.target.value)}
          placeholder="Display name"
          disabled={record.isRequired} // FK and PK columns cannot be renamed
        />
      ),
    },
    {
      title: 'Data Type',
      key: 'dataType',
      width: 130,
      render: (_: any, record: LinkPropertyMapping, index: number) => (
        <Select
          value={record.dataType}
          onChange={(value) => handleLinkPropertyChange(index, 'dataType', value)}
          style={{ width: '100%' }}
          disabled={record.isRequired} // FK and PK columns cannot change type
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
          disabled={record.isRequired} // FK and PK columns must be included
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
      {dataLoading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" tip="加载数据中..." />
        </div>
      ) : dataError ? (
        <Alert
          message="加载失败"
          description={dataError}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={loadData}>
              重试
            </Button>
          }
        />
      ) : (
        <>
          <Steps current={currentStep} style={{ marginBottom: 24 }}>
            <Step title="Definition" />
            <Step title={isManyToMany ? 'Join Table & Keys' : 'Connection Mapping'} />
            {isManyToMany && <Step title="Link Properties" />}
          </Steps>

          {/* Form wraps all steps to preserve values across step navigation */}
          <Form form={form} layout="vertical" preserve={true}>
            {/* Step 1: Definition - use display:none instead of conditional rendering to preserve values */}
            <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
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
                      {objectTypes.map((ot) => (
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
                      {objectTypes.map((ot) => (
                        <Select.Option key={ot.id} value={ot.id}>
                          {ot.display_name}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                </div>
              </Form.Item>
            </div>

            {/* Step 2: Connection Mapping - use display:none to preserve values */}
            <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
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
                  {rawTables.map((table) => (
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
                      <Select 
                        placeholder="Map Source Object PK to Join Table Column"
                        onChange={handleSourceKeyChange}
                      >
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
                      <Select 
                        placeholder="Map Target Object PK to Join Table Column"
                        onChange={handleTargetKeyChange}
                      >
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

            {/* Step 3: Link Properties (Only for N:N) - use display:none to preserve values */}
            <div style={{ display: currentStep === 2 && isManyToMany ? 'block' : 'none' }}>
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
          </Form>

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
        </>
      )}
    </Modal>
  );
};

export default LinkTypeWizard;
