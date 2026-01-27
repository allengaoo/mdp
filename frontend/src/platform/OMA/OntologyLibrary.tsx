import React, { useState, useEffect } from 'react';
import {
  Card,
  Tag,
  Space,
  Spin,
  message,
  Alert,
  Button,
  Modal,
  Form,
  Input,
  Dropdown,
  Typography,
} from 'antd';
import type { MenuProps } from 'antd';
import {
  CodeSandboxOutlined,
  LinkOutlined,
  ArrowRightOutlined,
  DatabaseOutlined,
  ReloadOutlined,
  PlusOutlined,
  EllipsisOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { fetchProjects, IOntologyProject } from '../../api/ontology';
import {
  createProject,
  updateProject,
  deleteProject,
} from '../../api/v3/ontology';

const { TextArea } = Input;
const { Text } = Typography;

// ==========================================
// Project Modal Component
// ==========================================
interface ProjectModalProps {
  open: boolean;
  mode: 'create' | 'edit';
  project: IOntologyProject | null;
  onClose: () => void;
  onSuccess: () => void;
}

const ProjectModal: React.FC<ProjectModalProps> = ({
  open,
  mode,
  project,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      if (mode === 'edit' && project) {
        form.setFieldsValue({
          name: project.title,
          description: project.description || '',
        });
      } else {
        form.resetFields();
      }
    }
  }, [open, mode, project, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      if (mode === 'create') {
        await createProject({
          name: values.name,
          description: values.description || null,
        });
        message.success('场景创建成功');
      } else if (mode === 'edit' && project) {
        await updateProject(project.id, {
          name: values.name,
          description: values.description || null,
        });
        message.success('场景更新成功');
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '操作失败';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={mode === 'create' ? '新建场景' : '编辑场景'}
      open={open}
      onCancel={onClose}
      onOk={handleSubmit}
      confirmLoading={loading}
      okText={mode === 'create' ? '创建' : '保存'}
      cancelText="取消"
      destroyOnClose
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="name"
          label="场景名称"
          rules={[
            { required: true, message: '请输入场景名称' },
            { max: 100, message: '名称不能超过100个字符' },
          ]}
        >
          <Input placeholder="输入场景名称，如：海上态势感知" />
        </Form.Item>

        <Form.Item
          name="description"
          label="描述"
          rules={[{ max: 500, message: '描述不能超过500个字符' }]}
        >
          <TextArea
            rows={4}
            placeholder="描述该场景的用途和范围..."
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

// ==========================================
// Main Component
// ==========================================
const OntologyLibrary = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<IOntologyProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [selectedProject, setSelectedProject] = useState<IOntologyProject | null>(null);

  // Fetch projects from API
  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProjects();
      setProjects(data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '加载项目列表失败，请检查网络连接';
      setError(errorMsg);
      message.error(errorMsg);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '未知';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const handleEnterWorkspace = (projectId: string) => {
    navigate(`/oma/project/${projectId}`);
  };

  // Create project
  const handleCreate = () => {
    setModalMode('create');
    setSelectedProject(null);
    setModalOpen(true);
  };

  // Edit project
  const handleEdit = (project: IOntologyProject) => {
    setModalMode('edit');
    setSelectedProject(project);
    setModalOpen(true);
  };

  // Delete project
  const handleDelete = (project: IOntologyProject) => {
    Modal.confirm({
      title: `删除场景 "${project.title}"？`,
      icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
      content: (
        <div style={{ marginTop: 12 }}>
          <Text type="secondary">
            此操作将删除场景配置。
          </Text>
          <div
            style={{
              marginTop: 12,
              padding: 12,
              background: '#fffbe6',
              border: '1px solid #ffe58f',
              borderRadius: 6,
            }}
          >
            <Text style={{ color: '#ad6800' }}>
              <strong>注意：</strong>链接到此场景的全局对象、链接和数据将<strong>不会</strong>被删除，
              它们仍保留在全域资产库中。
            </Text>
          </div>
          <div style={{ marginTop: 12 }}>
            <Text type="danger">此操作无法撤销。</Text>
          </div>
        </div>
      ),
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteProject(project.id);
          message.success('场景已删除');
          loadProjects();
        } catch (err: any) {
          const errorMsg = err.response?.data?.detail || '删除失败';
          message.error(errorMsg);
        }
      },
    });
  };

  // Card dropdown menu
  const getCardMenuItems = (project: IOntologyProject): MenuProps['items'] => [
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '编辑元数据',
      onClick: () => handleEdit(project),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除场景',
      danger: true,
      onClick: () => handleDelete(project),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px', color: '#8c8c8c' }}>加载项目列表...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
            本体库 (Ontology Library)
          </h1>
        </div>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={loadProjects}>
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
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
            本体库 (Ontology Library)
          </h1>
          <p style={{ color: '#666', marginTop: '8px', marginBottom: 0 }}>
            管理和浏览您的本体场景
          </p>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadProjects}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建场景
          </Button>
        </Space>
      </div>

      {projects.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: '#8c8c8c' }}>
          <DatabaseOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
          <div>暂无场景</div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            style={{ marginTop: 16 }}
            onClick={handleCreate}
          >
            创建第一个场景
          </Button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '24px',
          }}
        >
          {projects.map((project) => (
            <Card
              key={project.id}
              hoverable
              style={{
                borderRadius: '8px',
                border: '1px solid #e8e8e8',
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                transition: 'all 0.3s',
              }}
              styles={{
                body: {
                  padding: '20px',
                },
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
              }}
            >
              {/* Row 1: Header - Icon, Title, and Menu */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <DatabaseOutlined
                    style={{
                      fontSize: '32px',
                      color: '#1890ff',
                      marginRight: '12px',
                    }}
                  />
                  <h3
                    style={{
                      fontSize: '18px',
                      fontWeight: 'bold',
                      margin: 0,
                      flex: 1,
                    }}
                  >
                    {project.title}
                  </h3>
                </div>
                <Dropdown
                  menu={{ items: getCardMenuItems(project) }}
                  trigger={['click']}
                  placement="bottomRight"
                >
                  <Button
                    type="text"
                    icon={<EllipsisOutlined style={{ fontSize: 18 }} />}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Dropdown>
              </div>

              {/* Row 2: Description */}
              {project.description && (
                <p
                  style={{
                    color: '#666',
                    margin: '12px 0',
                    fontSize: '14px',
                    lineHeight: '1.6',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {project.description}
                </p>
              )}

              {/* Row 3: Tags */}
              {project.tags && project.tags.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <Space size={[8, 8]} wrap>
                    {project.tags.map((tag) => (
                      <Tag key={tag} color="blue">
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}

              {/* Row 4: Stats */}
              <div
                style={{
                  background: '#fafafa',
                  border: '1px solid #e8e8e8',
                  borderRadius: '6px',
                  padding: '12px',
                  marginBottom: '16px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-around',
                    gap: '16px',
                  }}
                >
                  {/* Object Type Count */}
                  <div
                    style={{
                      flex: 1,
                      textAlign: 'center',
                      padding: '8px',
                      background: '#fff',
                      borderRadius: '4px',
                      border: '1px solid #e8e8e8',
                    }}
                  >
                    <CodeSandboxOutlined
                      style={{ fontSize: '20px', color: '#1890ff', marginBottom: '4px' }}
                    />
                    <div
                      style={{
                        fontSize: '20px',
                        fontWeight: 'bold',
                        color: '#262626',
                        marginTop: '4px',
                      }}
                    >
                      {project.objectCount}
                    </div>
                    <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '2px' }}>
                      对象类型
                    </div>
                  </div>

                  {/* Link Type Count */}
                  <div
                    style={{
                      flex: 1,
                      textAlign: 'center',
                      padding: '8px',
                      background: '#fff',
                      borderRadius: '4px',
                      border: '1px solid #e8e8e8',
                    }}
                  >
                    <LinkOutlined
                      style={{ fontSize: '20px', color: '#52c41a', marginBottom: '4px' }}
                    />
                    <div
                      style={{
                        fontSize: '20px',
                        fontWeight: 'bold',
                        color: '#262626',
                        marginTop: '4px',
                      }}
                    >
                      {project.linkCount}
                    </div>
                    <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '2px' }}>
                      链接类型
                    </div>
                  </div>
                </div>
              </div>

              {/* Row 5: Footer */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginTop: '16px',
                  paddingTop: '16px',
                  borderTop: '1px dashed #e8e8e8',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: '#52c41a',
                      display: 'inline-block',
                    }}
                  />
                  <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    更新于 {formatDate(project.updatedAt)}
                  </span>
                </div>
                <a
                  onClick={(e) => {
                    e.preventDefault();
                    handleEnterWorkspace(project.id);
                  }}
                  style={{
                    color: '#1890ff',
                    fontSize: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  进入工作区
                  <ArrowRightOutlined />
                </a>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Project Modal */}
      <ProjectModal
        open={modalOpen}
        mode={modalMode}
        project={selectedProject}
        onClose={() => setModalOpen(false)}
        onSuccess={loadProjects}
      />
    </div>
  );
};

export default OntologyLibrary;
