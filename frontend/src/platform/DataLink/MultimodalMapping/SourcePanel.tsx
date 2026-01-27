/**
 * SourcePanel - Left sidebar for source table columns
 */
import React, { useEffect, useState } from 'react';
import { Card, Select, List, Typography, Spin, Empty } from 'antd';
import { DatabaseOutlined, HolderOutlined } from '@ant-design/icons';
import { fetchConnections, exploreSource } from '../../../api/v3/connectors';

const { Text } = Typography;

interface SourceColumn {
  name: string;
  type: string;
  nullable?: boolean;
}

interface SourcePanelProps {
  connectionId: string;
  tableName: string;
  onConnectionChange: (connectionId: string) => void;
  onTableChange: (tableName: string) => void;
}

const SourcePanel: React.FC<SourcePanelProps> = ({
  connectionId,
  tableName,
  onConnectionChange,
  onTableChange,
}) => {
  const [connections, setConnections] = useState<any[]>([]);
  const [tables, setTables] = useState<any[]>([]);
  const [columns, setColumns] = useState<SourceColumn[]>([]);
  const [loading, setLoading] = useState(false);

  // Load connections
  useEffect(() => {
    fetchConnections().then(setConnections).catch(console.error);
  }, []);

  // Load tables when connection changes
  useEffect(() => {
    if (!connectionId) {
      setTables([]);
      setColumns([]);
      return;
    }

    setLoading(true);
    exploreSource(connectionId)
      .then((data) => {
        setTables(data.tables || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [connectionId]);

  // Load columns when table changes
  useEffect(() => {
    if (!tableName || !tables.length) {
      setColumns([]);
      return;
    }

    const table = tables.find((t) => t.name === tableName);
    if (table?.columns) {
      setColumns(table.columns);
    }
  }, [tableName, tables]);

  const onDragStart = (event: React.DragEvent, column: SourceColumn) => {
    const data = {
      type: 'source',
      column: column.name,
      dataType: column.type,
    };
    event.dataTransfer.setData('application/json', JSON.stringify(data));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Card
      title={
        <span>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          数据源
        </span>
      }
      size="small"
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, overflow: 'auto', padding: '12px' }}
    >
      <div style={{ marginBottom: 12 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>连接</Text>
        <Select
          style={{ width: '100%', marginTop: 4 }}
          placeholder="选择数据连接"
          value={connectionId || undefined}
          onChange={onConnectionChange}
          options={connections.map((c) => ({
            label: `${c.name} (${c.conn_type})`,
            value: c.id,
          }))}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>表</Text>
        <Select
          style={{ width: '100%', marginTop: 4 }}
          placeholder="选择数据表"
          value={tableName || undefined}
          onChange={onTableChange}
          loading={loading}
          disabled={!connectionId}
          options={tables.map((t) => ({
            label: t.name,
            value: t.name,
          }))}
        />
      </div>

      <div>
        <Text type="secondary" style={{ fontSize: 12 }}>字段（拖拽到画布）</Text>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Spin size="small" />
          </div>
        ) : columns.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="请选择数据表"
            style={{ marginTop: 20 }}
          />
        ) : (
          <List
            size="small"
            style={{ marginTop: 8 }}
            dataSource={columns}
            renderItem={(col) => (
              <List.Item
                draggable
                onDragStart={(e) => onDragStart(e, col)}
                style={{
                  cursor: 'grab',
                  padding: '8px 12px',
                  marginBottom: 4,
                  backgroundColor: '#e6f4ff',
                  borderRadius: 6,
                  border: '1px solid #91caff',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <HolderOutlined style={{ color: '#8c8c8c' }} />
                  <div>
                    <div style={{ fontWeight: 500 }}>{col.name}</div>
                    <div style={{ fontSize: 11, color: '#8c8c8c' }}>{col.type}</div>
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

export default SourcePanel;
