/**
 * Physical Property List View component.
 * Shows flattened view of ALL properties from ALL Object Types in the current project.
 */
import React, { useState, useEffect, useMemo } from 'react';
import { Table, Tag, Space, Select, Tooltip, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { LinkOutlined, EyeOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchProjectObjectTypes } from '../../api/v3/ontology';
import { IV3ObjectTypeFull } from '../../api/v3/types';

interface PhysicalPropertyData {
  id: string;
  propKey: string;
  propName: string;
  dataType: string;
  objectName: string;
  objectId: string;
  sptName?: string;
  sptDisplayName?: string;
}

const PhysicalPropertyList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [objectTypes, setObjectTypes] = useState<IV3ObjectTypeFull[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedObjectFilter, setSelectedObjectFilter] = useState<string | undefined>(undefined);

  // Fetch object types from API
  const loadData = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const data = await fetchProjectObjectTypes(projectId);
      setObjectTypes(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch object types');
      setObjectTypes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  // Flatten properties from all object types
  const flattenedProperties = useMemo(() => {
    const properties: PhysicalPropertyData[] = [];

    objectTypes.forEach((objType) => {
      if (!objType.properties) return;

      objType.properties.forEach((prop) => {
        properties.push({
          id: `${objType.id}_${prop.api_name}`,
          propKey: prop.api_name,
          propName: prop.display_name || prop.api_name,
          dataType: prop.data_type,
          objectName: objType.display_name || objType.api_name,
          objectId: objType.id,
          sptName: prop.shared_property_api_name,
          sptDisplayName: prop.shared_property_display_name,
        });
      });
    });

    return properties;
  }, [objectTypes]);

  // Filter properties by selected object type
  const filteredProperties = useMemo(() => {
    if (!selectedObjectFilter) {
      return flattenedProperties;
    }
    return flattenedProperties.filter((prop) => prop.objectId === selectedObjectFilter);
  }, [flattenedProperties, selectedObjectFilter]);

  // Get unique object types for filter dropdown
  const uniqueObjectTypes = useMemo(() => {
    return objectTypes.map((obj) => ({
      value: obj.id,
      label: obj.display_name || obj.api_name,
    }));
  }, [objectTypes]);

  // Handle navigate to object type detail
  const handleNavigateToObject = (objectId: string) => {
    // Navigate to object type list, ideally could open specific object editor if supported
    navigate(`/oma/project/${projectId}/object-types`);
  };

  // Get data type tag color
  const getDataTypeColor = (dataType: string): string => {
    const colorMap: Record<string, string> = {
      string: 'blue',
      number: 'orange',
      integer: 'orange',
      boolean: 'green',
      datetime: 'purple',
      date: 'purple',
      array: 'cyan',
      object: 'geekblue',
    };
    return colorMap[dataType.toLowerCase()] || 'default';
  };

  const columns: ColumnsType<PhysicalPropertyData> = [
    {
      title: 'Property Name',
      key: 'propertyName',
      width: 250,
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.propName}</div>
          <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 4 }}>
            {record.propKey}
          </div>
        </div>
      ),
    },
    {
      title: 'Data Type',
      dataIndex: 'dataType',
      key: 'dataType',
      width: 120,
      render: (text: string) => (
        <Tag color={getDataTypeColor(text)}>{text}</Tag>
      ),
    },
    {
      title: 'Belongs to Object',
      key: 'objectName',
      width: 200,
      render: (_, record) => (
        <Space>
          <span>{record.objectName}</span>
          <Tooltip title="View Object Type Details">
            <EyeOutlined
              style={{ color: '#1890ff', cursor: 'pointer' }}
              onClick={() => handleNavigateToObject(record.objectId)}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: 'Linked Standard Property',
      key: 'sptName',
      width: 250,
      render: (_, record) => {
        if (record.sptName) {
          const displayName = record.sptDisplayName || record.sptName;
          return (
            <Tooltip title={`Linked to standard property: ${displayName} (${record.sptName})`}>
              <Space>
                <LinkOutlined style={{ color: '#1890ff' }} />
                <span style={{ color: '#1890ff' }}>{displayName}</span>
              </Space>
            </Tooltip>
          );
        }
        return <span style={{ color: '#8c8c8c' }}>-</span>;
      },
    },
  ];

  return (
    <div style={{ background: '#fff', padding: '24px', borderRadius: 8 }}>
      {/* Toolbar with Filter */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <span style={{ marginRight: 8 }}>Filter by Object:</span>
          <Select
            style={{ width: 250 }}
            placeholder="All Objects"
            allowClear
            value={selectedObjectFilter}
            onChange={setSelectedObjectFilter}
            options={uniqueObjectTypes}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </div>
        <div style={{ color: '#8c8c8c', fontSize: 14 }}>
          Total: {filteredProperties.length} properties
        </div>
      </div>

      <Table
        columns={columns}
        dataSource={filteredProperties}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        scroll={{ x: 1000 }}
      />
    </div>
  );
};

export default PhysicalPropertyList;
