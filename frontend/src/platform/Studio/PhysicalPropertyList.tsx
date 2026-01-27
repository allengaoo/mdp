/**
 * Physical Property List View component.
 * Shows flattened view of ALL properties from ALL Object Types in the current project.
 */
import React, { useState, useEffect, useMemo } from 'react';
import { Table, Tag, Space, Select, Tooltip, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { LinkOutlined, EyeOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../../api/axios';

interface ObjectTypeData {
  id: string;
  api_name: string;
  display_name: string;
  property_schema?: Record<string, any>;
}

interface PhysicalPropertyData {
  id: string;
  propKey: string;
  propName: string;
  dataType: string;
  objectName: string;
  objectId: string;
  sptName?: string;
}

const PhysicalPropertyList: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [objectTypes, setObjectTypes] = useState<ObjectTypeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedObjectFilter, setSelectedObjectFilter] = useState<string | undefined>(undefined);

  // Fetch object types from API
  const fetchObjectTypes = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/meta/object-types', {
        params: {
          limit: 100,
        },
      });
      // Filter by project if projectId is available
      const filteredData = projectId
        ? response.data.filter((item: ObjectTypeData) => item.project_id === projectId)
        : response.data;
      setObjectTypes(filteredData);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch object types');
      setObjectTypes([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchObjectTypes();
  }, [projectId]);

  // Flatten properties from all object types
  const flattenedProperties = useMemo(() => {
    const properties: PhysicalPropertyData[] = [];

    objectTypes.forEach((objType) => {
      if (!objType.property_schema) return;

      Object.entries(objType.property_schema).forEach(([propKey, propValue]) => {
        // Handle different property_schema formats
        let propName = propKey;
        let dataType = typeof propValue === 'string' ? propValue : 'string';
        let sptName: string | undefined;

        // If propValue is an object with more details
        if (typeof propValue === 'object' && propValue !== null) {
          propName = (propValue as any).displayName || (propValue as any).name || propKey;
          dataType = (propValue as any).type || (propValue as any).dataType || 'string';
          sptName = (propValue as any).linked_spt || (propValue as any).sptName;
        }

        properties.push({
          id: `${objType.id}_${propKey}`,
          propKey,
          propName: propName || propKey,
          dataType,
          objectName: objType.display_name,
          objectId: objType.id,
          sptName,
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
      label: obj.display_name,
    }));
  }, [objectTypes]);

  // Handle navigate to object type detail
  const handleNavigateToObject = (objectId: string) => {
    navigate(`/oma/project/${projectId}/object-types`);
    // In a real implementation, you might want to highlight or scroll to the specific object
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
      title: 'Belongs To Object',
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
      title: 'Linked Standard Property (SPT)',
      key: 'sptName',
      width: 250,
      render: (_, record) => {
        if (record.sptName) {
          return (
            <Tooltip title={`Inheriting constraints from ${record.sptName}`}>
              <Space>
                <LinkOutlined style={{ color: '#1890ff' }} />
                <span style={{ color: '#1890ff' }}>{record.sptName}</span>
              </Space>
            </Tooltip>
          );
        }
        return <span style={{ color: '#8c8c8c' }}>Local Definition</span>;
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
            style={{ width: 200 }}
            placeholder="All Objects"
            allowClear
            value={selectedObjectFilter}
            onChange={setSelectedObjectFilter}
            options={uniqueObjectTypes}
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
