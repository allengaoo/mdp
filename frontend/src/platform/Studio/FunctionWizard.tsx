/**
 * Function Definition Wizard component.
 * 3-step wizard for creating new function definitions.
 * Uses V3 API. Supports projectId for Studio (project-scoped) vs OMA (global).
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Steps,
  Form,
  Input,
  Button,
  Select,
  Table,
  Space,
  Switch,
  message,
  Card,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  MinusCircleOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { createFunction } from '../../api/v3/logic';
import v3Client from '../../api/v3/client';

const { TextArea } = Input;
const { Step } = Steps;
const { Text, Paragraph } = Typography;

interface FunctionWizardProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  /** Project ID for Studio (project-scoped). OMA passes undefined for global. */
  projectId?: string | null;
}

interface Parameter {
  name: string;
  type: string;
  required: boolean;
}

const DATA_TYPES = ['string', 'number', 'integer', 'boolean', 'object', 'array', 'date'];
const OUTPUT_TYPES = ['VOID', 'STRING', 'INTEGER', 'DOUBLE', 'BOOLEAN', 'OBJECT', 'OBJECT_REF', 'ARRAY'];

const FunctionWizard: React.FC<FunctionWizardProps> = ({ visible, onCancel, onSuccess, projectId: projectIdProp }) => {
  const { projectId: projectIdFromRoute } = useParams<{ projectId: string }>();
  // Prefer explicit prop (OMA passes undefined); fallback to route (Studio)
  const projectId = projectIdProp !== undefined ? projectIdProp : projectIdFromRoute;
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [outputType, setOutputType] = useState<string>('VOID');
  const [codeContent, setCodeContent] = useState<string>('');
  const [testInputs, setTestInputs] = useState<Record<string, any>>({});
  const [testResult, setTestResult] = useState<string>('');
  const [testLoading, setTestLoading] = useState(false);

  // Generate function stub when parameters or output type change
  useEffect(() => {
    if (currentStep === 2 && parameters.length > 0) {
      generateFunctionStub();
    }
  }, [parameters, outputType, currentStep]);

  // Generate function stub based on parameters
  const generateFunctionStub = () => {
    const formValues = form.getFieldsValue();
    const apiName = formValues.api_name || 'main';
    
    const paramList = parameters
      .map((p) => p.name)
      .filter((name) => name)
      .join(', ');
    
    const returnType = outputType === 'VOID' ? '' : ` -> ${outputType}`;
    
    const stub = `def ${apiName}(${paramList || '...'})${returnType}:
    """
    ${formValues.description || 'Function description'}
    """
    # TODO: Implement function logic
    ${outputType !== 'VOID' ? 'return None' : 'pass'}
`;
    
    if (!codeContent || codeContent.trim() === '') {
      setCodeContent(stub);
    }
  };

  // Initialize test inputs when parameters change
  useEffect(() => {
    if (currentStep === 2 && parameters.length > 0) {
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
  }, [parameters, currentStep]);

  // Handle next step
  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['api_name', 'display_name']);
      } else if (currentStep === 1) {
        // Validate parameters if any are defined
        if (parameters.length > 0) {
          const hasInvalid = parameters.some((p) => !p.name || !p.type);
          if (hasInvalid) {
            message.error('Please complete all parameter definitions');
            return;
          }
        }
      }
      setCurrentStep(currentStep + 1);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  // Handle previous step
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // Handle finish
  const handleFinish = async () => {
    try {
      const values = form.getFieldsValue();
      
      const payload = {
        api_name: values.api_name,
        display_name: values.display_name,
        description: values.description || undefined,
        code_content: codeContent || undefined,
        input_params_schema: parameters.length > 0 ? parameters : undefined,
        output_type: outputType,
        bound_object_type_id: values.bound_object_type_id || null,
        project_id: projectId || null,
      };

      await createFunction(payload);
      message.success('Function definition created successfully');
      handleReset();
      onSuccess();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to create function definition');
    }
  };

  // Reset form
  const handleReset = () => {
    form.resetFields();
    setCurrentStep(0);
    setParameters([]);
    setOutputType('VOID');
    setCodeContent('');
    setTestInputs({});
    setTestResult('');
  };

  // Handle cancel
  const handleCancel = () => {
    handleReset();
    onCancel();
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

  // Handle test run - Call real API
  const handleTestRun = async () => {
    if (!codeContent.trim()) {
      message.warning('请先编写代码');
      return;
    }

    setTestLoading(true);
    setTestResult('');

    try {
      const response = await v3Client.post('/execute/code/test', {
        code_content: codeContent,
        context: testInputs, // params merged into context
      });

      const result = response.data;
      setTestResult(JSON.stringify(result, null, 2));

      if (result.success) {
        message.success(`执行成功 (${result.execution_time_ms || 0}ms)`);
      } else {
        message.error(`执行失败: ${result.error || '未知错误'}`);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || '执行失败';
      setTestResult(JSON.stringify({ success: false, error: errorMsg }, null, 2));
      message.error(errorMsg);
    } finally {
      setTestLoading(false);
    }
  };

  // Auto-generate API name from display name
  const handleDisplayNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const displayName = e.target.value;
    const apiName = displayName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    form.setFieldsValue({ api_name: apiName });
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
      title="Create Function Definition"
      open={visible}
      onCancel={handleCancel}
      width={1000}
      footer={null}
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="Basic Info" />
        <Step title="Signature" />
        <Step title="Implementation & Test" />
      </Steps>

      <Form form={form} layout="vertical" preserve={true}>
        {/* Step 1: Basic Info */}
        {currentStep === 0 && (
          <div>
            <Form.Item
              label="Display Name"
              name="display_name"
              rules={[{ required: true, message: 'Please enter display name' }]}
            >
              <Input placeholder="Function Name" onChange={handleDisplayNameChange} />
            </Form.Item>

            <Form.Item
              label="API Name"
              name="api_name"
              rules={[{ required: true, message: 'Please enter API name' }]}
            >
              <Input placeholder="api_name" style={{ fontFamily: 'monospace' }} />
            </Form.Item>

            <Form.Item label="Description" name="description">
              <TextArea rows={3} placeholder="Function description" />
            </Form.Item>
          </div>
        )}

        {/* Step 2: Signature */}
        {currentStep === 1 && (
          <div>
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
          </div>
        )}

        {/* Step 3: Implementation & Test */}
        {currentStep === 2 && (
          <div>
            {/* Code Editor */}
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
                <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleTestRun} loading={testLoading}>
                  {testLoading ? 'Running...' : 'Run'}
                </Button>
              </div>

              {testResult && (
                <div>
                  <h5>Output</h5>
                  <TextArea
                    value={testResult}
                    readOnly
                    rows={6}
                    style={{ fontFamily: 'monospace', fontSize: 12, background: '#f5f5f5' }}
                  />
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Footer Buttons */}
        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={handleCancel}>Cancel</Button>
          <Space>
            {currentStep > 0 && <Button onClick={handlePrev}>Previous</Button>}
            {currentStep < 2 ? (
              <Button type="primary" onClick={handleNext}>
                Next
              </Button>
            ) : (
              <Button type="primary" onClick={handleFinish}>
                Create
              </Button>
            )}
          </Space>
        </div>
      </Form>
    </Modal>
  );
};

export default FunctionWizard;

