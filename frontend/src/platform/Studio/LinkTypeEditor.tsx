/**
 * Link Type Editor component.
 * Single modal with reactive sections based on Cardinality changes.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  Select,
  Alert,
  Table,
  Switch,
  message,
  Divider,
} from 'antd';
import { useParams } from 'react-router-dom';
import apiClient from '../../api/axios';
import {
  fetchObjectTypes,
  fetchDatasources,
  IObjectType,
  IDataSourceTable,
} from '../../api/ontology';

// ObjectType interface is now imported from API
// RawTable interface is now IDataSourceTable from API

interface LinkPropertyMapping {
  column: string;
  displayName: string;
  dataType: string;
  include: boolean;
}

interface LinkTypeData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  source_type_id: string;
  target_type_id: string;
  cardinality: string;
}

interface LinkTypeEditorProps {
  visible: boolean;
  linkType: LinkTypeData | null;
  onCancel: () => void;
  onSuccess: () => void;
}

// Mock data removed - now using backend API

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

const LinkTypeEditor: React.FC<LinkTypeEditorProps> = ({
  visible,
  linkType,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [cardinality, setCardinality] = useState<string>('ONE_TO_MANY');
  const [selectedJoinTable, setSelectedJoinTable] = useState<IDataSourceTable | null>(null);
  const [linkProperties, setLinkProperties] = useState<LinkPropertyMapping[]>([]);
  const [loading, setLoading] = useState(false);
  const [objectTypes, setObjectTypes] = useState<IObjectType[]>([]);
  const [datasources, setDatasources] = useState<IDataSourceTable[]>([]);
  const [dataLoading, setDataLoading] = useState(false);

  // Fetch object types and datasources when modal opens
  useEffect(() => {
    if (visible) {
      const loadData = async () => {
        try {
          setDataLoading(true);
          const [objectTypesData, datasourcesData] = await Promise.all([
            fetchObjectTypes(projectId),
            fetchDatasources(),
          ]);
          setObjectTypes(objectTypesData);
          setDatasources(datasourcesData);
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to load data');
          console.error('Error loading data:', error);
        } finally {
          setDataLoading(false);
        }
      };
      loadData();
    }
  }, [visible, projectId]);

  // Initialize form when linkType changes
  useEffect(() => {
    if (linkType && visible) {
      form.setFieldsValue({
        display_name: linkType.display_name,
        // Note: description field removed - not in database schema
        source_type_id: linkType.source_type_id,
        target_type_id: linkType.target_type_id,
        cardinality: linkType.cardinality,
      });
      setCardinality(linkType.cardinality);
      
      // Initialize join table and properties if M:N
      // Note: Since mapping_config is not stored in DB, we initialize with empty/default values
      if (linkType.cardinality === 'MANY_TO_MANY') {
        // If datasources are loaded, use the first one as default (if available)
        if (datasources.length > 0) {
          const defaultTable = datasources[0];
          setSelectedJoinTable(defaultTable);
          const columns = parseColumnsSchema(defaultTable.columns_schema);
          if (columns.length >= 2) {
            form.setFieldsValue({
              join_table_id: defaultTable.id,
              source_key_mapping: columns[0]?.name,
              target_key_mapping: columns[1]?.name,
            });
            // Initialize link properties
            const keyColumns = [columns[0]?.name, columns[1]?.name];
            const propertyColumns = columns.filter(
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
        }
      }
    }
  }, [linkType, visible, form, datasources]);

  // Parse columns_schema (can be string or array)
  const parseColumnsSchema = (
    columnsSchema: IDataSourceTable['columns_schema']
  ): Array<{ name: string; type: string }> => {
    if (Array.isArray(columnsSchema)) {
      return columnsSchema;
    }
    if (typeof columnsSchema === 'string') {
      try {
        return JSON.parse(columnsSchema);
      } catch (e) {
        console.error('Failed to parse columns_schema:', e);
        return [];
      }
    }
    return [];
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

  // Handle cardinality change - reactive logic
  const handleCardinalityChange = (value: string) => {
    setCardinality(value);
    // Reset mapping fields when cardinality changes
    if (value === 'MANY_TO_MANY') {
      form.setFieldsValue({
        source_property: undefined,
        target_property: undefined,
      });
      // Initialize with first join table if available
      if (datasources.length > 0) {
        const defaultTable = datasources[0];
        setSelectedJoinTable(defaultTable);
        const columns = parseColumnsSchema(defaultTable.columns_schema);
        if (columns.length >= 2) {
          form.setFieldsValue({
            join_table_id: defaultTable.id,
            source_key_mapping: columns[0]?.name,
            target_key_mapping: columns[1]?.name,
          });
          // Initialize link properties
          const keyColumns = [columns[0]?.name, columns[1]?.name];
          const propertyColumns = columns.filter(
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
      }
    } else {
      form.setFieldsValue({
        join_table_id: undefined,
        source_key_mapping: undefined,
        target_key_mapping: undefined,
      });
      setSelectedJoinTable(null);
      setLinkProperties([]);
    }
  };

  // Get source object type
  const getSourceObjectType = (): IObjectType | undefined => {
    const sourceTypeId = form.getFieldValue('source_type_id');
    return objectTypes.find((ot) => ot.id === sourceTypeId);
  };

  // Get target object type
  const getTargetObjectType = (): IObjectType | undefined => {
    const targetTypeId = form.getFieldValue('target_type_id');
    return objectTypes.find((ot) => ot.id === targetTypeId);
  };

  // Get object properties (for FK mapping)
  const getObjectProperties = (objectType: IObjectType | undefined): string[] => {
    if (!objectType || !objectType.property_schema) {
      return ['id']; // Default PK
    }
    // Handle property_schema as object or array
    if (Array.isArray(objectType.property_schema)) {
      return objectType.property_schema.map((prop: any) => prop.key || prop.name || String(prop));
    }
    if (typeof objectType.property_schema === 'object') {
      return Object.keys(objectType.property_schema);
    }
    return ['id']; // Default PK
  };

  // Handle join table selection
  const handleJoinTableSelect = (tableId: string) => {
    const table = datasources.find((t) => t.id === tableId);
    setSelectedJoinTable(table || null);
    
    if (table) {
      const columns = parseColumnsSchema(table.columns_schema);
      const sourceKey = form.getFieldValue('source_key_mapping');
      const targetKey = form.getFieldValue('target_key_mapping');
      const keyColumns = [sourceKey, targetKey].filter(Boolean);
      
      const propertyColumns = columns.filter(
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

  // Handle save
  const handleSave = async () => {
    try {
      setLoading(true);
      const values = form.getFieldsValue();

      const payload = {
        display_name: values.display_name,
        // Note: description field removed - not in database schema
        cardinality: cardinality,
      };

      await apiClient.put(`/meta/link-types/${linkType?.id}`, payload);
      message.success('Link type updated successfully');
      onSuccess();
      handleCancel();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update link type');
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    form.resetFields();
    setCardinality('ONE_TO_MANY');
    setSelectedJoinTable(null);
    setLinkProperties([]);
    onCancel();
  };

  // Link property columns
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

  if (!linkType) return null;

  const isManyToMany = cardinality === 'MANY_TO_MANY';
  const sourceObject = getSourceObjectType();
  const targetObject = getTargetObjectType();

  return (
    <Modal
      title={`Edit Link Type: ${linkType.display_name}`}
      open={visible}
      onCancel={handleCancel}
      width={1000}
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
      <Form form={form} layout="vertical">
        {/* Read-only Section */}
        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 16 }}>Basic Information (Read-only)</h4>
          <Form.Item label="Name">
            <Input value={linkType.display_name} disabled />
          </Form.Item>
          <Form.Item label="API Identifier">
            <Input value={linkType.api_name} disabled />
          </Form.Item>
          <Form.Item label="Source Object">
            <Input
              value={sourceObject?.display_name || linkType.source_type_id}
              disabled
            />
          </Form.Item>
          <Form.Item label="Target Object">
            <Input
              value={targetObject?.display_name || linkType.target_type_id}
              disabled
            />
          </Form.Item>
        </div>

        <Divider />

        {/* Editable Section */}
        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 16 }}>Editable Fields</h4>
          {/* Note: Description field removed - not in database schema */}
          <Form.Item
            name="cardinality"
            label="Cardinality"
            rules={[{ required: true, message: 'Please select cardinality' }]}
          >
            <Select
              placeholder="Select cardinality"
              onChange={handleCardinalityChange}
            >
              {CARDINALITY_OPTIONS.map((opt) => (
                <Select.Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </div>

        <Divider />

        {/* Reactive Mapping Section */}
        {!isManyToMany && (
          <div>
            <h4 style={{ marginBottom: 16 }}>Foreign Key Mapping</h4>
            <Alert
              message="Foreign Key Mapping"
              description="Map the source and target object properties for the relationship."
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <Form.Item
                name="source_property"
                label="Source Object Property"
                style={{ flex: 1 }}
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
            <h4 style={{ marginBottom: 16 }}>Join Table & Keys</h4>
            <Alert
              message="Join Table Mode"
              description="Many-to-Many relationships require an intermediate Join Table."
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Form.Item name="join_table_id" label="Select Join Table">
              <Select
                placeholder="Select join table"
                onChange={handleJoinTableSelect}
                loading={dataLoading}
              >
                {datasources.map((table) => (
                  <Select.Option key={table.id} value={table.id}>
                    {table.table_name} ({table.db_type})
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {selectedJoinTable && (
              <>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                    Source Key Mapping:
                  </label>
                  <Form.Item name="source_key_mapping">
                    <Select placeholder="Map Source Object PK to Join Table Column">
                      {parseColumnsSchema(selectedJoinTable.columns_schema)
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
                  <Form.Item name="target_key_mapping">
                    <Select placeholder="Map Target Object PK to Join Table Column">
                      {parseColumnsSchema(selectedJoinTable.columns_schema)
                        .filter((col) => col.name.includes('_id') || col.name.includes('id'))
                        .map((col) => (
                          <Select.Option key={col.name} value={col.name}>
                            {col.name} ({col.type})
                          </Select.Option>
                        ))}
                    </Select>
                  </Form.Item>
                </div>

                <Divider />

                <h4 style={{ marginBottom: 16 }}>Link Properties Mapping</h4>
                <Alert
                  message="Link Properties"
                  description="Define properties that live on the link itself (e.g., 'Role', 'Assigned At'). These are mapped from the remaining columns in the join table."
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  columns={linkPropertyColumns}
                  dataSource={linkProperties}
                  rowKey="column"
                  pagination={false}
                  size="small"
                  style={{ background: '#fff' }}
                />
              </>
            )}
          </div>
        )}
      </Form>
    </Modal>
  );
};

export default LinkTypeEditor;
