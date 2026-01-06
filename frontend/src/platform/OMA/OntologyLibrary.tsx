import React, { useState, useEffect } from 'react';
import { Card, Tag, Space, Spin, message } from 'antd';
import {
  CodeSandboxOutlined,
  LinkOutlined,
  ArrowRightOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { fetchProjects, IOntologyProject } from '../../api/ontology';

const OntologyLibrary = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<IOntologyProject[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch projects from API
  useEffect(() => {
    const loadProjects = async () => {
      try {
        setLoading(true);
        const data = await fetchProjects();
        setProjects(data);
      } catch (error: any) {
        message.error(error.response?.data?.detail || 'Failed to fetch projects');
        // Fallback to empty array on error
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

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
    // Navigate to project workspace
    // For now, just navigate to a placeholder route
    navigate(`/oma/project/${projectId}`);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px', color: '#8c8c8c' }}>加载项目列表...</div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          本体库 (Ontology Library)
        </h1>
        <p style={{ color: '#666', marginTop: '8px', marginBottom: 0 }}>
          管理和浏览您的本体项目
        </p>
      </div>

      {projects.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: '#8c8c8c' }}>
          <DatabaseOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
          <div>暂无项目</div>
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
            {/* Row 1: Header - Icon and Title */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '12px',
              }}
            >
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
    </div>
  );
};

export default OntologyLibrary;

