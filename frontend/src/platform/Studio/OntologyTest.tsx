/**
 * Ontology Test component.
 * 3-column layout: Action Library | Orchestration Canvas | Monitor Panel
 */
import React, { useState } from 'react';
import { Card, Button, List, Tag, Typography, Space, Divider, Empty } from 'antd';
import { PlusOutlined, ReloadOutlined, PlayCircleOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

// Mock action library data (OODA loop examples)
interface ActionItem {
  id: string;
  name: string;
  category: string;
  description: string;
}

const MOCK_ACTIONS: ActionItem[] = [
  {
    id: 'obs-1',
    name: 'Entity Identify',
    category: 'Observe',
    description: 'Identify and classify entities in the environment',
  },
  {
    id: 'obs-2',
    name: 'Threat Assess',
    category: 'Observe',
    description: 'Assess threat levels of detected entities',
  },
  {
    id: 'ori-1',
    name: 'Situation Analysis',
    category: 'Orient',
    description: 'Analyze current situation and context',
  },
  {
    id: 'dec-1',
    name: 'Mission Planning',
    category: 'Decide',
    description: 'Plan mission objectives and strategy',
  },
  {
    id: 'act-1',
    name: 'Execute Strike',
    category: 'Act',
    description: 'Execute strike action on target',
  },
  {
    id: 'act-2',
    name: 'Deploy Resources',
    category: 'Act',
    description: 'Deploy resources to mission area',
  },
];

interface SelectedAction {
  id: string;
  actionId: string;
  actionName: string;
  params?: Record<string, any>;
}

const OntologyTest: React.FC = () => {
  const [selectedActions, setSelectedActions] = useState<SelectedAction[]>([]);

  const handleAddAction = (action: ActionItem) => {
    const newAction: SelectedAction = {
      id: `step-${selectedActions.length + 1}`,
      actionId: action.id,
      actionName: action.name,
      params: {},
    };
    setSelectedActions([...selectedActions, newAction]);
  };

  const handleRemoveAction = (id: string) => {
    setSelectedActions(selectedActions.filter(a => a.id !== id));
  };

  const handleReset = () => {
    setSelectedActions([]);
  };

  const handleSubmit = () => {
    console.log('Submitting execution:', selectedActions);
    // Mock execution
  };

  // Mock sandbox state
  const sandboxState = {
    fighters: [
      { id: 'f1', callsign: 'J-20-01', fuel: 90, status: 'Ready' },
      { id: 'f2', callsign: 'J-16-05', fuel: 85, status: 'Ready' },
    ],
    targets: [
      { id: 't1', name: 'Enemy Radar', threat: 'High', health: 100 },
    ],
  };

  return (
    <div style={{ display: 'flex', gap: '16px', height: 'calc(100vh - 200px)', minHeight: 600 }}>
      {/* Column 1: Action Library */}
      <div style={{ width: '280px', background: '#fff', borderRadius: 8, padding: '16px', overflow: 'auto' }}>
        <Title level={5} style={{ marginBottom: 16 }}>Action Library</Title>
        <List
          dataSource={MOCK_ACTIONS}
          renderItem={(action) => (
            <List.Item
              style={{
                padding: '12px',
                marginBottom: 8,
                border: '1px solid #e8e8e8',
                borderRadius: 6,
                cursor: 'pointer',
              }}
              actions={[
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  size="small"
                  onClick={() => handleAddAction(action)}
                >
                  Add
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>{action.name}</Text>
                    <Tag color="blue" size="small">{action.category}</Tag>
                  </Space>
                }
                description={<Text type="secondary" style={{ fontSize: 12 }}>{action.description}</Text>}
              />
            </List.Item>
          )}
        />
      </div>

      {/* Column 2: Orchestration Canvas */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#fff', borderRadius: 8, overflow: 'hidden' }}>
        {/* Header */}
        <div
          style={{
            padding: '16px 24px',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Title level={5} style={{ margin: 0 }}>
            模拟编排 ({selectedActions.length} Steps)
          </Title>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              Reset Env
            </Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleSubmit}
              disabled={selectedActions.length === 0}
            >
              Submit Execution
            </Button>
          </Space>
        </div>

        {/* Content */}
        <div style={{ flex: 1, padding: '24px', overflow: 'auto', background: '#fafafa' }}>
          {selectedActions.length === 0 ? (
            <Empty
              description="Waiting for action composition"
              style={{ marginTop: 100 }}
            />
          ) : (
            <List
              dataSource={selectedActions}
              renderItem={(action, index) => (
                <List.Item
                  style={{
                    background: '#fff',
                    marginBottom: 12,
                    padding: '16px',
                    border: '1px solid #e8e8e8',
                    borderRadius: 6,
                  }}
                  actions={[
                    <Button
                      type="link"
                      danger
                      size="small"
                      onClick={() => handleRemoveAction(action.id)}
                    >
                      Remove
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <div
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          background: '#1890ff',
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold',
                        }}
                      >
                        {index + 1}
                      </div>
                    }
                    title={<Text strong>{action.actionName}</Text>}
                    description={
                      <Space>
                        <Text type="secondary">Action ID: {action.actionId}</Text>
                        {Object.keys(action.params || {}).length > 0 && (
                          <Tag>Params: {JSON.stringify(action.params)}</Tag>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </div>

      {/* Column 3: Monitor Panel */}
      <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Top Half: Console / Logs */}
        <Card
          title="Console / Logs"
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          styles={{ body: { flex: 1, padding: '12px', overflow: 'auto', background: '#1e1e1e', color: '#d4d4d4' } }}
        >
          <div style={{ fontFamily: 'monospace', fontSize: 12 }}>
            <div style={{ color: '#4ec9b0' }}>{'>'} System initialized</div>
            <div style={{ color: '#4ec9b0' }}>{'>'} Ready for execution</div>
            {selectedActions.length > 0 && (
              <>
                <div style={{ color: '#569cd6' }}>{'>'} {selectedActions.length} action(s) queued</div>
                {selectedActions.map((action, idx) => (
                  <div key={action.id} style={{ color: '#ce9178', marginLeft: 16 }}>
                    [{idx + 1}] {action.actionName}
                  </div>
                ))}
              </>
            )}
          </div>
        </Card>

        {/* Bottom Half: Sandbox State */}
        <Card
          title="Sandbox State"
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          styles={{ body: { flex: 1, padding: '12px', overflow: 'auto' } }}
        >
          <div style={{ fontFamily: 'monospace', fontSize: 12, background: '#f5f5f5', padding: '12px', borderRadius: 4 }}>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {JSON.stringify(sandboxState, null, 2)}
            </pre>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default OntologyTest;

