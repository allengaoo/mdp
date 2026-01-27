/**
 * Object Type Editor component.
 * Tab-based editor for editing existing object types.
 * 
 * @note V3 Migration: Uses api/ontology.ts functions which internally use V3 API.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Tabs,
  Form,
  Input,
  Button,
  Alert,
  Select,
  Table,
  Tag,
  message,
} from 'antd';
import { useParams } from 'react-router-dom';
import { fetchSharedProperties, updateObjectType, ISharedProperty } from '../../api/ontology';
import { IV3ObjectTypeFull } from '../../api/v3/types';

const { TabPane } = Tabs;
const { TextArea } = Input;

interface PropertyMapping {
  rawColumn: string;
  propertyName: string;
  type: string;
  useSharedProperty?: string;
}

// Use V3 ObjectTypeFull interface which includes datasource
type ObjectTypeData = IV3ObjectTypeFull;

interface ObjectTypeEditorProps {
  visible: boolean;
  objectType: ObjectTypeData | null;
  onCancel: () => void;
  onSuccess: () => void;
}


const ObjectTypeEditor: React.FC<ObjectTypeEditorProps> = ({
  visible,
  objectType,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('basic');
  const [propertyMappings, setPropertyMappings] = useState<PropertyMapping[]>([]);
  const [loading, setLoading] = useState(false);
  const [sharedProperties, setSharedProperties] = useState<ISharedProperty[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  // Fetch shared properties on mount
  useEffect(() => {
    if (visible) {
      const loadSharedProperties = async () => {
        try {
          setLoadingData(true);
          const data = await fetchSharedProperties();
          setSharedProperties(data);
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to load shared properties');
        } finally {
          setLoadingData(false);
        }
      };
      loadSharedProperties();
    }
  }, [visible, projectId]);

  // Initialize form when objectType changes
  useEffect(() => {
    if (objectType && visible) {
      form.setFieldsValue({
        display_name: objectType.display_name,
        description: objectType.description || '',
      });

      // Initialize property mappings from properties array (V3 format)
      if (objectType.properties && objectType.properties.length > 0) {
        const mappings: PropertyMapping[] = objectType.properties.map((prop) => ({
          rawColumn: prop.api_name, // In edit mode, we use property name as raw column
          propertyName: prop.api_name,
          type: prop.data_type.toLowerCase(), // Convert STRING -> string, etc.
          useSharedProperty: prop.property_def_id, // Use property_def_id to identify shared property
        }));
        setPropertyMappings(mappings);
      }
    }
  }, [objectType, visible, form]);

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

  // Add new property mapping
  const handleAddProperty = () => {
    const newMapping: PropertyMapping = {
      rawColumn: `new_property_${Date.now()}`,
      propertyName: '',
      type: 'string',
      useSharedProperty: undefined,
    };
    setPropertyMappings([...propertyMappings, newMapping]);
  };

  // Remove property mapping
  const handleRemoveProperty = (index: number) => {
    const newMappings = propertyMappings.filter((_, i) => i !== index);
    setPropertyMappings(newMappings);
  };

  // Handle save
  const handleSave = async () => {
    try {
      setLoading(true);
      const values = form.getFieldsValue();

      // Build property_schema from mappings (convert to Dict format for update endpoint)
      const propertySchemaDict: Record<string, any> = {};
      propertyMappings.forEach((mapping) => {
        if (mapping.propertyName && mapping.type) {
          // Convert property type to uppercase (e.g., 'string' -> 'STRING')
          const typeUpper = mapping.type.toUpperCase();
          // Find shared property ID if useSharedProperty is set
          let sharedPropertyId: string | undefined = undefined;
          if (mapping.useSharedProperty) {
            const sharedProp = sharedProperties.find((p) => p.api_name === mapping.useSharedProperty);
            sharedPropertyId = sharedProp?.id;
          }
          propertySchemaDict[mapping.propertyName] = {
            label: mapping.propertyName, // Use property name as label for now
            type: typeUpper,
            required: false, // Default to false for edit mode
            ...(sharedPropertyId && { shared_property_id: sharedPropertyId }),
          };
        }
      });

      const payload = {
        display_name: values.display_name,
        description: values.description || null,
        property_schema: propertySchemaDict,
      };

      if (!objectType?.id) {
        message.error('Object type ID is missing');
        return;
      }
      await updateObjectType(objectType.id, payload);
      message.success('Object type updated successfully');
      onSuccess();
      handleCancel();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update object type');
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    form.resetFields();
    setActiveTab('basic');
    setPropertyMappings([]);
    onCancel();
  };

  // Property mapping table columns
  const mappingColumns = [
    {
      title: 'Property Name',
      key: 'propertyName',
      width: 200,
      render: (_: any, record: PropertyMapping, index: number) => (
        <Input
          value={record.propertyName}
          onChange={(e) => handlePropertyMappingChange(index, 'propertyName', e.target.value)}
          disabled={!!record.useSharedProperty}
          placeholder="Property name"
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
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, record: PropertyMapping, index: number) => (
        <Button
          type="link"
          danger
          onClick={() => handleRemoveProperty(index)}
          disabled={propertyMappings.length === 1} // Prevent removing last property
        >
          Remove
        </Button>
      ),
    },
  ];

  if (!objectType) return null;

  return (
    <Modal
      title={`Edit Object Type: ${objectType.display_name}`}
      open={visible}
      onCancel={handleCancel}
      width={900}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button key="save" type="primary" loading={loading} onClick={handleSave}>
          Save Changes
        </Button>,
      ]}
      destroyOnClose
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Basic Info" key="basic">
          <Form form={form} layout="vertical">
            <Form.Item label="API Name">
              <Input value={objectType.api_name} disabled />
            </Form.Item>
            <Form.Item
              name="display_name"
              label="Display Name"
              rules={[{ required: true, message: 'Please enter display name' }]}
            >
              <Input placeholder="e.g., Battle Tank" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <TextArea rows={4} placeholder="Enter description..." />
            </Form.Item>
          </Form>
        </TabPane>
        <TabPane tab="Datasource" key="datasource">
          {objectType.datasource ? (
            <div>
              <Alert
                message="Data Source Information"
                description={`This object type is connected to a data source via ${objectType.datasource.type === 'pipeline' ? 'Pipeline' : 'Mapping'}.`}
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              {/* Pipeline Type Datasource */}
              {objectType.datasource.type === 'pipeline' && (
                <div>
                  <h4 style={{ marginBottom: 12 }}>Pipeline Configuration</h4>
                  <Table
                    dataSource={[
                      { key: 'dataset', label: 'Dataset', value: objectType.datasource.dataset_name || objectType.datasource.dataset_id },
                      { key: 'table', label: 'Table Name', value: objectType.datasource.table_name || '-' },
                      { key: 'connection', label: 'Connection', value: objectType.datasource.connection_name || objectType.datasource.connection_id },
                      { key: 'db_type', label: 'Database Type', value: objectType.datasource.db_type || '-' },
                      { key: 'mode', label: 'Pipeline Mode', value: objectType.datasource.pipeline_mode || '-' },
                    ]}
                    columns={[
                      { title: 'Field', dataIndex: 'label', key: 'label', width: 150 },
                      { title: 'Value', dataIndex: 'value', key: 'value' },
                    ]}
                    pagination={false}
                    size="small"
                    style={{ marginBottom: 24 }}
                  />
                  
                  {objectType.datasource.sync_status && (
                    <>
                      <h4 style={{ marginBottom: 12 }}>Sync Status</h4>
                      <Table
                        dataSource={[
                          { 
                            key: 'status', 
                            label: 'Status', 
                            value: objectType.datasource.sync_status,
                          },
                          { 
                            key: 'last_sync', 
                            label: 'Last Sync Time', 
                            value: objectType.datasource.last_sync_time 
                              ? new Date(objectType.datasource.last_sync_time).toLocaleString() 
                              : '-'
                          },
                          { 
                            key: 'rows', 
                            label: 'Rows Processed', 
                            value: objectType.datasource.rows_processed !== undefined
                              ? objectType.datasource.rows_processed.toLocaleString()
                              : '-'
                          },
                        ]}
                        columns={[
                          { title: 'Field', dataIndex: 'label', key: 'label', width: 150 },
                          { 
                            title: 'Value', 
                            key: 'value',
                            render: (_: any, record: any) => {
                              if (record.key === 'status') {
                                const statusConfig: Record<string, { color: string; text: string }> = {
                                  'SUCCESS': { color: 'success', text: 'Success' },
                                  'RUNNING': { color: 'processing', text: 'Running' },
                                  'FAILED': { color: 'error', text: 'Failed' },
                                  'PENDING': { color: 'default', text: 'Pending' },
                                };
                                const config = statusConfig[record.value] || { color: 'default', text: record.value || 'N/A' };
                                return <Tag color={config.color}>{config.text}</Tag>;
                              }
                              return record.value;
                            }
                          },
                        ]}
                        pagination={false}
                        size="small"
                      />
                    </>
                  )}
                </div>
              )}
              
              {/* Mapping Type Datasource */}
              {objectType.datasource.type === 'mapping' && (
                <div>
                  <h4 style={{ marginBottom: 12 }}>Mapping Configuration</h4>
                  <Table
                    dataSource={[
                      { key: 'table', label: 'Source Table', value: objectType.datasource.source_table_name || '-' },
                      { key: 'connection', label: 'Connection', value: objectType.datasource.connection_name || objectType.datasource.connection_id },
                      { key: 'db_type', label: 'Database Type', value: objectType.datasource.db_type || '-' },
                    ]}
                    columns={[
                      { title: 'Field', dataIndex: 'label', key: 'label', width: 150 },
                      { title: 'Value', dataIndex: 'value', key: 'value' },
                    ]}
                    pagination={false}
                    size="small"
                  />
                </div>
              )}
            </div>
          ) : (
            <div>
              <Alert
                message="No Data Source Configured"
                description="This object type is not currently connected to any data source. Configure a Pipeline or Mapping to connect it to data."
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <div>
                <p>
                  <strong>API Name:</strong> {objectType.api_name} (Read-only)
                </p>
                <p style={{ color: '#666', marginTop: 8 }}>
                  To connect this object type to a data source, create a Pipeline or Mapping definition.
                </p>
              </div>
            </div>
          )}
        </TabPane>
        <TabPane tab="Property Mapping" key="mapping">
          <div style={{ marginBottom: 16 }}>
            <Button type="primary" onClick={handleAddProperty}>
              Add Property
            </Button>
          </div>
          <Table
            columns={mappingColumns}
            dataSource={propertyMappings}
            rowKey={(record, index) => `${record.propertyName}-${index}`}
            pagination={false}
            size="small"
          />
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default ObjectTypeEditor;

