/**
 * TargetPanel - Right sidebar for target ontology properties
 */
import React, { useEffect, useState } from 'react';
import { Card, Select, List, Typography, Spin, Empty } from 'antd';
import { AimOutlined, HolderOutlined } from '@ant-design/icons';
import { fetchObjectTypes } from '../../../api/v3/ontology';

const { Text } = Typography;

interface ObjectProperty {
  api_name: string;
  display_name: string;
  data_type: string;
}

interface TargetPanelProps {
  objectTypeId: string;
  onObjectTypeChange: (objectTypeId: string) => void;
}

const TargetPanel: React.FC<TargetPanelProps> = ({
  objectTypeId,
  onObjectTypeChange,
}) => {
  const [objectTypes, setObjectTypes] = useState<any[]>([]);
  const [properties, setProperties] = useState<ObjectProperty[]>([]);
  const [loading, setLoading] = useState(false);

  // Load object types
  useEffect(() => {
    setLoading(true);
    fetchObjectTypes()
      .then(setObjectTypes)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Load properties when object type changes
  useEffect(() => {
    if (!objectTypeId || !objectTypes.length) {
      setProperties([]);
      return;
    }

    const objectType = objectTypes.find((t) => t.id === objectTypeId);
    if (objectType?.property_schema?.properties) {
      const props = objectType.property_schema.properties.map((p: any) => ({
        api_name: p.key || p.api_name,
        display_name: p.label || p.display_name || p.key,
        data_type: p.type || p.data_type,
      }));
      setProperties(props);
    } else {
      setProperties([]);
    }
  }, [objectTypeId, objectTypes]);

  const onDragStart = (event: React.DragEvent, prop: ObjectProperty) => {
    const data = {
      type: 'target',
      property: prop.api_name,
      label: prop.display_name,
      dataType: prop.data_type,
    };
    event.dataTransfer.setData('application/json', JSON.stringify(data));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Card
      title={
        <span>
          <AimOutlined style={{ marginRight: 8 }} />
          目标对象
        </span>
      }
      size="small"
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, overflow: 'auto', padding: '12px' }}
    >
      <div style={{ marginBottom: 12 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>对象类型</Text>
        <Select
          style={{ width: '100%', marginTop: 4 }}
          placeholder="选择目标对象类型"
          value={objectTypeId || undefined}
          onChange={onObjectTypeChange}
          loading={loading}
          showSearch
          optionFilterProp="label"
          options={objectTypes.map((t) => ({
            label: t.display_name || t.api_name,
            value: t.id,
          }))}
        />
      </div>

      <div>
        <Text type="secondary" style={{ fontSize: 12 }}>属性（拖拽到画布）</Text>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Spin size="small" />
          </div>
        ) : properties.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="请选择对象类型"
            style={{ marginTop: 20 }}
          />
        ) : (
          <List
            size="small"
            style={{ marginTop: 8 }}
            dataSource={properties}
            renderItem={(prop) => (
              <List.Item
                draggable
                onDragStart={(e) => onDragStart(e, prop)}
                style={{
                  cursor: 'grab',
                  padding: '8px 12px',
                  marginBottom: 4,
                  backgroundColor: '#f6ffed',
                  borderRadius: 6,
                  border: '1px solid #b7eb8f',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <HolderOutlined style={{ color: '#8c8c8c' }} />
                  <div>
                    <div style={{ fontWeight: 500 }}>{prop.display_name}</div>
                    <div style={{ fontSize: 11, color: '#8c8c8c' }}>
                      {prop.api_name} · {prop.data_type}
                    </div>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}
      </div>
    </Card>
  );
};

export default TargetPanel;
