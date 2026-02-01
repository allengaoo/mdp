/**
 * Actions & Logic Page - MDP Platform V3.1
 * 
 * Displays Actions and Functions in a tabbed interface.
 * - Actions Tab: Shows action definitions with their bound functions + Execute button
 * - Functions Tab: Shows function definitions with code preview drawer
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography,
  Tabs,
  Table,
  Button,
  Space,
  Tag,
  Drawer,
  Spin,
  Alert,
  Input,
  message,
  Modal,
  Form,
  InputNumber,
  Switch,
  Result,
} from 'antd';
import {
  ReloadOutlined,
  PlusOutlined,
  SearchOutlined,
  ThunderboltOutlined,
  CodeOutlined,
  FunctionOutlined,
  LinkOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  fetchActionsWithFunctions,
  fetchFunctionsForList,
  fetchActionDetails,
  executeAction,
  getActionDefinition,
  IActionWithFunction,
  IFunctionDef,
  IActionDetails,
  IParamSchema,
  IActionExecuteResponse,
  IActionDefinitionRead,
} from '../../api/v3/logic';
import ActionWizard from '../Studio/ActionWizard';
import ActionEditor from '../Studio/ActionEditor';
import FunctionWizard from '../Studio/FunctionWizard';

const { Title, Text, Paragraph } = Typography;

// ==========================================
// Output Type Colors
// ==========================================
const outputTypeColors: Record<string, string> = {
  VOID: 'default',
  STRING: 'blue',
  NUMBER: 'green',
  BOOLEAN: 'orange',
  OBJECT: 'purple',
  ARRAY: 'cyan',
};

// ==========================================
// Execute Modal Component
// ==========================================
interface ExecuteModalProps {
  visible: boolean;
  action: IActionWithFunction | null;
  onClose: () => void;
  onExecuted: () => void;
}

const ExecuteModal: React.FC<ExecuteModalProps> = ({ visible, action, onClose, onExecuted }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [actionDetails, setActionDetails] = useState<IActionDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [result, setResult] = useState<IActionExecuteResponse | null>(null);

  // Load action details when modal opens
  useEffect(() => {
    if (visible && action) {
      setResult(null);
      form.resetFields();
      loadActionDetails();
    }
  }, [visible, action]);

  const loadActionDetails = async () => {
    if (!action) return;
    setDetailsLoading(true);
    try {
      const details = await fetchActionDetails(action.id);
      setActionDetails(details);
      
      // Set default values
      if (details.input_params_schema) {
        const defaults: Record<string, any> = {};
        details.input_params_schema.forEach((param) => {
          if (param.default !== undefined) {
            defaults[param.name] = param.default;
          }
        });
        form.setFieldsValue(defaults);
      }
    } catch (err) {
      console.error('Failed to load action details:', err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleExecute = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      setResult(null);
      
      const response = await executeAction(action!.id, {
        params: values,
        project_id: 'default-project',
      });
      
      setResult(response);
      
      if (response.success) {
        message.success(`执行成功 (${response.execution_time_ms}ms)`);
      } else {
        message.error(`执行失败: ${response.error_message}`);
      }
      
      onExecuted();
    } catch (err: any) {
      message.error(`执行出错: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderFormField = (param: IParamSchema) => {
    const label = (
      <span>
        {param.name}
        {param.description && (
          <span style={{ fontWeight: 400, color: '#8c8c8c', marginLeft: 8 }}>
            ({param.description})
          </span>
        )}
      </span>
    );

    switch (param.type) {
      case 'number':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            rules={[{ required: param.required, message: `请输入 ${param.name}` }]}
          >
            <InputNumber style={{ width: '100%' }} placeholder={`输入 ${param.name}`} />
          </Form.Item>
        );
      case 'boolean':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        );
      default:
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            rules={[{ required: param.required, message: `请输入 ${param.name}` }]}
          >
            <Input placeholder={`输入 ${param.name}`} />
          </Form.Item>
        );
    }
  };

  return (
    <Modal
      title={
        <div>
          <PlayCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          执行 Action: {action?.display_name}
        </div>
      }
      open={visible}
      onCancel={onClose}
      width={600}
      footer={
        result ? (
          <Button onClick={onClose}>关闭</Button>
        ) : (
          <Space>
            <Button onClick={onClose}>取消</Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleExecute}
              loading={loading}
            >
              执行
            </Button>
          </Space>
        )
      }
    >
      {detailsLoading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin tip="加载参数配置..." />
        </div>
      ) : result ? (
        <div>
          <Result
            status={result.success ? 'success' : 'error'}
            title={result.success ? '执行成功' : '执行失败'}
            subTitle={`耗时: ${result.execution_time_ms}ms | 日志ID: ${result.log_id.substring(0, 8)}...`}
          />
          
          {result.error_message && (
            <Alert
              type="error"
              message="错误信息"
              description={result.error_message}
              style={{ marginBottom: 16 }}
            />
          )}
          
          {result.stdout && (
            <div style={{ marginBottom: 16 }}>
              <Text strong>控制台输出:</Text>
              <pre
                style={{
                  marginTop: 8,
                  padding: 12,
                  background: '#1e1e1e',
                  color: '#d4d4d4',
                  borderRadius: 6,
                  maxHeight: 150,
                  overflow: 'auto',
                  fontSize: 12,
                }}
              >
                {result.stdout}
              </pre>
            </div>
          )}
          
          {result.success && result.result && (
            <div>
              <Text strong>返回结果:</Text>
              <pre
                style={{
                  marginTop: 8,
                  padding: 12,
                  background: '#f6f8fa',
                  borderRadius: 6,
                  maxHeight: 200,
                  overflow: 'auto',
                  fontSize: 12,
                }}
              >
                {JSON.stringify(result.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      ) : (
        <Form form={form} layout="vertical">
          {actionDetails?.input_params_schema && actionDetails.input_params_schema.length > 0 ? (
            actionDetails.input_params_schema.map(renderFormField)
          ) : (
            <Alert
              type="info"
              message="此 Action 无需输入参数"
              style={{ marginBottom: 16 }}
            />
          )}
        </Form>
      )}
    </Modal>
  );
};

// ==========================================
// Actions Tab Component
// ==========================================
interface ActionsTabProps {
  actions: IActionWithFunction[];
  loading: boolean;
  searchText: string;
  onExecute: (action: IActionWithFunction) => void;
  onEdit: (action: IActionWithFunction) => void;
}

const ActionsTab: React.FC<ActionsTabProps> = ({ actions, loading, searchText, onExecute, onEdit }) => {
  const filteredActions = actions.filter(
    (action) =>
      action.api_name.toLowerCase().includes(searchText.toLowerCase()) ||
      action.display_name.toLowerCase().includes(searchText.toLowerCase()) ||
      (action.function_api_name || '').toLowerCase().includes(searchText.toLowerCase())
  );

  const columns: ColumnsType<IActionWithFunction> = [
    {
      title: 'Action 名称',
      key: 'name',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 600, color: '#262626' }}>
            {record.display_name}
          </div>
          <div style={{ fontSize: 12, color: '#8c8c8c', fontFamily: 'monospace' }}>
            {record.api_name}
          </div>
        </div>
      ),
    },
    {
      title: '绑定函数',
      key: 'function',
      render: (_, record) => (
        record.function_api_name ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <LinkOutlined style={{ color: '#1890ff' }} />
            <span
              style={{
                fontFamily: 'monospace',
                fontSize: 13,
                color: '#1890ff',
                cursor: 'pointer',
              }}
            >
              {record.function_api_name}
            </span>
          </div>
        ) : (
          <Text type="secondary">未绑定</Text>
        )
      ),
    },
    {
      title: '函数显示名',
      dataIndex: 'function_display_name',
      key: 'function_display_name',
      render: (value) => value || <Text type="secondary">-</Text>,
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => onExecute(record)}
            disabled={!record.backing_function_id}
          >
            执行
          </Button>
          <Button type="link" size="small" onClick={() => onEdit(record)}>
            编辑
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      dataSource={filteredActions}
      columns={columns}
      rowKey="id"
      loading={loading}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showTotal: (total) => `共 ${total} 条`,
      }}
      locale={{ emptyText: '暂无 Action 数据' }}
    />
  );
};

// ==========================================
// Functions Tab Component
// ==========================================
interface FunctionsTabProps {
  functions: IFunctionDef[];
  loading: boolean;
  searchText: string;
  onSelectFunction: (func: IFunctionDef) => void;
}

const FunctionsTab: React.FC<FunctionsTabProps> = ({
  functions,
  loading,
  searchText,
  onSelectFunction,
}) => {
  const filteredFunctions = functions.filter(
    (func) =>
      func.api_name.toLowerCase().includes(searchText.toLowerCase()) ||
      func.display_name.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns: ColumnsType<IFunctionDef> = [
    {
      title: 'Function 名称',
      key: 'name',
      render: (_, record) => (
        <div
          style={{ cursor: 'pointer' }}
          onClick={() => onSelectFunction(record)}
        >
          <div
            style={{
              fontWeight: 600,
              fontFamily: 'monospace',
              fontSize: 13,
              color: '#262626',
            }}
          >
            {record.api_name}
          </div>
          <div style={{ fontSize: 12, color: '#8c8c8c' }}>
            {record.display_name}
          </div>
        </div>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (value) => value || <Text type="secondary">-</Text>,
    },
    {
      title: '输出类型',
      dataIndex: 'output_type',
      key: 'output_type',
      width: 120,
      render: (value) => (
        <Tag color={outputTypeColors[value] || 'default'}>{value}</Tag>
      ),
    },
    {
      title: '代码',
      key: 'code',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<CodeOutlined />}
          onClick={() => onSelectFunction(record)}
        >
          预览
        </Button>
      ),
    },
  ];

  return (
    <Table
      dataSource={filteredFunctions}
      columns={columns}
      rowKey="id"
      loading={loading}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showTotal: (total) => `共 ${total} 条`,
      }}
      onRow={(record) => ({
        onClick: () => onSelectFunction(record),
        style: { cursor: 'pointer' },
      })}
      locale={{ emptyText: '暂无 Function 数据' }}
    />
  );
};

// ==========================================
// Code Preview Drawer Component
// ==========================================
interface CodeDrawerProps {
  visible: boolean;
  onClose: () => void;
  func: IFunctionDef | null;
}

const CodeDrawer: React.FC<CodeDrawerProps> = ({ visible, onClose, func }) => {
  if (!func) return null;

  const codeContent = func.code_content || '// 暂无代码内容';

  return (
    <Drawer
      title={
        <div>
          <div style={{ fontWeight: 600 }}>{func.display_name}</div>
          <div style={{ fontSize: 12, color: '#8c8c8c', fontFamily: 'monospace' }}>
            {func.api_name}
          </div>
        </div>
      }
      placement="right"
      width={600}
      open={visible}
      onClose={onClose}
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">描述：</Text>
        <Paragraph>{func.description || '暂无描述'}</Paragraph>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">输出类型：</Text>
        <Tag color={outputTypeColors[func.output_type] || 'default'} style={{ marginLeft: 8 }}>
          {func.output_type}
        </Tag>
      </div>

      <div>
        <Text type="secondary">代码内容：</Text>
        <pre
          style={{
            marginTop: 8,
            padding: 16,
            background: '#282c34',
            color: '#abb2bf',
            borderRadius: 8,
            overflow: 'auto',
            maxHeight: 400,
            fontSize: 13,
            fontFamily: "'Fira Code', 'Consolas', monospace",
            lineHeight: 1.6,
          }}
        >
          {codeContent}
        </pre>
      </div>
    </Drawer>
  );
};

// ==========================================
// Main Component
// ==========================================
const ActionLogic: React.FC = () => {
  const [activeTab, setActiveTab] = useState('actions');
  const [actions, setActions] = useState<IActionWithFunction[]>([]);
  const [functions, setFunctions] = useState<IFunctionDef[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState<IFunctionDef | null>(null);
  
  // Execute Modal state
  const [executeModalVisible, setExecuteModalVisible] = useState(false);
  const [selectedAction, setSelectedAction] = useState<IActionWithFunction | null>(null);
  
  // Create Action Wizard state
  const [actionWizardVisible, setActionWizardVisible] = useState(false);
  // Create Function Wizard state (OMA global - no project)
  const [functionWizardVisible, setFunctionWizardVisible] = useState(false);
  
  // Edit Action state
  const [editorVisible, setEditorVisible] = useState(false);
  const [selectedActionForEdit, setSelectedActionForEdit] = useState<IActionDefinitionRead | null>(null);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [actionsData, functionsData] = await Promise.all([
        fetchActionsWithFunctions(),
        fetchFunctionsForList(),
      ]);
      setActions(actionsData);
      setFunctions(functionsData);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '加载数据失败';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle function selection for drawer
  const handleSelectFunction = (func: IFunctionDef) => {
    setSelectedFunction(func);
    setDrawerVisible(true);
  };

  // Handle action execution
  const handleExecuteAction = (action: IActionWithFunction) => {
    setSelectedAction(action);
    setExecuteModalVisible(true);
  };

  // Handle edit action
  const handleEditAction = async (action: IActionWithFunction) => {
    try {
      // 获取完整的 action 数据
      const fullAction = await getActionDefinition(action.id);
      setSelectedActionForEdit(fullAction);
      setEditorVisible(true);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '获取 Action 详情失败');
    }
  };

  // Handle edit success
  const handleEditSuccess = () => {
    setEditorVisible(false);
    setSelectedActionForEdit(null);
    loadData(); // 刷新列表
  };

  // Tab items
  const tabItems = [
    {
      key: 'actions',
      label: (
        <span>
          <ThunderboltOutlined />
          Actions ({actions.length})
        </span>
      ),
      children: (
        <ActionsTab
          actions={actions}
          loading={loading}
          searchText={searchText}
          onExecute={handleExecuteAction}
          onEdit={handleEditAction}
        />
      ),
    },
    {
      key: 'functions',
      label: (
        <span>
          <FunctionOutlined />
          Functions ({functions.length})
        </span>
      ),
      children: (
        <FunctionsTab
          functions={functions}
          loading={loading}
          searchText={searchText}
          onSelectFunction={handleSelectFunction}
        />
      ),
    },
  ];

  // Error state
  if (error && actions.length === 0 && functions.length === 0) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ margin: 0 }}>
            行为与逻辑 (Actions & Logic)
          </Title>
        </div>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadData}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 24,
        }}
      >
        <div>
          <Title level={4} style={{ margin: 0 }}>
            行为与逻辑 (Actions & Logic)
          </Title>
          <Text type="secondary">
            管理业务动作 (Actions) 和底层逻辑函数 (Functions)
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
            刷新
          </Button>
          {activeTab === 'actions' && (
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setActionWizardVisible(true)}
            >
              新建 Action
            </Button>
          )}
          {activeTab === 'functions' && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setFunctionWizardVisible(true)}
            >
              新建 Function
            </Button>
          )}
        </Space>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索名称..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
      </div>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      {/* Code Preview Drawer */}
      <CodeDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        func={selectedFunction}
      />

      {/* Execute Action Modal */}
      <ExecuteModal
        visible={executeModalVisible}
        action={selectedAction}
        onClose={() => setExecuteModalVisible(false)}
        onExecuted={loadData}
      />

      {/* Create Action Wizard */}
      <ActionWizard
        visible={actionWizardVisible}
        onCancel={() => setActionWizardVisible(false)}
        onSuccess={() => {
          setActionWizardVisible(false);
          loadData();
        }}
      />

      {/* Create Function Wizard (OMA global - projectId undefined) */}
      <FunctionWizard
        visible={functionWizardVisible}
        projectId={undefined}
        onCancel={() => setFunctionWizardVisible(false)}
        onSuccess={() => {
          setFunctionWizardVisible(false);
          loadData();
        }}
      />

      {/* Edit Action Modal */}
      {selectedActionForEdit && (
        <ActionEditor
          visible={editorVisible}
          action={selectedActionForEdit}
          onCancel={() => {
            setEditorVisible(false);
            setSelectedActionForEdit(null);
          }}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
};

export default ActionLogic;
