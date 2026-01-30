/**
 * Chat2App Page Component
 * MDP Platform V3.1
 * 
 * Natural language to data visualization interface.
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, Input, Button, Space, Typography, Spin, 
  Alert, Tag, Divider, List, message, Dropdown 
} from 'antd';
import { 
  SendOutlined, RobotOutlined, UserOutlined, 
  CodeOutlined, ReloadOutlined, BugOutlined 
} from '@ant-design/icons';
import { AmisRenderer } from '../../../components/common/AmisRenderer';
import v3Client from '../../../api/v3/client';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  amis_schema?: any;
  suggestions?: string[];
  timestamp: Date;
}

interface HealthStatus {
  ollama_available: boolean;
  model: string;
  status: string;
}

export const Chat2AppPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkHealth = async () => {
    try {
      const res = await v3Client.get('/chat/health');
      setHealth(res.data);
    } catch (err) {
      setHealth({ ollama_available: false, model: 'unknown', status: 'error' });
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await v3Client.post('/chat/message', {
        message: userMessage.content,
        history: messages.slice(-10).map((m) => ({
          role: m.role,
          content: m.content,
        })),
      });

      const data = res.data;
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.message,
        sql: data.sql,
        amis_schema: data.amis_schema,
        suggestions: data.suggestions,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      message.error('请求失败: ' + (err.response?.data?.detail || err.message));
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '抱歉，处理您的请求时发生错误。',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /**
   * Debug: Test AMIS Renderer with hardcoded valid schemas
   * This helps isolate whether the issue is with the Renderer component or LLM output structure
   */
  const testAmisRenderer = (schemaType: 'table' | 'chart' | 'form' | 'table-api') => {
    console.log('[Chat2App] Testing AMIS Renderer with type:', schemaType);
    
    let testSchema: any;
    let testContent: string;

    switch (schemaType) {
      case 'table':
        testSchema = {
          type: 'table',
          columns: [
            { name: 'id', label: 'ID' },
            { name: 'name', label: '名称' },
            { name: 'status', label: '状态' },
            { name: 'count', label: '数量' },
          ],
          data: {
            items: [
              { id: 1, name: '测试对象1', status: 'active', count: 100 },
              { id: 2, name: '测试对象2', status: 'inactive', count: 200 },
              { id: 3, name: '测试对象3', status: 'active', count: 150 },
              { id: 4, name: '测试对象4', status: 'pending', count: 80 },
            ],
          },
        };
        testContent = '这是测试表格数据（硬编码）';
        break;

      case 'chart':
        testSchema = {
          type: 'chart',
          config: {
            xAxis: {
              type: 'category',
              data: ['一月', '二月', '三月', '四月', '五月'],
            },
            yAxis: {
              type: 'value',
            },
            series: [
              {
                type: 'bar',
                data: [120, 200, 150, 80, 70],
                name: '数量',
              },
            ],
            title: {
              text: '测试图表',
            },
          },
        };
        testContent = '这是测试图表数据（硬编码）';
        break;

      case 'form':
        testSchema = {
          type: 'form',
          body: {
            type: 'form',
            controls: [
              { type: 'text', name: 'name', label: '名称' },
              { type: 'number', name: 'age', label: '年龄' },
            ],
          },
        };
        testContent = '这是测试表单数据（硬编码）';
        break;

      case 'table-api':
        // Test schema with API configuration
        testSchema = {
          type: 'table',
          columns: [
            { name: 'id', label: 'ID' },
            { name: 'name', label: '名称' },
            { name: 'status', label: '状态' },
          ],
          // API config for dynamic data fetching
          api: {
            url: '/search/objects',
            method: 'POST',
            data: {
              q: '海上',
              page: 1,
              page_size: 5,
            },
          },
        };
        testContent = '这是测试表格数据（通过 API 获取）';
        break;

      default:
        return;
    }

    console.log('[Chat2App] Test schema:', JSON.stringify(testSchema, null, 2));

    const testMessage: ChatMessage = {
      role: 'assistant',
      content: testContent,
      amis_schema: testSchema,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, testMessage]);
    message.success(`已添加 ${schemaType} 类型测试消息`);
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <RobotOutlined style={{ fontSize: 24 }} />
            <div>
              <Text strong style={{ fontSize: 18 }}>Chat2App</Text>
              <br />
              <Text type="secondary">用自然语言查询和分析数据</Text>
            </div>
          </Space>
          <Space>
            <Tag color={health?.ollama_available ? 'green' : 'red'}>
              {health?.status || '检查中...'}
            </Tag>
            <Button icon={<ReloadOutlined />} onClick={checkHealth} size="small">
              刷新状态
            </Button>
            {/* Debug Button - Temporary for AMIS rendering testing */}
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'table',
                    label: '测试表格渲染',
                    onClick: () => testAmisRenderer('table'),
                  },
                  {
                    key: 'chart',
                    label: '测试图表渲染',
                    onClick: () => testAmisRenderer('chart'),
                  },
                  {
                    key: 'form',
                    label: '测试表单渲染',
                    onClick: () => testAmisRenderer('form'),
                  },
                  {
                    key: 'table-api',
                    label: '测试表格（API 数据源）',
                    onClick: () => testAmisRenderer('table-api'),
                  },
                ],
              }}
              placement="bottomRight"
            >
              <Button 
                icon={<BugOutlined />} 
                size="small"
                danger
              >
                调试 AMIS
              </Button>
            </Dropdown>
          </Space>
        </Space>
      </Card>

      {/* Health Warning */}
      {health && !health.ollama_available && (
        <Alert
          message="AI 服务未连接"
          description="请确保 Ollama 服务正在运行。执行: ollama serve"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Chat Messages */}
      <Card 
        style={{ marginBottom: 16, minHeight: 400, maxHeight: 600, overflow: 'auto' }}
        bodyStyle={{ padding: 16 }}
      >
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <RobotOutlined style={{ fontSize: 48, color: '#ccc' }} />
            <Paragraph type="secondary" style={{ marginTop: 16 }}>
              试试问我：
            </Paragraph>
            <Space wrap>
              {['显示所有对象', '统计对象类型', '最近创建的记录'].map((q) => (
                <Tag 
                  key={q} 
                  style={{ cursor: 'pointer' }} 
                  onClick={() => handleSuggestionClick(q)}
                >
                  {q}
                </Tag>
              ))}
            </Space>
          </div>
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg, idx) => (
              <List.Item 
                key={idx}
                style={{ 
                  flexDirection: 'column', 
                  alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  border: 'none',
                  padding: '8px 0',
                }}
              >
                <Space align="start" style={{ maxWidth: '85%' }}>
                  {msg.role === 'assistant' && <RobotOutlined />}
                  <div>
                    <Card 
                      size="small" 
                      style={{ 
                        background: msg.role === 'user' ? '#e6f7ff' : '#f5f5f5',
                      }}
                    >
                      <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                        {msg.content}
                      </Paragraph>
                      
                      {/* Show SQL */}
                      {msg.sql && (
                        <>
                          <Divider style={{ margin: '8px 0' }} />
                          <details>
                            <summary style={{ cursor: 'pointer', color: '#1890ff' }}>
                              <CodeOutlined /> 查看 SQL
                            </summary>
                            <pre style={{ 
                              fontSize: 12, 
                              background: '#f0f0f0', 
                              padding: 8, 
                              borderRadius: 4,
                              overflow: 'auto',
                            }}>
                              {msg.sql}
                            </pre>
                          </details>
                        </>
                      )}
                    </Card>

                    {/* AMIS Rendered Content */}
                    {msg.amis_schema && (
                      <div style={{ marginTop: 8 }}>
                        <AmisRenderer schema={msg.amis_schema} />
                      </div>
                    )}

                    {/* Suggestions */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <Space wrap style={{ marginTop: 8 }}>
                        {msg.suggestions.map((s, i) => (
                          <Tag 
                            key={i} 
                            style={{ cursor: 'pointer' }}
                            onClick={() => handleSuggestionClick(s)}
                          >
                            {s}
                          </Tag>
                        ))}
                      </Space>
                    )}
                  </div>
                  {msg.role === 'user' && <UserOutlined />}
                </Space>
              </List.Item>
            )}
          />
        )}
        <div ref={messagesEndRef} />
        {loading && (
          <div style={{ textAlign: 'center', padding: 16 }}>
            <Spin tip="思考中..." />
          </div>
        )}
      </Card>

      {/* Input Area */}
      <Card bodyStyle={{ padding: 16 }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题，例如：显示所有目标对象..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />}
            onClick={sendMessage}
            loading={loading}
            disabled={!input.trim()}
          >
            发送
          </Button>
        </Space.Compact>
      </Card>
    </div>
  );
};

export default Chat2AppPage;
