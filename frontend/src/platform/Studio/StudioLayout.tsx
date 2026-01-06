/**
 * Studio Layout component for Ontology Project Studio.
 * Renders inside MainLayout's Content area with its own sidebar.
 */
import React from 'react';
import { Layout, Menu, Breadcrumb } from 'antd';
import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';
import type { MenuProps } from 'antd';
import {
  ApartmentOutlined,
  NodeIndexOutlined,
  LinkOutlined,
  PropertySafetyOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  FunctionOutlined,
  FileTextOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';

const { Sider, Content } = Layout;

// Mock project data
const MOCK_PROJECTS: Record<string, { name: string; description: string }> = {
  '00000000-0000-0000-0000-000000000001': {
    name: 'Battlefield System',
    description: 'Military operations simulation',
  },
};

const StudioLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams<{ projectId: string }>();
  
  const project = projectId ? MOCK_PROJECTS[projectId] : null;
  const projectName = project?.name || 'Unknown Project';

  const menuItems: MenuProps['items'] = [
    {
      key: 'entities',
      label: '实体与关系 (Entities & Relations)',
      type: 'group',
      children: [
        {
          key: `/oma/project/${projectId}/topology`,
          icon: <ApartmentOutlined />,
          label: '拓扑总览 (Topology)',
        },
        {
          key: `/oma/project/${projectId}/object-types`,
          icon: <NodeIndexOutlined />,
          label: '对象类型 (Object Types)',
        },
        {
          key: `/oma/project/${projectId}/link-types`,
          icon: <LinkOutlined />,
          label: '链接类型 (Link Types)',
        },
        {
          key: `/oma/project/${projectId}/shared-properties`,
          icon: <PropertySafetyOutlined />,
          label: '公共属性 (Shared Properties)',
        },
        {
          key: `/oma/project/${projectId}/physical-properties`,
          icon: <DatabaseOutlined />,
          label: '物理属性 (Physical Properties)',
        },
      ],
    },
    {
      key: 'logic',
      label: '逻辑与行为 (Logic & Actions)',
      type: 'group',
      children: [
        {
          key: `/oma/project/${projectId}/actions`,
          icon: <ThunderboltOutlined />,
          label: '行为定义 (Action Definitions)',
        },
        {
          key: `/oma/project/${projectId}/functions`,
          icon: <FunctionOutlined />,
          label: '函数 (Functions)',
        },
      ],
    },
    {
      key: 'runtime',
      label: '运行与调试 (Run & Debug)',
      type: 'group',
      children: [
        {
          key: `/oma/project/${projectId}/logs`,
          icon: <FileTextOutlined />,
          label: '运行日志 (Execution Logs)',
        },
        {
          key: `/oma/project/${projectId}/test`,
          icon: <ExperimentOutlined />,
          label: '本体测试 (Ontology Test)',
        },
      ],
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  // Get selected key based on current location
  const getSelectedKeys = () => {
    const path = location.pathname;
    if (path.includes('/topology')) {
      return [`/oma/project/${projectId}/topology`];
    }
    if (path.includes('/object-types')) {
      return [`/oma/project/${projectId}/object-types`];
    }
    if (path.includes('/link-types')) {
      return [`/oma/project/${projectId}/link-types`];
    }
    if (path.includes('/shared-properties')) {
      return [`/oma/project/${projectId}/shared-properties`];
    }
    if (path.includes('/physical-properties')) {
      return [`/oma/project/${projectId}/physical-properties`];
    }
    if (path.includes('/actions')) {
      return [`/oma/project/${projectId}/actions`];
    }
    if (path.includes('/functions')) {
      return [`/oma/project/${projectId}/functions`];
    }
    if (path.includes('/logs')) {
      return [`/oma/project/${projectId}/logs`];
    }
    if (path.includes('/test')) {
      return [`/oma/project/${projectId}/test`];
    }
    return [`/oma/project/${projectId}/topology`]; // Default
  };

  const breadcrumbItems: Array<{ title: string; path?: string | null }> = [
    { 
      title: '本体管理 (Ontology Management)',
      path: '/oma/library',
    },
    { 
      title: projectName,
      path: `/oma/project/${projectId}/topology`,
    },
    { 
      title: getCurrentPageTitle(),
      path: null, // Current page, no navigation
    },
  ];

  function getCurrentPageTitle(): string {
    const path = location.pathname;
    if (path.includes('/topology')) return '拓扑总览';
    if (path.includes('/object-types')) return '对象类型';
    if (path.includes('/link-types')) return '链接类型';
    if (path.includes('/shared-properties')) return '公共属性';
    if (path.includes('/physical-properties')) return '物理属性';
    if (path.includes('/actions')) return '行为定义';
    if (path.includes('/functions')) return '函数';
    if (path.includes('/logs')) return '运行日志';
    if (path.includes('/test')) return '本体测试';
    return '拓扑总览';
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#f5f5f5' }}>
      {/* Breadcrumb Header */}
      <div
        style={{
          height: 48,
          background: '#fff',
          padding: '0 24px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          flexShrink: 0,
        }}
      >
        <Breadcrumb 
          items={breadcrumbItems}
          itemRender={(item, params, items) => {
            const isLast = params.index === items.length - 1;
            const hasPath = item.path && !isLast;
            
            if (!hasPath) {
              return <span>{item.title}</span>;
            }
            
            return (
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  navigate(item.path!);
                }}
                style={{ 
                  color: 'inherit',
                  textDecoration: 'none',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.textDecoration = 'underline';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.textDecoration = 'none';
                }}
              >
                {item.title}
              </a>
            );
          }}
        />
      </div>
      
      {/* Main Content Area with Sidebar */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Studio Sidebar */}
        <Sider
          width={250}
          style={{
            background: '#fff',
            borderRight: '1px solid #f0f0f0',
            height: '100%',
            overflow: 'auto',
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={getSelectedKeys()}
            items={menuItems}
            onClick={handleMenuClick}
            style={{
              borderRight: 'none',
              height: '100%',
            }}
            theme="light"
          />
        </Sider>
        
        {/* Content Area */}
        <Content
          style={{
            flex: 1,
            padding: '24px',
            background: '#f5f5f5',
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </div>
    </div>
  );
};

export default StudioLayout;

