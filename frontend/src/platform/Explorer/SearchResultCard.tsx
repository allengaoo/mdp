/**
 * SearchResultCard Component
 * MDP Platform - Global Search Module
 * 
 * Displays a single search result with highlights and property badges.
 */

import React from 'react';
import { Card, Tag, Typography, Space, Tooltip, Badge } from 'antd';
import { 
  AimOutlined, 
  RocketOutlined, 
  RadarChartOutlined, 
  FileTextOutlined,
  AppstoreOutlined 
} from '@ant-design/icons';
import type { IObjectHit } from '../../api/v3/search';

const { Text, Paragraph } = Typography;

interface SearchResultCardProps {
  hit: IObjectHit;
  onClick?: (hit: IObjectHit) => void;
}

// Object type icon mapping
const getObjectIcon = (objectType: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    target: <AimOutlined style={{ color: '#ff4d4f' }} />,
    vessel: <RocketOutlined style={{ color: '#1890ff' }} />,
    aircraft: <RocketOutlined style={{ color: '#52c41a' }} />,
    sensor: <RadarChartOutlined style={{ color: '#722ed1' }} />,
    intel_report: <FileTextOutlined style={{ color: '#faad14' }} />,
  };
  return iconMap[objectType] || <AppstoreOutlined style={{ color: '#8c8c8c' }} />;
};

// Object type color mapping
const getObjectColor = (objectType: string): string => {
  const colorMap: Record<string, string> = {
    target: 'red',
    vessel: 'blue',
    aircraft: 'green',
    sensor: 'purple',
    intel_report: 'orange',
  };
  return colorMap[objectType] || 'default';
};

const SearchResultCard: React.FC<SearchResultCardProps> = ({ hit, onClick }) => {
  // Extract filterable properties to show as badges
  const propertyBadges: { key: string; value: string }[] = [];
  
  for (const [key, value] of Object.entries(hit.properties)) {
    // Only show keyword fields (ending with _kwd)
    if (key.endsWith('_kwd') && value) {
      const displayKey = key.replace(/_kwd$/, '');
      propertyBadges.push({ key: displayKey, value: String(value) });
    }
  }

  // Render display name with highlights if available
  const renderDisplayName = () => {
    const highlights = hit.highlights?.['display_name'];
    if (highlights && highlights.length > 0) {
      // Use the first highlight
      return (
        <span 
          dangerouslySetInnerHTML={{ __html: highlights[0] }}
          style={{ 
            fontSize: 16, 
            fontWeight: 600,
          }}
        />
      );
    }
    return (
      <Text strong style={{ fontSize: 16 }}>
        {hit.display_name || `${hit.object_type}_${hit.id.slice(0, 8)}`}
      </Text>
    );
  };

  // Render content highlights
  const renderContentHighlights = () => {
    // Find text field highlights
    const textHighlights: string[] = [];
    
    if (hit.highlights) {
      for (const [key, values] of Object.entries(hit.highlights)) {
        if (key.includes('_txt') && values && values.length > 0) {
          textHighlights.push(...values);
        }
      }
    }

    if (textHighlights.length === 0) {
      return null;
    }

    return (
      <div style={{ marginTop: 8 }}>
        {textHighlights.slice(0, 2).map((highlight, idx) => (
          <Paragraph 
            key={idx}
            style={{ 
              margin: 0, 
              fontSize: 13, 
              color: '#666',
              background: '#fafafa',
              padding: '4px 8px',
              borderRadius: 4,
              marginBottom: 4
            }}
          >
            <span dangerouslySetInnerHTML={{ __html: `...${highlight}...` }} />
          </Paragraph>
        ))}
      </div>
    );
  };

  return (
    <Card
      hoverable
      onClick={() => onClick?.(hit)}
      style={{ 
        marginBottom: 12,
        borderRadius: 8,
        border: '1px solid #e8e8e8',
      }}
      styles={{
        body: { padding: 16 }
      }}
    >
      {/* Header: Icon + Name + Type Badge */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: 8
      }}>
        <Space align="start">
          <div style={{ 
            fontSize: 24, 
            marginRight: 8,
            display: 'flex',
            alignItems: 'center'
          }}>
            {getObjectIcon(hit.object_type)}
          </div>
          <div>
            {renderDisplayName()}
            <div style={{ marginTop: 4 }}>
              <Tag color={getObjectColor(hit.object_type)}>
                {hit.object_type_display || hit.object_type}
              </Tag>
              <Tooltip title="相关性得分">
                <Badge 
                  count={`${(hit.score * 100).toFixed(0)}%`}
                  style={{ 
                    backgroundColor: hit.score > 0.7 ? '#52c41a' : 
                                    hit.score > 0.4 ? '#faad14' : '#8c8c8c',
                    fontSize: 10
                  }}
                />
              </Tooltip>
            </div>
          </div>
        </Space>
      </div>

      {/* Content Highlights */}
      {renderContentHighlights()}

      {/* Property Badges */}
      {propertyBadges.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Space wrap size={[4, 4]}>
            {propertyBadges.slice(0, 5).map(({ key, value }) => (
              <Tag key={key} style={{ margin: 0 }}>
                <Text type="secondary" style={{ fontSize: 11 }}>{key}:</Text>{' '}
                <Text style={{ fontSize: 12 }}>{value}</Text>
              </Tag>
            ))}
            {propertyBadges.length > 5 && (
              <Tag>+{propertyBadges.length - 5}</Tag>
            )}
          </Space>
        </div>
      )}

      {/* Footer: ID */}
      <div style={{ 
        marginTop: 12, 
        paddingTop: 8, 
        borderTop: '1px dashed #e8e8e8',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <Text type="secondary" style={{ fontSize: 11 }}>
          ID: {hit.id.slice(0, 8)}...
        </Text>
      </div>
    </Card>
  );
};

export default SearchResultCard;
