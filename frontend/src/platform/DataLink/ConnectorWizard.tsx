/**
 * Connector Wizard - MDP Platform V3.1
 * 
 * Dynamic form for creating/editing data connections.
 * Renders fields based on ConnectorConfigRegistry.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Typography,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Space,
  Card,
  Steps,
  Result,
  Alert,
  Spin,
  Divider,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import {
  fetchConnector,
  createConnector,
  updateConnector,
  testConnection,
  IConnectionRead,
  IConnectionCreate,
  ConnectorType,
} from '../../api/v3/connectors';
import {
  CONNECTOR_REGISTRY,
  getConnectorTypes,
  buildDefaultConfig,
  FieldDefinition,
} from './ConnectorConfigRegistry';

const { Title, Text, Paragraph } = Typography;

// ==========================================
// Dynamic Field Renderer
// ==========================================

interface DynamicFieldProps {
  field: FieldDefinition;
}

const DynamicField: React.FC<DynamicFieldProps> = ({ field }) => {
  const rules = field.required ? [{ required: true, message: `请输入${field.label}` }] : [];

  switch (field.type) {
    case 'password':
      return (
        <Form.Item
          name={['config_json', field.name]}
          label={field.label}
          rules={rules}
          tooltip={field.tooltip}
        >
          <Input.Password placeholder={field.placeholder} />
        </Form.Item>
      );

    case 'number':
      return (
        <Form.Item
          name={['config_json', field.name]}
          label={field.label}
          rules={rules}
          tooltip={field.tooltip}
        >
          <InputNumber
            style={{ width: '100%' }}
            placeholder={field.placeholder}
            min={field.min}
            max={field.max}
          />
        </Form.Item>
      );

    case 'select':
      return (
        <Form.Item
          name={['config_json', field.name]}
          label={field.label}
          rules={rules}
          tooltip={field.tooltip}
        >
          <Select placeholder={field.placeholder} options={field.options} />
        </Form.Item>
      );

    case 'textarea':
      return (
        <Form.Item
          name={['config_json', field.name]}
          label={field.label}
          rules={rules}
          tooltip={field.tooltip}
        >
          <Input.TextArea rows={4} placeholder={field.placeholder} />
        </Form.Item>
      );

    default:
      return (
        <Form.Item
          name={['config_json', field.name]}
          label={field.label}
          rules={rules}
          tooltip={field.tooltip}
        >
          <Input placeholder={field.placeholder} />
        </Form.Item>
      );
  }
};

// ==========================================
// Main Component
// ==========================================

const ConnectorWizard: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = id && id !== 'new';

  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    latency_ms?: number;
  } | null>(null);
  const [selectedType, setSelectedType] = useState<ConnectorType | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Load existing connector for edit mode
  useEffect(() => {
    if (isEdit) {
      loadConnector();
    }
  }, [id]);

  const loadConnector = async () => {
    try {
      setLoading(true);
      const data = await fetchConnector(id!);
      setSelectedType(data.conn_type);
      form.setFieldsValue({
        name: data.name,
        conn_type: data.conn_type,
        config_json: data.config_json,
      });
      setCurrentStep(1); // Skip type selection in edit mode
    } catch (err: any) {
      message.error(err.response?.data?.detail || '加载连接器失败');
      navigate('/data/connectors');
    } finally {
      setLoading(false);
    }
  };

  // Handle type selection
  const handleTypeSelect = (type: ConnectorType) => {
    setSelectedType(type);
    setTestResult(null);
    
    // Set default values
    const defaults = buildDefaultConfig(type);
    form.setFieldsValue({
      conn_type: type,
      config_json: defaults,
    });
    
    setCurrentStep(1);
  };

  // Test connection
  const handleTest = async () => {
    try {
      await form.validateFields();
      setTesting(true);
      setTestResult(null);

      const values = form.getFieldsValue();
      const result = await testConnection({
        conn_type: values.conn_type,
        config_json: values.config_json,
      });

      setTestResult(result);
      
      if (result.success) {
        message.success(`连接测试成功 (${result.latency_ms}ms)`);
      } else {
        message.error(`连接测试失败: ${result.message}`);
      }
    } catch (err: any) {
      if (err.errorFields) {
        message.error('请填写所有必填项');
      } else {
        setTestResult({
          success: false,
          message: err.response?.data?.detail || '测试失败',
        });
      }
    } finally {
      setTesting(false);
    }
  };

  // Save connection
  const handleSave = async () => {
    try {
      await form.validateFields();
      setSaving(true);

      const values = form.getFieldsValue();
      const payload: IConnectionCreate = {
        name: values.name,
        conn_type: values.conn_type,
        config_json: values.config_json,
      };

      if (isEdit) {
        await updateConnector(id!, payload);
        message.success('更新成功');
      } else {
        await createConnector(payload);
        message.success('创建成功');
      }

      navigate('/data/connectors');
    } catch (err: any) {
      if (err.errorFields) {
        message.error('请填写所有必填项');
      } else {
        message.error(err.response?.data?.detail || '保存失败');
      }
    } finally {
      setSaving(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  const connectorDef = selectedType ? CONNECTOR_REGISTRY[selectedType] : null;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/data/connectors')}
          style={{ marginBottom: 16 }}
        >
          返回列表
        </Button>
        <Title level={4} style={{ margin: 0 }}>
          {isEdit ? '编辑连接器' : '新建连接器'}
        </Title>
      </div>

      {/* Steps */}
      <Steps
        current={currentStep}
        style={{ marginBottom: 32 }}
        items={[
          { title: '选择类型' },
          { title: '配置连接' },
          { title: '测试验证' },
        ]}
      />

      {/* Step 1: Type Selection */}
      {currentStep === 0 && !isEdit && (
        <Card>
          <Title level={5}>选择连接器类型</Title>
          <Paragraph type="secondary">
            选择要连接的数据源类型
          </Paragraph>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: 16,
              marginTop: 24,
            }}
          >
            {getConnectorTypes().map((type) => {
              const def = CONNECTOR_REGISTRY[type];
              const IconComponent = def.icon;
              return (
                <Card
                  key={type}
                  hoverable
                  onClick={() => handleTypeSelect(type)}
                  style={{
                    textAlign: 'center',
                    border: selectedType === type ? `2px solid ${def.color}` : undefined,
                  }}
                >
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      margin: '0 auto 12px',
                      borderRadius: 8,
                      background: `${def.color}15`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 24,
                      color: def.color,
                    }}
                  >
                    <IconComponent />
                  </div>
                  <Text strong>{def.label}</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {def.description.slice(0, 30)}...
                  </Text>
                </Card>
              );
            })}
          </div>
        </Card>
      )}

      {/* Step 2 & 3: Configuration & Test */}
      {currentStep >= 1 && selectedType && connectorDef && (
        <Card>
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              conn_type: selectedType,
              config_json: buildDefaultConfig(selectedType),
            }}
          >
            {/* Hidden type field */}
            <Form.Item name="conn_type" hidden>
              <Input />
            </Form.Item>

            {/* Connection name */}
            <Form.Item
              name="name"
              label="连接器名称"
              rules={[{ required: true, message: '请输入连接器名称' }]}
            >
              <Input placeholder="例如: 生产数据库" />
            </Form.Item>

            <Divider>
              <Space>
                {React.createElement(connectorDef.icon)}
                {connectorDef.label} 配置
              </Space>
            </Divider>

            {/* Dynamic fields from registry */}
            {connectorDef.fields.map((field) => (
              <DynamicField key={field.name} field={field} />
            ))}

            {/* Test Result */}
            {testResult && (
              <Alert
                type={testResult.success ? 'success' : 'error'}
                icon={testResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                message={testResult.success ? '连接测试成功' : '连接测试失败'}
                description={
                  testResult.success
                    ? `延迟: ${testResult.latency_ms}ms`
                    : testResult.message
                }
                showIcon
                style={{ marginBottom: 24 }}
              />
            )}

            {/* Actions */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: 16,
                borderTop: '1px solid #f0f0f0',
              }}
            >
              <Button
                onClick={() => {
                  if (!isEdit) {
                    setCurrentStep(0);
                    setSelectedType(null);
                    setTestResult(null);
                  }
                }}
                disabled={isEdit}
              >
                上一步
              </Button>

              <Space>
                <Button
                  onClick={handleTest}
                  loading={testing}
                  icon={testing ? <LoadingOutlined /> : undefined}
                >
                  测试连接
                </Button>
                <Button
                  type="primary"
                  onClick={handleSave}
                  loading={saving}
                  disabled={!testResult?.success && !isEdit}
                >
                  {isEdit ? '保存修改' : '创建连接器'}
                </Button>
              </Space>
            </div>
          </Form>
        </Card>
      )}
    </div>
  );
};

export default ConnectorWizard;
