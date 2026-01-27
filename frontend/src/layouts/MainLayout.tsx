import { Layout, Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';
import {  DatabaseOutlined,  FolderOutlined,  PropertySafetyOutlined,  ApiOutlined,  NodeIndexOutlined,  ApartmentOutlined,  ThunderboltOutlined,  LinkOutlined,  CloudSyncOutlined,  DashboardOutlined,  SearchOutlined,  ShareAltOutlined,  UserOutlined,  RobotOutlined,} from '@ant-design/icons';
const { Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuProps['items'] = [
    // ==========================================
    // Group 1: 构建与定义
    // ==========================================
    {
      key: 'group-build',
      label: '构建与定义',
      type: 'group',
      children: [
        // SubMenu: 本体管理
        {
          key: 'ontology',
          icon: <DatabaseOutlined />,
          label: '本体管理',
          children: [
            {
              key: '/oma/library',
              icon: <FolderOutlined />,
              label: '本体场景库',
            },
            {
              key: '/oma/objects',
              icon: <NodeIndexOutlined />,
              label: '对象中心',
            },
            {
              key: '/oma/shared-properties',
              icon: <PropertySafetyOutlined />,
              label: '公共属性',
            },
            {
              key: '/oma/relations',
              icon: <ApartmentOutlined />,
              label: '关系图谱',
            },
            {
              key: '/oma/actions',
              icon: <ThunderboltOutlined />,
              label: '行为与逻辑',
            },
          ],
        },
        // SubMenu: 数据链接
        {
          key: 'data-link',
          icon: <LinkOutlined />,
          label: '数据链接',
          children: [
            {
              key: '/data/connectors',
              icon: <ApiOutlined />,
              label: '连接器管理',
            },
            {
              key: '/data/mapping',
              icon: <CloudSyncOutlined />,
              label: '多模态映射',
            },
            {
              key: '/data/health',
              icon: <DashboardOutlined />,
              label: '索引健康度',
            },
          ],
        },
      ],
    },
    // ==========================================
    // Group 2: 探索与分析
    // ==========================================
    {
      key: 'group-explore',
      label: '探索与分析',
      type: 'group',
      children: [
        // SubMenu: 洞察与分析
        {
          key: 'insight',
          icon: <SearchOutlined />,
          label: '洞察与分析',
          children: [
            {
              key: '/explore/search',
              icon: <SearchOutlined />,
              label: '全域检索',
            },
            {
              key: '/explore/graph',
              icon: <ShareAltOutlined />,
              label: '图谱分析',
            },
            {
              key: '/explore/object360',
              icon: <UserOutlined />,
              label: '对象360视图',
            },
            {
              key: '/explore/chat',
              icon: <RobotOutlined />,
              label: 'Chat2App',
            },
          ],
        },
      ],
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  // Get selected keys based on current location
  const getSelectedKeys = () => {
    // 直接使用当前路径作为选中 key
    return [location.pathname];
  };

  const getOpenKeys = () => {
    // 默认展开所有子菜单
    return ['ontology', 'data-link', 'insight'];
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={250}
        style={{
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
        }}
      >
        <div
          style={{
            height: 64,
            padding: '16px',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            fontSize: '18px',
            fontWeight: 'bold',
          }}
        >
          MDP Platform
        </div>
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            borderRight: 'none',
            height: 'calc(100vh - 64px)',
          }}
        />
      </Sider>
      <Layout>
        <Content
          style={{
            margin: '24px',
            padding: '24px',
            background: '#f5f5f5',
            minHeight: 'calc(100vh - 48px)',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

