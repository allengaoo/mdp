/**
 * Object Type Creation Wizard component.
 * 3-step wizard for creating new object types.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Steps,
  Form,
  Input,
  Button,
  Alert,
  Tabs,
  Upload,
  Table,
  Select,
  Space,
  message,
} from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { useParams } from 'react-router-dom';
import {
  fetchDatasources,
  fetchSharedProperties,
  createObjectType,
  IDataSourceTable,
  ISharedProperty,
} from '../../api/ontology';

const { Step } = Steps;
const { TextArea } = Input;
const { Dragger } = Upload;

interface PropertyMapping {
  rawColumn: string;
  propertyName: string;
  type: string;
  useSharedProperty?: string;
}

interface ObjectTypeWizardProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}


const ObjectTypeWizard: React.FC<ObjectTypeWizardProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedDataSource, setSelectedDataSource] = useState<IDataSourceTable | null>(null);
  const [availableColumns, setAvailableColumns] = useState<IDataSourceTable['columns_schema']>([]);
  const [primaryKey, setPrimaryKey] = useState<string>('');
  const [propertyMappings, setPropertyMappings] = useState<PropertyMapping[]>([]);
  const [uploadedColumns, setUploadedColumns] = useState<IDataSourceTable['columns_schema']>([]);
  const [loading, setLoading] = useState(false);
  const [datasources, setDatasources] = useState<IDataSourceTable[]>([]);
  const [sharedProperties, setSharedProperties] = useState<ISharedProperty[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  // Store form values from Step 1 to ensure they're available when creating
  const [step1Values, setStep1Values] = useState<{ api_name?: string; display_name?: string; description?: string }>({});

  // Fetch datasources and shared properties on mount
  useEffect(() => {
    if (visible) {
      const loadData = async () => {
        try {
          setLoadingData(true);
          const [datasourcesData, sharedPropsData] = await Promise.all([
            fetchDatasources(),
            fetchSharedProperties(),
          ]);
          setDatasources(datasourcesData);
          setSharedProperties(sharedPropsData);
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to load data');
        } finally {
          setLoadingData(false);
        }
      };
      loadData();
    }
  }, [visible, projectId]);

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
    const apiName = convertToApiName(displayName);
    form.setFieldsValue({ api_name: apiName });
    // Save to state for later use
    setStep1Values((prev: { api_name?: string; display_name?: string; description?: string }) => ({ ...prev, display_name: displayName, api_name: apiName }));
  };

  // Handle API name change
  const handleApiNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const apiName = e.target.value;
    setStep1Values((prev: { api_name?: string; display_name?: string; description?: string }) => ({ ...prev, api_name: apiName }));
  };

  // Handle description change
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const description = e.target.value;
    setStep1Values((prev: { api_name?: string; display_name?: string; description?: string }) => ({ ...prev, description }));
  };

  // Handle data source selection
  const handleDataSourceSelect = (record: IDataSourceTable) => {
    setSelectedDataSource(record);
    // Parse columns_schema if it's a string
    const columns = Array.isArray(record.columns_schema)
      ? record.columns_schema
      : typeof record.columns_schema === 'string'
      ? JSON.parse(record.columns_schema)
      : [];
    setAvailableColumns(columns);
    // Initialize property mappings
    const mappings: PropertyMapping[] = columns.map((col: { name: string; type: string }) => ({
      rawColumn: col.name,
      propertyName: col.name,
      type: mapColumnTypeToPropertyType(col.type),
      useSharedProperty: undefined,
    }));
    setPropertyMappings(mappings);
  };

  // Map database column type to property type
  const mapColumnTypeToPropertyType = (dbType: string): string => {
    const typeMap: Record<string, string> = {
      varchar: 'string',
      int: 'number',
      decimal: 'number',
      datetime: 'datetime',
      json: 'array',
      text: 'string',
    };
    return typeMap[dbType.toLowerCase()] || 'string';
  };

  // Infer data type from CSV value
  const inferDataType = (value: string): string => {
    if (!value || value.trim() === '') return 'varchar';
    const trimmed = value.trim();
    
    // Check for integer
    if (/^-?\d+$/.test(trimmed)) return 'int';
    
    // Check for float/double
    if (/^-?\d+\.\d+$/.test(trimmed)) return 'decimal';
    
    // Check for boolean
    if (/^(true|false|yes|no|1|0)$/i.test(trimmed)) return 'boolean';
    
    // Check for datetime (ISO format or common date formats)
    if (/^\d{4}-\d{2}-\d{2}(T|\s)\d{2}:\d{2}:\d{2}/.test(trimmed)) return 'datetime';
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return 'date';
    
    // Default to varchar with estimated length
    const len = trimmed.length;
    return len > 255 ? 'text' : 'varchar';
  };

  // Parse CSV file and extract columns with type inference
  const parseCSVFile = (file: File): Promise<Array<{ name: string; type: string; length?: number }>> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          const lines = text.split(/\r?\n/).filter(line => line.trim());
          
          if (lines.length === 0) {
            reject(new Error('CSV file is empty'));
            return;
          }

          // Parse header line
          const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
          
          // Analyze first few data rows to infer types
          const sampleRows = lines.slice(1, Math.min(6, lines.length));
          const columnTypes: Record<string, string[]> = {};
          
          headers.forEach(header => {
            columnTypes[header] = [];
          });

          sampleRows.forEach(row => {
            // Simple CSV parsing (handles basic cases, not quoted commas)
            const values = row.split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
            headers.forEach((header, idx) => {
              if (values[idx] !== undefined) {
                columnTypes[header].push(inferDataType(values[idx]));
              }
            });
          });

          // Determine final type for each column (most common non-varchar type)
          const columns = headers.map(header => {
            const types = columnTypes[header];
            const typeCounts: Record<string, number> = {};
            types.forEach(t => {
              typeCounts[t] = (typeCounts[t] || 0) + 1;
            });
            
            // Find most common type, preferring specific types over varchar
            let finalType = 'varchar';
            let maxCount = 0;
            Object.entries(typeCounts).forEach(([type, count]) => {
              if (type !== 'varchar' && count >= maxCount) {
                finalType = type;
                maxCount = count;
              }
            });
            
            // If all values are varchar or empty, use varchar
            if (maxCount === 0) finalType = 'varchar';

            return {
              name: header.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
              type: finalType,
              length: finalType === 'varchar' ? 255 : undefined,
            };
          });

          resolve(columns);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  // Handle CSV upload - real parsing
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.csv',
    beforeUpload: async (file) => {
      try {
        const columns = await parseCSVFile(file);
        
        if (columns.length === 0) {
          message.error('No columns found in CSV file');
          return false;
        }

        setUploadedColumns(columns);
        setAvailableColumns(columns);
        const mappings: PropertyMapping[] = columns.map((col) => ({
          rawColumn: col.name,
          propertyName: col.name,
          type: mapColumnTypeToPropertyType(col.type),
          useSharedProperty: undefined,
        }));
        setPropertyMappings(mappings);
        message.success(`成功解析 ${file.name}，检测到 ${columns.length} 个列`);
      } catch (err: any) {
        message.error(`解析 CSV 失败: ${err.message || '未知错误'}`);
      }
      return false; // Prevent actual upload
    },
  };

  // Handle shared property selection
  const handleSharedPropertyChange = (index: number, sharedPropApiName: string) => {
    const sharedProp = sharedProperties.find((p) => p.api_name === sharedPropApiName);
    if (sharedProp) {
      const newMappings = [...propertyMappings];
      newMappings[index] = {
        ...newMappings[index],
        useSharedProperty: sharedPropApiName,
        propertyName: sharedProp.api_name,
        type: mapSharedPropertyTypeToPropertyType(sharedProp.data_type),
      };
      setPropertyMappings(newMappings);
    }
  };

  // Map shared property data_type to property type
  const mapSharedPropertyTypeToPropertyType = (dataType: string): string => {
    const typeMap: Record<string, string> = {
      STRING: 'string',
      INTEGER: 'number',
      DOUBLE: 'number',
      BOOLEAN: 'boolean',
      DATE: 'datetime',
      GEOPOINT: 'geopoint',
      NUMBER: 'number',
    };
    return typeMap[dataType.toUpperCase()] || 'string';
  };

  // Handle property mapping changes
  const handlePropertyMappingChange = (index: number, field: keyof PropertyMapping, value: any) => {
    const newMappings = [...propertyMappings];
    newMappings[index] = {
      ...newMappings[index],
      [field]: value,
    };
    setPropertyMappings(newMappings);
  };

  // Validate current step
  const validateStep = async (): Promise<boolean> => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['display_name', 'api_name', 'description']);
        return true;
      } else if (currentStep === 1) {
        if (availableColumns.length === 0) {
          message.error('Please select a data source or upload a CSV file');
          return false;
        }
        return true;
      } else if (currentStep === 2) {
        if (!primaryKey) {
          message.error('Please select a primary key');
          return false;
        }
        // Validate that PK is mapped
        const pkMapping = propertyMappings.find((m) => m.rawColumn === primaryKey);
        if (!pkMapping || !pkMapping.propertyName) {
          message.error('Primary key must be mapped to a property');
          return false;
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
      
      // Get form values - use saved step1Values if form fields are not available
      const formValues = form.getFieldsValue();
      const values = {
        api_name: formValues.api_name || step1Values.api_name,
        display_name: formValues.display_name || step1Values.display_name,
        description: formValues.description || step1Values.description,
      };

      // Validate required fields
      if (!values.api_name || !values.display_name) {
        message.error('Please complete all required fields in Step 1');
        setCurrentStep(0); // Go back to Step 1
        return;
      }

      // Build property_schema from mappings (convert to PropertyDef array format)
      const propertySchema = propertyMappings
        .filter((mapping) => mapping.propertyName && mapping.type)
        .map((mapping) => {
          // Convert property type to uppercase (e.g., 'string' -> 'STRING')
          const typeUpper = mapping.type.toUpperCase();
          // Find shared property ID if useSharedProperty is set (it's API name, need to find ID)
          let sharedPropertyId: string | undefined = undefined;
          if (mapping.useSharedProperty) {
            const sharedProp = sharedProperties.find((p) => p.api_name === mapping.useSharedProperty);
            sharedPropertyId = sharedProp?.id;
          }
          const propDef: any = {
            key: mapping.propertyName,
            label: mapping.propertyName, // Use property name as label for now
            type: typeUpper,
            required: mapping.rawColumn === primaryKey, // PK is required
          };
          // Only add shared_property_id if it exists
          if (sharedPropertyId) {
            propDef.shared_property_id = sharedPropertyId;
          }
          return propDef;
        });

      // Ensure required fields are present
      if (!values.api_name || !values.display_name) {
        message.error('API Name and Display Name are required');
        setCurrentStep(0); // Go back to Step 1
        return;
      }

      const payload = {
        api_name: values.api_name,
        display_name: values.display_name,
        description: values.description || null,
        property_schema: propertySchema,
        project_id: projectId || null,
      };

      console.log('Creating object type with payload:', JSON.stringify(payload, null, 2));
      await createObjectType(payload);
      message.success('Object type created successfully');
      onSuccess();
      handleCancel();
    } catch (error: any) {
      console.error('Error creating object type:', error);
      console.error('Error response:', error.response?.data);
      // Log validation errors if present
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // FastAPI validation errors
          const validationErrors = error.response.data.detail.map((err: any) => 
            `${err.loc?.join('.')}: ${err.msg}`
          ).join('\n');
          message.error(`Validation failed:\n${validationErrors}`);
        } else {
          message.error(error.response.data.detail);
        }
      } else {
        message.error('Failed to create object type');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    form.resetFields();
    setCurrentStep(0);
    setSelectedDataSource(null);
    setAvailableColumns([]);
    setPrimaryKey('');
    setPropertyMappings([]);
    setUploadedColumns([]);
    setStep1Values({}); // Reset saved values
    onCancel();
  };

  // Data source table columns
  const datasourceColumns = [
    {
      title: 'Table Name',
      dataIndex: 'table_name',
      key: 'table_name',
    },
    {
      title: 'DB Type',
      dataIndex: 'db_type',
      key: 'db_type',
    },
  ];

  // Property mapping table columns
  const mappingColumns = [
    {
      title: 'Raw Column',
      dataIndex: 'rawColumn',
      key: 'rawColumn',
      width: 150,
    },
    {
      title: 'Property Name',
      key: 'propertyName',
      width: 200,
      render: (_: any, record: PropertyMapping, index: number) => (
        <Input
          value={record.propertyName}
          onChange={(e) => handlePropertyMappingChange(index, 'propertyName', e.target.value)}
          disabled={!!record.useSharedProperty}
        />
      ),
    },
    {
      title: 'Type',
      key: 'type',
      width: 120,
      render: (_: any, record: PropertyMapping, index: number) => (
        <Select
          value={record.type}
          onChange={(value) => handlePropertyMappingChange(index, 'type', value)}
          disabled={!!record.useSharedProperty}
          style={{ width: '100%' }}
        >
          <Select.Option value="string">String</Select.Option>
          <Select.Option value="number">Number</Select.Option>
          <Select.Option value="datetime">DateTime</Select.Option>
          <Select.Option value="array">Array</Select.Option>
          <Select.Option value="boolean">Boolean</Select.Option>
        </Select>
      ),
    },
    {
      title: 'Use Shared Property',
      key: 'useSharedProperty',
      width: 200,
      render: (_: any, record: PropertyMapping, index: number) => (
        <Select
          value={record.useSharedProperty}
          onChange={(value) => handleSharedPropertyChange(index, value)}
          allowClear
          placeholder="None"
          style={{ width: '100%' }}
        >
          {sharedProperties.map((prop) => (
            <Select.Option key={prop.api_name} value={prop.api_name}>
              {prop.display_name}
            </Select.Option>
          ))}
        </Select>
      ),
    },
  ];

  return (
    <Modal
      title="Create Object Type"
      open={visible}
      onCancel={handleCancel}
      width={900}
      footer={null}
      destroyOnClose
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="Basic Info" />
        <Step title="Backing Datasource" />
        <Step title="Property Mapping" />
      </Steps>

      {/* Step 1: Basic Info */}
      {currentStep === 0 && (
        <Form form={form} layout="vertical">
          <Form.Item
            name="display_name"
            label="Display Name"
            rules={[{ required: true, message: 'Please enter display name' }]}
          >
            <Input placeholder="e.g., Battle Tank" onChange={handleDisplayNameChange} />
          </Form.Item>
          <Form.Item
            name="api_name"
            label="API Name"
            rules={[{ required: true, message: 'Please enter API name' }]}
          >
            <Input placeholder="e.g., battle_tank" onChange={handleApiNameChange} />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={4} placeholder="Enter description..." onChange={handleDescriptionChange} />
          </Form.Item>
        </Form>
      )}

      {/* Step 2: Backing Datasource */}
      {currentStep === 1 && (
        <div>
          <Alert
            message="Data Source Selection"
            description="The Ontology layer abstracts logical entities from raw data sources. Select a data source or upload a CSV file to define the column structure."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Tabs>
            <Tabs.TabPane tab="Upload CSV" key="csv">
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">Click or drag file to this area to upload</p>
                <p className="ant-upload-hint">Support for CSV files only</p>
              </Dragger>
              {uploadedColumns.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <p>Detected columns:</p>
                  <ul>
              {Array.isArray(uploadedColumns) && uploadedColumns.map((col: { name: string; type: string }) => (
                <li key={col.name}>
                  {col.name} ({col.type})
                </li>
              ))}
                  </ul>
                </div>
              )}
            </Tabs.TabPane>
            <Tabs.TabPane tab="Select from Catalog" key="catalog">
              {loadingData ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading datasources...</div>
              ) : (
                <Table
                  columns={datasourceColumns}
                  dataSource={datasources}
                  rowKey="id"
                  rowSelection={{
                    type: 'radio',
                    selectedRowKeys: selectedDataSource ? [selectedDataSource.id] : [],
                    onSelect: (record) => handleDataSourceSelect(record),
                  }}
                  pagination={false}
                  loading={loadingData}
                />
              )}
            </Tabs.TabPane>
          </Tabs>
        </div>
      )}

      {/* Step 3: Property Mapping */}
      {currentStep === 2 && (
        <div>
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: 'block', marginBottom: 8 }}>Primary Key:</label>
            <Select
              value={primaryKey}
              onChange={setPrimaryKey}
              style={{ width: '100%' }}
              placeholder="Select primary key column"
            >
              {Array.isArray(availableColumns) && availableColumns.map((col: { name: string; type: string }) => (
                <Select.Option key={col.name} value={col.name}>
                  {col.name} ({col.type})
                </Select.Option>
              ))}
            </Select>
          </div>
          <Table
            columns={mappingColumns}
            dataSource={propertyMappings}
            rowKey="rawColumn"
            pagination={false}
            size="small"
          />
        </div>
      )}

      {/* Footer Buttons */}
      <div style={{ marginTop: 24, textAlign: 'right' }}>
        <Space>
          {currentStep > 0 && (
            <Button onClick={handlePrev}>Previous</Button>
          )}
          {currentStep < 2 ? (
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

export default ObjectTypeWizard;

