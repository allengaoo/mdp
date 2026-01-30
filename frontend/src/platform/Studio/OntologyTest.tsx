/**
 * Ontology Test component.
 * 3-column layout: Action Library | Orchestration Canvas | Monitor Panel
 * Connected to real backend APIs for action execution.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, List, Tag, Typography, Space, Empty, Tooltip, Badge, Spin, message, Select } from 'antd';
import {
  PlusOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  EyeOutlined,
  RadarChartOutlined,
  BulbOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import {
  fetchActionDefinitions,
  fetchObjectTypes,
  fetchObjectInstances,
  executeAction,
  IActionDefinition,
  IObjectType,
  IObjectInstance,
} from '../../api/ontology';

const { Title, Text } = Typography;

// OODA Category configuration
const CATEGORY_CONFIG: Record<string, { color: string; bgColor: string; icon: React.ReactNode }> = {
  Observe: { color: '#10b981', bgColor: '#ecfdf5', icon: <EyeOutlined /> },
  Orient: { color: '#f59e0b', bgColor: '#fffbeb', icon: <RadarChartOutlined /> },
  Decide: { color: '#6366f1', bgColor: '#eef2ff', icon: <BulbOutlined /> },
  Act: { color: '#ef4444', bgColor: '#fef2f2', icon: <RocketOutlined /> },
  Default: { color: '#6b7280', bgColor: '#f3f4f6', icon: <ThunderboltOutlined /> },
};

// Map action api_name to OODA category (heuristic based on naming)
const inferCategory = (apiName: string): string => {
  const name = apiName.toLowerCase();
  if (name.includes('observe') || name.includes('detect') || name.includes('scan') || name.includes('identify')) {
    return 'Observe';
  }
  if (name.includes('orient') || name.includes('analyze') || name.includes('assess') || name.includes('evaluate')) {
    return 'Orient';
  }
  if (name.includes('decide') || name.includes('plan') || name.includes('select') || name.includes('choose')) {
    return 'Decide';
  }
  if (name.includes('act') || name.includes('execute') || name.includes('strike') || name.includes('deploy') || name.includes('send') || name.includes('update')) {
    return 'Act';
  }
  return 'Default';
};

// Extended action item with category
interface ActionItem {
  id: string;
  api_name: string;
  display_name: string;
  backing_function_id: string;
  category: string;
}

interface SelectedAction {
  id: string;
  actionId: string;
  actionApiName: string;
  actionName: string;
  category: string;
  params?: Record<string, unknown>;
}

interface ExecutionLog {
  id: string;
  timestamp: Date;
  actionName: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  message?: string;
  result?: any;
}

interface SandboxState {
  objectTypes: IObjectType[];
  instances: Record<string, IObjectInstance[]>; // keyed by object_type api_name
}

const OntologyTest: React.FC = () => {
  // Action Library State
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [actionsLoading, setActionsLoading] = useState<boolean>(true);

  // Orchestration State
  const [selectedActions, setSelectedActions] = useState<SelectedAction[]>([]);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  // Sandbox State
  const [objectTypes, setObjectTypes] = useState<IObjectType[]>([]);
  const [sandboxInstances, setSandboxInstances] = useState<Record<string, IObjectInstance[]>>({});
  const [sandboxLoading, setSandboxLoading] = useState<boolean>(true);
  const [selectedSourceId, setSelectedSourceId] = useState<string>('');

  // Console Logs
  const [logs, setLogs] = useState<ExecutionLog[]>([]);

  // Load action definitions
  useEffect(() => {
    const loadActions = async () => {
      setActionsLoading(true);
      try {
        const data = await fetchActionDefinitions();
        // Add category to each action
        const actionsWithCategory = data.map((action) => ({
          ...action,
          category: inferCategory(action.api_name),
        }));
        setActions(actionsWithCategory);
        addLog('info', '行为库加载完成', `共 ${data.length} 个行为`);
      } catch (error: any) {
        console.error('Failed to load actions:', error);
        addLog('error', '行为库加载失败', error.message);
        message.error('加载行为库失败');
      } finally {
        setActionsLoading(false);
      }
    };
    loadActions();
  }, []);

  // Load object types and instances for sandbox
  useEffect(() => {
    const loadSandboxData = async () => {
      setSandboxLoading(true);
      try {
        // Load object types
        const types = await fetchObjectTypes();
        setObjectTypes(types);

        // Load instances for each type (limit to first 3 types for performance)
        const typesToLoad = types.slice(0, 3);
        const instancesMap: Record<string, IObjectInstance[]> = {};

        for (const type of typesToLoad) {
          try {
            const instances = await fetchObjectInstances(type.api_name);
            if (instances.length > 0) {
              instancesMap[type.api_name] = instances.slice(0, 5); // Limit to 5 per type
            }
          } catch (e) {
            console.warn(`Failed to load instances for ${type.api_name}:`, e);
          }
        }

        setSandboxInstances(instancesMap);

        // Auto-select first instance as source if available
        const firstInstances = Object.values(instancesMap).flat();
        if (firstInstances.length > 0 && !selectedSourceId) {
          setSelectedSourceId(firstInstances[0].id);
        }

        addLog('info', '沙箱数据加载完成', `${types.length} 种类型`);
      } catch (error: any) {
        console.error('Failed to load sandbox data:', error);
        addLog('error', '沙箱数据加载失败', error.message);
      } finally {
        setSandboxLoading(false);
      }
    };
    loadSandboxData();
  }, []);

  // Add log helper
  const addLog = (type: 'info' | 'success' | 'error' | 'pending', title: string, detail?: string) => {
    const logEntry: ExecutionLog = {
      id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      actionName: title,
      status: type === 'info' ? 'pending' : type,
      message: detail,
    };
    setLogs((prev) => [...prev.slice(-50), logEntry]); // Keep last 50 logs
  };

  // Handle add action to orchestration
  const handleAddAction = (action: ActionItem) => {
    const newAction: SelectedAction = {
      id: `step-${Date.now()}`,
      actionId: action.id,
      actionApiName: action.api_name,
      actionName: action.display_name,
      category: action.category,
      params: {},
    };
    setSelectedActions([...selectedActions, newAction]);
    addLog('info', `添加行为: ${action.display_name}`, action.api_name);
  };

  // Handle remove action from orchestration
  const handleRemoveAction = (id: string) => {
    const action = selectedActions.find((a) => a.id === id);
    setSelectedActions(selectedActions.filter((a) => a.id !== id));
    if (action) {
      addLog('info', `移除行为: ${action.actionName}`);
    }
  };

  // Handle reset orchestration
  const handleReset = () => {
    setSelectedActions([]);
    addLog('info', '编排已重置');
  };

  // Handle execute all actions
  const handleSubmit = async () => {
    if (selectedActions.length === 0) {
      message.warning('请先添加行为到编排中');
      return;
    }

    if (!selectedSourceId) {
      message.warning('请先选择执行源对象');
      return;
    }

    setIsExecuting(true);
    addLog('info', '开始执行编排', `共 ${selectedActions.length} 个行为`);

    let successCount = 0;
    let failCount = 0;

    for (const action of selectedActions) {
      addLog('pending', `执行中: ${action.actionName}`, action.actionApiName);

      try {
        const result = await executeAction(action.actionApiName, selectedSourceId, action.params);

        if (result.success) {
          successCount++;
          addLog('success', `✓ ${action.actionName}`, JSON.stringify(result.result).slice(0, 100));
        } else {
          failCount++;
          addLog('error', `✗ ${action.actionName}`, result.message || '执行失败');
        }
      } catch (error: any) {
        failCount++;
        addLog('error', `✗ ${action.actionName}`, error.response?.data?.detail || error.message);
      }

      // Small delay between actions
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    setIsExecuting(false);
    addLog(
      failCount === 0 ? 'success' : 'error',
      '编排执行完成',
      `成功: ${successCount}, 失败: ${failCount}`
    );
    message.info(`执行完成: ${successCount} 成功, ${failCount} 失败`);

    // Refresh sandbox data after execution
    refreshSandbox();
  };

  // Refresh sandbox data
  const refreshSandbox = useCallback(async () => {
    setSandboxLoading(true);
    try {
      const instancesMap: Record<string, IObjectInstance[]> = {};
      const typesToLoad = objectTypes.slice(0, 3);

      for (const type of typesToLoad) {
        try {
          const instances = await fetchObjectInstances(type.api_name);
          if (instances.length > 0) {
            instancesMap[type.api_name] = instances.slice(0, 5);
          }
        } catch (e) {
          console.warn(`Failed to refresh instances for ${type.api_name}:`, e);
        }
      }

      setSandboxInstances(instancesMap);
      addLog('info', '沙箱状态已刷新');
    } catch (error) {
      console.error('Failed to refresh sandbox:', error);
    } finally {
      setSandboxLoading(false);
    }
  }, [objectTypes]);

  // Get all instances as flat list for source selection
  const allInstances = Object.entries(sandboxInstances).flatMap(([typeName, instances]) =>
    instances.map((inst) => ({ ...inst, typeName }))
  );

  return (
    <div
      style={{
        display: 'flex',
        gap: '12px',
        height: 'calc(100vh - 140px)',
        minHeight: 450,
        overflow: 'hidden',
      }}
    >
      {/* Column 1: Action Library */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined style={{ color: '#6366f1' }} />
            <span>行为库</span>
            <Badge count={actions.length} style={{ backgroundColor: '#6366f1' }} />
          </Space>
        }
        styles={{
          header: {
            borderBottom: '2px solid #f0f0f0',
            padding: '10px 14px',
          },
          body: {
            padding: '10px',
            overflow: 'auto',
            flex: 1,
          },
        }}
        style={{
          width: 260,
          flexShrink: 0,
          borderRadius: 10,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {actionsLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
            <div style={{ marginTop: 12, color: '#999' }}>加载行为库...</div>
          </div>
        ) : actions.length === 0 ? (
          <Empty description="暂无行为定义" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            {actions.map((action) => {
              const config = CATEGORY_CONFIG[action.category] || CATEGORY_CONFIG.Default;
              return (
                <div
                  key={action.id}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 10,
                    border: `1px solid ${config.color}20`,
                    background: config.bgColor,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateX(4px)';
                    e.currentTarget.style.boxShadow = `0 4px 12px ${config.color}20`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateX(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                        <Tag
                          icon={config.icon}
                          style={{
                            color: config.color,
                            background: 'white',
                            border: `1px solid ${config.color}`,
                            borderRadius: 4,
                            fontSize: 11,
                            padding: '1px 6px',
                          }}
                        >
                          {action.category}
                        </Tag>
                      </div>
                      <Text strong style={{ fontSize: 14, display: 'block', marginBottom: 4 }}>
                        {action.display_name}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12, lineHeight: 1.4 }}>
                        {action.api_name}
                      </Text>
                    </div>
                    <Tooltip title="添加到编排">
                      <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAddAction(action);
                        }}
                        style={{
                          borderRadius: 6,
                          marginLeft: 12,
                          background: config.color,
                          borderColor: config.color,
                          flexShrink: 0,
                        }}
                      />
                    </Tooltip>
                  </div>
                </div>
              );
            })}
          </Space>
        )}
      </Card>

      {/* Column 2: Orchestration Canvas */}
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
            <Space>
              <PlayCircleOutlined style={{ color: '#1677ff' }} />
              <span>编排执行</span>
              <Tag color="blue" style={{ marginLeft: 4 }}>
                {selectedActions.length} 步骤
              </Tag>
            </Space>
            <Space size={8}>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
                disabled={selectedActions.length === 0 || isExecuting}
                style={{ borderRadius: 6 }}
              >
                重置
              </Button>
              <Button
                type="primary"
                icon={isExecuting ? <LoadingOutlined /> : <PlayCircleOutlined />}
                onClick={handleSubmit}
                disabled={selectedActions.length === 0 || isExecuting}
                loading={isExecuting}
                style={{ borderRadius: 6 }}
              >
                {isExecuting ? '执行中...' : '执行'}
              </Button>
            </Space>
          </div>
        }
        styles={{
          header: {
            borderBottom: '2px solid #f0f0f0',
            padding: '12px 16px',
          },
          body: {
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            flex: 1,
          },
        }}
        style={{
          flex: 1,
          minWidth: 200,
          borderRadius: 10,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Source Object Selector */}
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', background: '#fafafa' }}>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            执行源对象:
          </Text>
          <Select
            style={{ width: '100%' }}
            placeholder="选择源对象实例"
            value={selectedSourceId || undefined}
            onChange={setSelectedSourceId}
            loading={sandboxLoading}
            showSearch
            optionFilterProp="children"
          >
            {allInstances.map((inst) => (
              <Select.Option key={inst.id} value={inst.id}>
                [{inst.typeName}] {inst.properties?.callsign || inst.properties?.name || inst.id.slice(0, 8)}
              </Select.Option>
            ))}
          </Select>
        </div>

        <div
          style={{
            flex: 1,
            padding: '16px',
            overflow: 'auto',
            background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          }}
        >
          {selectedActions.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 14 }}>
                    从左侧行为库选择行为添加到编排中
                  </Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: 12, opacity: 0.7 }}>
                    支持 OODA 循环：观察 → 定向 → 决策 → 行动
                  </Text>
                </div>
              }
              style={{ marginTop: 80 }}
            />
          ) : (
            <div style={{ position: 'relative' }}>
              {/* Connection line */}
              <div
                style={{
                  position: 'absolute',
                  left: 23,
                  top: 40,
                  bottom: 40,
                  width: 2,
                  background: 'linear-gradient(180deg, #1677ff 0%, #6366f1 50%, #10b981 100%)',
                  borderRadius: 1,
                  opacity: 0.3,
                }}
              />
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {selectedActions.map((action, index) => {
                  const config = CATEGORY_CONFIG[action.category] || CATEGORY_CONFIG.Default;
                  return (
                    <div
                      key={action.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 16,
                        padding: '16px 20px',
                        background: '#fff',
                        borderRadius: 10,
                        border: '1px solid #e5e7eb',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                        transition: 'all 0.2s ease',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
                      }}
                    >
                      {/* Step number */}
                      <div
                        style={{
                          width: 36,
                          height: 36,
                          borderRadius: '50%',
                          background: `linear-gradient(135deg, ${config.color} 0%, ${config.color}dd 100%)`,
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 600,
                          fontSize: 14,
                          flexShrink: 0,
                          boxShadow: `0 2px 8px ${config.color}40`,
                        }}
                      >
                        {index + 1}
                      </div>

                      {/* Action info */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                          <Text strong style={{ fontSize: 14 }}>
                            {action.actionName}
                          </Text>
                          <Tag
                            style={{
                              color: config.color,
                              background: config.bgColor,
                              border: 'none',
                              borderRadius: 4,
                              fontSize: 11,
                            }}
                          >
                            {action.category}
                          </Tag>
                        </div>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {action.actionApiName}
                        </Text>
                      </div>

                      {/* Delete button */}
                      <Tooltip title="移除">
                        <Button
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => handleRemoveAction(action.id)}
                          disabled={isExecuting}
                          style={{ borderRadius: 6 }}
                        />
                      </Tooltip>
                    </div>
                  );
                })}
              </Space>
            </div>
          )}
        </div>
      </Card>

      {/* Column 3: Monitor Panel */}
      <div style={{ width: 280, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {/* Console / Logs */}
        <Card
          title={
            <Space>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: isExecuting ? '#f59e0b' : '#10b981',
                  animation: isExecuting ? 'pulse 1s infinite' : 'none',
                }}
              />
              <span>控制台</span>
            </Space>
          }
          extra={
            <Text type="secondary" style={{ fontSize: 11 }}>
              {logs.length} 条日志
            </Text>
          }
          styles={{
            header: {
              borderBottom: 'none',
              padding: '12px 16px',
              background: '#1e1e1e',
              color: '#fff',
            },
            body: {
              padding: 0,
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
            },
          }}
          style={{
            flex: 1,
            borderRadius: 12,
            overflow: 'hidden',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            style={{
              flex: 1,
              padding: '16px',
              background: '#1e1e1e',
              fontFamily: '"Fira Code", "JetBrains Mono", Consolas, monospace',
              fontSize: 12,
              lineHeight: 1.8,
              overflow: 'auto',
              maxHeight: 300,
            }}
          >
            {logs.length === 0 ? (
              <>
                <div style={{ color: '#4ec9b0' }}>
                  <span style={{ color: '#6a9955' }}>[INFO]</span> 系统初始化中...
                </div>
                <div style={{ color: '#6a9955', marginTop: 8 }}>
                  <span style={{ opacity: 0.5 }}>{'>'}</span> _
                </div>
              </>
            ) : (
              logs.map((log) => {
                let color = '#4ec9b0';
                let prefix = '[INFO]';
                let prefixColor = '#6a9955';

                if (log.status === 'success') {
                  color = '#4ec9b0';
                  prefix = '[OK]';
                  prefixColor = '#10b981';
                } else if (log.status === 'error' || log.status === 'failed') {
                  color = '#ff6b6b';
                  prefix = '[ERR]';
                  prefixColor = '#ef4444';
                } else if (log.status === 'running' || log.status === 'pending') {
                  color = '#dcdcaa';
                  prefix = '[RUN]';
                  prefixColor = '#f59e0b';
                }

                return (
                  <div key={log.id} style={{ color, marginBottom: 4 }}>
                    <span style={{ color: prefixColor }}>{prefix}</span> {log.actionName}
                    {log.message && (
                      <span style={{ color: '#6a9955', marginLeft: 8, fontSize: 11 }}>
                        ({log.message.slice(0, 50)})
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Sandbox State */}
        <Card
          title={
            <Space>
              <TeamOutlined style={{ color: '#6366f1' }} />
              <span>沙箱状态</span>
            </Space>
          }
          extra={
            <Space>
              <Tooltip title="刷新">
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={refreshSandbox}
                  loading={sandboxLoading}
                />
              </Tooltip>
              <Tag color={sandboxLoading ? 'orange' : 'green'} style={{ borderRadius: 4 }}>
                {sandboxLoading ? '加载中' : '在线'}
              </Tag>
            </Space>
          }
          styles={{
            header: {
              borderBottom: '2px solid #f0f0f0',
              padding: '12px 16px',
            },
            body: {
              padding: '12px 16px',
              flex: 1,
              overflow: 'auto',
            },
          }}
          style={{
            flex: 1,
            borderRadius: 12,
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {sandboxLoading ? (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <Spin size="small" />
            </div>
          ) : Object.keys(sandboxInstances).length === 0 ? (
            <Empty description="暂无沙箱数据" image={Empty.PRESENTED_IMAGE_SIMPLE} style={{ margin: '20px 0' }} />
          ) : (
            <div
              style={{
                fontFamily: '"Fira Code", "JetBrains Mono", Consolas, monospace',
                fontSize: 11,
                background: '#f8fafc',
                padding: '12px',
                borderRadius: 8,
                border: '1px solid #e5e7eb',
                maxHeight: 200,
                overflow: 'auto',
              }}
            >
              {Object.entries(sandboxInstances).map(([typeName, instances]) => (
                <div key={typeName} style={{ marginBottom: 12 }}>
                  <Text strong style={{ color: '#6366f1', fontSize: 12 }}>
                    {typeName} ({instances.length})
                  </Text>
                  {instances.slice(0, 3).map((inst) => (
                    <div
                      key={inst.id}
                      style={{
                        marginLeft: 8,
                        marginTop: 4,
                        padding: '4px 8px',
                        background: inst.id === selectedSourceId ? '#e0f2fe' : '#fff',
                        borderRadius: 4,
                        fontSize: 10,
                        cursor: 'pointer',
                        border: inst.id === selectedSourceId ? '1px solid #0ea5e9' : '1px solid #e5e7eb',
                      }}
                      onClick={() => setSelectedSourceId(inst.id)}
                    >
                      <div style={{ color: '#374151' }}>
                        {inst.properties?.callsign || inst.properties?.name || inst.id.slice(0, 12)}
                      </div>
                      {inst.properties?.status && (
                        <Tag
                          color={inst.properties.status === 'Ready' ? 'green' : 'orange'}
                          style={{ fontSize: 9, padding: '0 4px', marginTop: 2 }}
                        >
                          {inst.properties.status}
                        </Tag>
                      )}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Pulse animation for console indicator */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default OntologyTest;
