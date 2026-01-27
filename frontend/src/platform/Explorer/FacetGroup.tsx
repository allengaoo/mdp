/**
 * FacetGroup Component
 * MDP Platform - Global Search Module
 * 
 * Renders a collapsible checkbox group for faceted filtering.
 */

import React, { useState } from 'react';
import { Checkbox, Collapse, Badge, Typography, Space } from 'antd';
import { CaretRightOutlined } from '@ant-design/icons';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';
import type { IFacet, IFacetBucket } from '../../api/v3/search';

const { Text } = Typography;

interface FacetGroupProps {
  facet: IFacet;
  selectedValues: string[];
  onChange: (field: string, values: string[]) => void;
  maxVisible?: number;
}

const FacetGroup: React.FC<FacetGroupProps> = ({
  facet,
  selectedValues,
  onChange,
  maxVisible = 5,
}) => {
  const [showAll, setShowAll] = useState(false);

  const visibleBuckets = showAll 
    ? facet.buckets 
    : facet.buckets.slice(0, maxVisible);

  const hasMore = facet.buckets.length > maxVisible;

  const handleCheckboxChange = (key: string) => (e: CheckboxChangeEvent) => {
    const checked = e.target.checked;
    let newValues: string[];

    if (checked) {
      newValues = [...selectedValues, key];
    } else {
      newValues = selectedValues.filter(v => v !== key);
    }

    onChange(facet.field, newValues);
  };

  const handleSelectAll = () => {
    if (selectedValues.length === facet.buckets.length) {
      onChange(facet.field, []);
    } else {
      onChange(facet.field, facet.buckets.map(b => b.key));
    }
  };

  // Total count of selected items
  const selectedCount = selectedValues.length;

  return (
    <Collapse
      defaultActiveKey={['1']}
      expandIcon={({ isActive }) => (
        <CaretRightOutlined rotate={isActive ? 90 : 0} />
      )}
      style={{ marginBottom: 8, background: '#fff' }}
      items={[
        {
          key: '1',
          label: (
            <Space>
              <Text strong>{facet.display_name}</Text>
              {selectedCount > 0 && (
                <Badge 
                  count={selectedCount} 
                  style={{ backgroundColor: '#1890ff' }} 
                />
              )}
            </Space>
          ),
          children: (
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              <div style={{ marginBottom: 8, borderBottom: '1px solid #f0f0f0', paddingBottom: 8 }}>
                <a onClick={handleSelectAll} style={{ fontSize: 12 }}>
                  {selectedValues.length === facet.buckets.length ? '取消全选' : '全选'}
                </a>
              </div>
              
              {visibleBuckets.map((bucket: IFacetBucket) => (
                <div 
                  key={bucket.key} 
                  style={{ 
                    marginBottom: 4,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <Checkbox
                    checked={selectedValues.includes(bucket.key)}
                    onChange={handleCheckboxChange(bucket.key)}
                    style={{ flex: 1 }}
                  >
                    <Text 
                      ellipsis={{ tooltip: bucket.key }}
                      style={{ maxWidth: 150, display: 'inline-block' }}
                    >
                      {bucket.key || '(空)'}
                    </Text>
                  </Checkbox>
                  <Badge 
                    count={bucket.count} 
                    style={{ 
                      backgroundColor: selectedValues.includes(bucket.key) 
                        ? '#1890ff' 
                        : '#d9d9d9',
                      marginLeft: 8
                    }} 
                    showZero
                    overflowCount={9999}
                  />
                </div>
              ))}

              {hasMore && (
                <a 
                  onClick={() => setShowAll(!showAll)}
                  style={{ display: 'block', marginTop: 8, fontSize: 12 }}
                >
                  {showAll 
                    ? '收起' 
                    : `显示更多 (${facet.buckets.length - maxVisible})`}
                </a>
              )}
            </div>
          ),
        },
      ]}
    />
  );
};

export default FacetGroup;
