/**
 * Link Type Editor component.
 * Single modal with reactive sections based on Cardinality changes.
 * 
 * @note V3 Migration: Read operations use V3 API (via api/ontology.ts adapters).
 * Update operation still uses V1 API (TODO: migrate when V3 endpoint is available).
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
import apiClient from '../../api/axios'; // TODO: Remove when V3 updateLinkType is available
import {
  fetchObjectTypes,
  fetchDatasources,
  IObjectType,
  IDataSourceTable,
} from '../../api/ontology';
import {
  createLinkMapping,
  getLinkMappingByDefId,
  updateLinkMapping,
  ILinkMapping,
} from '../../api/v3/ontology';

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
  description?: string | null;
  source_object_def_id: string;
  target_object_def_id: string;
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
  const [existingMapping, setExistingMapping] = useState<ILinkMapping | null>(null);

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

          // If editing existing link type, fetch mapping
          if (linkType) {
            const mapping = await getLinkMappingByDefId(linkType.id);
            setExistingMapping(mapping);
          }
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to load data');
          console.error('Error loading data:', error);
        } finally {
          setDataLoading(false);
        }
      };
      loadData();
    }
  }, [visible, projectId, linkType]);

  // Initialize form when linkType changes
  useEffect(() => {
    if (linkType && visible) {
      form.setFieldsValue({
        display_name: linkType.display_name,
        // Note: description field removed - not in database schema
        source_object_def_id: linkType.source_object_def_id,
        target_object_def_id: linkType.target_object_def_id,
        cardinality: linkType.cardinality,
      });
      setCardinality(linkType.cardinality);
      
      // Initialize join table and properties if M:N and mapping exists
      if (linkType.cardinality === 'MANY_TO_MANY' && existingMapping) {
        // Find the table in datasources (might need to fetch if not loaded)
        // Assuming datasources are loaded by the time existingMapping is set
        const table = datasources.find(t => t.id === existingMapping.source_connection_id); // Note: source_connection_id might be connection ID, not table ID. 
        // Actually IDataSourceTable.id is usually connection_id or similar. 
        // Let's assume datasources list contains tables with IDs that match what we store.
        // Wait, IDataSourceTable usually has `id` as connection_id or a unique ID.
        // Let's check IDataSourceTable definition.
        // It seems fetchDatasources returns tables.
        
        // Let's try to match by table name if ID doesn't match directly, or just use the ID stored.
        // For now, let's assume we store table ID or connection ID + table name.
        // LinkMappingDef stores source_connection_id and join_table_name.
        
        const matchedTable = datasources.find(
          t => t.connection_id === existingMapping.source_connection_id && t.table_name === existingMapping.join_table_name
        );

        if (matchedTable) {
          setSelectedJoinTable(matchedTable);
          form.setFieldsValue({
            join_table_id: matchedTable.id,
            source_key_mapping: existingMapping.source_key_column,
            target_key_mapping: existingMapping.target_key_column,
          });

          // Restore property mappings
          const columns = parseColumnsSchema(matchedTable.columns_schema);
          const keyColumns = [existingMapping.source_key_column, existingMapping.target_key_column];
          const propertyColumns = columns.filter(
            (col) => !keyColumns.includes(col.name)
          );
          
          const properties: LinkPropertyMapping[] = propertyColumns.map((col) => {
            const mappedProp = existingMapping.property_mappings[col.name];
            return {
              column: col.name,
              displayName: mappedProp || col.name, // If mapped, use it (or maybe key is prop name?)
              // Actually property_mappings is { "link_prop": "table_col" } usually, or { "table_col": "link_prop" }?
              // The model says: property_mappings: Dict[str, str] = Field(default={}, sa_column=Column(JSON))  # { "link_prop": "table_col" }
              // So we need to find if this column is in values.
              
              // Let's reverse lookup
              dataType: mapColumnTypeToDataType(col.type),
              include: Object.values(existingMapping.property_mappings).includes(col.name),
            };
          });
          
          // Update display names from mapping keys
          properties.forEach(p => {
             const entry = Object.entries(existingMapping.property_mappings).find(([k, v]) => v === p.column);
             if (entry) {
               p.displayName = entry[0];
             }
          });

          setLinkProperties(properties);
        }
      } else if (linkType.cardinality === 'MANY_TO_MANY' && !existingMapping) {
        // Default initialization if no mapping exists (same as before)
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
  }, [linkType, visible, form, datasources, existingMapping]);

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
    const sourceTypeId = linkType?.source_object_def_id;
    return objectTypes.find((ot) => ot.id === sourceTypeId);
  };

  // Get target object type
  const getTargetObjectType = (): IObjectType | undefined => {
    const targetTypeId = linkType?.target_object_def_id;
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

      // Save Link Mapping if M:N
      if (cardinality === 'MANY_TO_MANY' && selectedJoinTable) {
        const mappingPayload = {
          link_def_id: linkType?.id,
          source_connection_id: selectedJoinTable.connection_id, // Use connection_id
          join_table_name: selectedJoinTable.table_name, // Use table_name
          source_key_column: values.source_key_mapping,
          target_key_column: values.target_key_mapping,
          property_mappings: linkProperties
            .filter(p => p.include)
            .reduce((acc, p) => ({ ...acc, [p.displayName]: p.column }), {}),
        };

        if (existingMapping) {
          await updateLinkMapping(existingMapping.id, mappingPayload);
        } else {
          // Fix type mismatch: link_def_id can be undefined in linkType, but required in createLinkMapping
          if (!linkType?.id) {
            message.error('Link type ID is missing');
            return;
          }
          const createPayload = {
            ...mappingPayload,
            link_def_id: linkType.id
          };
          await createLinkMapping(createPayload);
        }
      }

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
              value={sourceObject?.display_name || linkType.source_object_def_id}
              disabled
            />
          </Form.Item>
          <Form.Item label="Target Object">
            <Input
              value={targetObject?.display_name || linkType.target_object_def_id}
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
