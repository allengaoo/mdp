/**
 * Function Definition Editor component.
 * Tabs layout for editing existing function definitions.
 * Uses V3 API. Supports code test run.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  Select,
  Table,
  Space,
  Switch,
  Tabs,
  message,
  Card,
  Typography,
  Alert,
  Spin,
  Tag,
  Collapse,
} from 'antd';
import {
  PlusOutlined,
  MinusCircleOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  CodeOutlined,
} from '@ant-design/icons';
import { updateFunction } from '../../api/v3/logic';
import apiClient from '../../api/axios';
import { useParams } from 'react-router-dom';

const { TextArea } = Input;
const { TabPane } = Tabs;
const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface FunctionDefinitionData {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  code_content?: string;
  bound_object_type_id?: string | null;
  input_params_schema?: Array<{
    name: string;
    type: string;
    required: boolean;
  }>;
  output_type?: string;
}

interface FunctionEditorProps {
  visible: boolean;
  function: FunctionDefinitionData;
  onCancel: () => void;
  onSuccess: () => void;
}

interface Parameter {
  name: string;
  type: string;
  required: boolean;
}

interface ExecutionResult {
  success: boolean;
  result: any;
  stdout: string;
  stderr: string;
  execution_time_ms: number;
  executor_used: string;
  error_message?: string;
  error_type?: string;
  traceback?: string;
}

const DATA_TYPES = ['string', 'number', 'integer', 'boolean', 'object', 'array', 'date'];
const OUTPUT_TYPES = ['VOID', 'STRING', 'INTEGER', 'DOUBLE', 'BOOLEAN', 'OBJECT', 'OBJECT_REF', 'ARRAY'];

const FunctionEditor: React.FC<FunctionEditorProps> = ({
  visible,
  function: funcData,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [outputType, setOutputType] = useState<string>('VOID');
  const [codeContent, setCodeContent] = useState<string>('');
  const [testInputs, setTestInputs] = useState<Record<string, any>>({});
  const [testResult, setTestResult] = useState<ExecutionResult | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  // Initialize form data
  useEffect(() => {
    if (visible && funcData) {
      // Set form values
      form.setFieldsValue({
        display_name: funcData.display_name,
        api_name: funcData.api_name,
        description: funcData.description || '',
      });

      // Set state
      setOutputType(funcData.output_type || 'VOID');
      setCodeContent(funcData.code_content || '');

      // Set parameters
      if (funcData.input_params_schema) {
        setParameters(
          funcData.input_params_schema.map((p) => ({
            name: p.name,
            type: p.type,
            required: p.required,
          }))
        );
      }
    }
  }, [visible, funcData, form]);

  // Initialize test inputs when parameters change
  useEffect(() => {
    if (parameters.length > 0) {
      const inputs: Record<string, any> = {};
      parameters.forEach((param) => {
        if (param.name) {
          switch (param.type) {
            case 'string':
              inputs[param.name] = '';
              break;
            case 'number':
            case 'integer':
              inputs[param.name] = 0;
              break;
            case 'boolean':
              inputs[param.name] = false;
              break;
            case 'array':
              inputs[param.name] = [];
              break;
            case 'object':
              inputs[param.name] = {};
              break;
            default:
              inputs[param.name] = '';
          }
        }
      });
      setTestInputs(inputs);
    }
  }, [parameters]);

  // Handle save
  const handleSave = async () => {
    try {
      const values = form.getFieldsValue();

      const payload = {
        display_name: values.display_name,
        description: values.description || undefined,
        code_content: codeContent || undefined,
        input_params_schema: parameters.length > 0 ? parameters : undefined,
        output_type: outputType,
        bound_object_type_id: values.bound_object_type_id || null,
      };

      await updateFunction(funcData.id, payload);
      message.success('Function definition updated successfully');
      onSuccess();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update function definition');
    }
  };

  // Add parameter
  const addParameter = () => {
    setParameters([...parameters, { name: '', type: 'string', required: false }]);
  };

  // Remove parameter
  const removeParameter = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  // Update parameter
  const updateParameter = (index: number, field: keyof Parameter, value: any) => {
    const updated = [...parameters];
    updated[index] = { ...updated[index], [field]: value };
    setParameters(updated);
  };

  // Handle test run - 调用真实的后端 API
  const handleTestRun = async () => {
    if (!codeContent.trim()) {
      message.warning('请先编写代码');
      return;
    }

    setIsRunning(true);
    setTestResult(null);

    try {
      // 构建执行上下文
      const context = {
        params: testInputs,
        source: {
          id: 'test-source-id',
          object_type_id: funcData.bound_object_type_id || 'unknown',
          properties: testInputs,
        },
      };

      // 调用后端试运行 API
      const response = await apiClient.post('/execute/code/test', {
        code_content: codeContent,
        context: context,
        executor_type: 'auto',
        timeout_seconds: 30,
      });

      const result: ExecutionResult = response.data;
      setTestResult(result);

      if (result.success) {
        message.success(`执行成功 (${result.execution_time_ms}ms)`);
      } else {
        message.error(`执行失败: ${result.error_type || 'Error'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || '执行失败';
      setTestResult({
        success: false,
        result: null,
        stdout: '',
        stderr: '',
        execution_time_ms: 0,
        executor_used: 'unknown',
        error_message: errorMessage,
        error_type: 'NetworkError',
      });
      message.error(`请求失败: ${errorMessage}`);
    } finally {
      setIsRunning(false);
    }
  };

  const paramColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (_: any, record: Parameter, index: number) => (
        <Input
          value={record.name}
          onChange={(e) => updateParameter(index, 'name', e.target.value)}
          placeholder="param_name"
          style={{ fontFamily: 'monospace' }}
        />
      ),
    },
    {
      title: 'Data Type',
      dataIndex: 'type',
      key: 'type',
      render: (_: any, record: Parameter, index: number) => (
        <Select
          value={record.type}
          onChange={(value) => updateParameter(index, 'type', value)}
          style={{ width: '100%' }}
        >
          {DATA_TYPES.map((type) => (
            <Select.Option key={type} value={type}>
              {type}
            </Select.Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Required?',
      dataIndex: 'required',
      key: 'required',
      render: (_: any, record: Parameter, index: number) => (
        <Switch
          checked={record.required}
          onChange={(checked) => updateParameter(index, 'required', checked)}
        />
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, __: Parameter, index: number) => (
        <Button
          type="link"
          danger
          icon={<MinusCircleOutlined />}
          onClick={() => removeParameter(index)}
        >
          Remove
        </Button>
      ),
    },
  ];

  return (
    <Modal
      title="Edit Function Definition"
      open={visible}
      onCancel={onCancel}
      width={1000}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="save" type="primary" onClick={handleSave}>
          Save Changes
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical">
        <Tabs defaultActiveKey="basic">
          {/* Tab 1: Basic Info */}
          <TabPane tab="Basic" key="basic">
            <Form.Item
              label="Display Name"
              name="display_name"
              rules={[{ required: true, message: 'Please enter display name' }]}
            >
              <Input placeholder="Function Name" />
            </Form.Item>

            <Form.Item label="API Name" name="api_name">
              <Input placeholder="api_name" style={{ fontFamily: 'monospace' }} disabled />
            </Form.Item>

            <Form.Item label="Description" name="description">
              <TextArea rows={3} placeholder="Function description" />
            </Form.Item>
          </TabPane>

          {/* Tab 2: Signature */}
          <TabPane tab="Signature" key="signature">
            <div style={{ marginBottom: 24 }}>
              <h4>Input Parameters</h4>
              <Table
                columns={paramColumns}
                dataSource={parameters}
                rowKey={(_, index) => `param-${index}`}
                pagination={false}
                size="small"
                footer={() => (
                  <Button type="dashed" icon={<PlusOutlined />} onClick={addParameter} block>
                    Add Parameter
                  </Button>
                )}
              />
            </div>

            <div>
              <h4>Return Type</h4>
              <Select
                value={outputType}
                onChange={setOutputType}
                style={{ width: '100%' }}
                size="large"
              >
                {OUTPUT_TYPES.map((type) => (
                  <Select.Option key={type} value={type}>
                    {type}
                  </Select.Option>
                ))}
              </Select>
            </div>
          </TabPane>

          {/* Tab 3: Code */}
          <TabPane tab="Code" key="code">
            <div style={{ marginBottom: 24 }}>
              <h4>Code Implementation</h4>
              <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 8 }}>
                Note: For better code editing experience, consider installing @monaco-editor/react
              </Paragraph>
              <TextArea
                value={codeContent}
                onChange={(e) => setCodeContent(e.target.value)}
                rows={15}
                style={{ fontFamily: 'monospace', fontSize: 13 }}
                placeholder="def main(...): ..."
              />
            </div>

            {/* Test Runner */}
            <Card
              title={
                <Space>
                  <PlayCircleOutlined />
                  <span>Dry Run / 试运行</span>
                </Space>
              }
              size="small"
            >
              <div style={{ marginBottom: 16 }}>
                <h5>Input Parameters</h5>
                {parameters.length === 0 ? (
                  <Text type="secondary">No parameters defined</Text>
                ) : (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {parameters.map((param) => {
                      if (!param.name) return null;
                      return (
                        <div key={param.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <Text strong style={{ width: 120 }}>
                            {param.name} ({param.type}):
                          </Text>
                          {param.type === 'boolean' ? (
                            <Switch
                              checked={testInputs[param.name] || false}
                              onChange={(checked) =>
                                setTestInputs({ ...testInputs, [param.name]: checked })
                              }
                            />
                          ) : param.type === 'number' || param.type === 'integer' ? (
                            <Input
                              type="number"
                              value={testInputs[param.name] || ''}
                              onChange={(e) =>
                                setTestInputs({
                                  ...testInputs,
                                  [param.name]: Number(e.target.value),
                                })
                              }
                              style={{ flex: 1 }}
                            />
                          ) : (
                            <Input
                              value={testInputs[param.name] || ''}
                              onChange={(e) =>
                                setTestInputs({ ...testInputs, [param.name]: e.target.value })
                              }
                              style={{ flex: 1 }}
                              placeholder={`Enter ${param.type} value`}
                            />
                          )}
                        </div>
                      );
                    })}
                  </Space>
                )}
              </div>

              <div style={{ marginBottom: 16 }}>
                <Button
                  type="primary"
                  icon={isRunning ? <LoadingOutlined /> : <PlayCircleOutlined />}
                  onClick={handleTestRun}
                  loading={isRunning}
                >
                  {isRunning ? '执行中...' : '运行'}
                </Button>
              </div>

              {/* 执行结果展示 */}
              {testResult && (
                <div>
                  {/* 状态栏 */}
                  <div style={{ marginBottom: 12 }}>
                    {testResult.success ? (
                      <Alert
                        message={
                          <Space>
                            <CheckCircleOutlined />
                            <span>执行成功</span>
                            <Tag color="blue">{testResult.execution_time_ms}ms</Tag>
                            <Tag color="green">{testResult.executor_used}</Tag>
                          </Space>
                        }
                        type="success"
                        showIcon={false}
                      />
                    ) : (
                      <Alert
                        message={
                          <Space>
                            <CloseCircleOutlined />
                            <span>执行失败</span>
                            <Tag color="red">{testResult.error_type}</Tag>
                          </Space>
                        }
                        description={testResult.error_message}
                        type="error"
                        showIcon={false}
                      />
                    )}
                  </div>

                  {/* 返回值 */}
                  {testResult.success && (
                    <div style={{ marginBottom: 12 }}>
                      <Text strong>返回值:</Text>
                      <div
                        style={{
                          background: '#f6f8fa',
                          padding: '8px 12px',
                          borderRadius: 4,
                          fontFamily: 'monospace',
                          fontSize: 13,
                          marginTop: 4,
                          maxHeight: 150,
                          overflow: 'auto',
                        }}
                      >
                        {testResult.result === null
                          ? <Text type="secondary">null</Text>
                          : typeof testResult.result === 'object'
                          ? JSON.stringify(testResult.result, null, 2)
                          : String(testResult.result)}
                      </div>
                    </div>
                  )}

                  {/* 标准输出/错误 */}
                  <Collapse ghost size="small">
                    {testResult.stdout && (
                      <Panel
                        header={
                          <Space>
                            <CodeOutlined />
                            <span>标准输出 (stdout)</span>
                          </Space>
                        }
                        key="stdout"
                      >
                        <pre
                          style={{
                            background: '#1e1e1e',
                            color: '#d4d4d4',
                            padding: 12,
                            borderRadius: 4,
                            fontSize: 12,
                            margin: 0,
                            maxHeight: 200,
                            overflow: 'auto',
                          }}
                        >
                          {testResult.stdout}
                        </pre>
                      </Panel>
                    )}
                    {testResult.stderr && (
                      <Panel
                        header={
                          <Space>
                            <CodeOutlined style={{ color: '#ff4d4f' }} />
                            <span style={{ color: '#ff4d4f' }}>标准错误 (stderr)</span>
                          </Space>
                        }
                        key="stderr"
                      >
                        <pre
                          style={{
                            background: '#2d1f1f',
                            color: '#ff6b6b',
                            padding: 12,
                            borderRadius: 4,
                            fontSize: 12,
                            margin: 0,
                            maxHeight: 200,
                            overflow: 'auto',
                          }}
                        >
                          {testResult.stderr}
                        </pre>
                      </Panel>
                    )}
                    {testResult.traceback && (
                      <Panel
                        header={
                          <Space>
                            <CodeOutlined style={{ color: '#ff4d4f' }} />
                            <span style={{ color: '#ff4d4f' }}>错误堆栈</span>
                          </Space>
                        }
                        key="traceback"
                      >
                        <pre
                          style={{
                            background: '#2d1f1f',
                            color: '#ff6b6b',
                            padding: 12,
                            borderRadius: 4,
                            fontSize: 11,
                            margin: 0,
                            maxHeight: 300,
                            overflow: 'auto',
                          }}
                        >
                          {testResult.traceback}
                        </pre>
                      </Panel>
                    )}
                  </Collapse>
                </div>
              )}
            </Card>
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

export default FunctionEditor;

