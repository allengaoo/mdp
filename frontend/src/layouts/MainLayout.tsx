import { Layout, Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';
import {
  DatabaseOutlined,
  FolderOutlined,
  RocketOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';

const { Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuProps['items'] = [
    {
      key: 'ontology',
      icon: <DatabaseOutlined />,
      label: '本体管理 (Ontology Management)',
      children: [
        {
          key: '/oma/library',
          icon: <FolderOutlined />,
          label: '本体库 (Library)',
        },
        {
          key: 'example-apps',
          icon: <AppstoreOutlined />,
          label: '示例应用 (Apps)',
          children: [
            {
              key: '/apps/battlefield',
              icon: <RocketOutlined />,
              label: '战场态势 (Battlefield)',
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
    if (location.pathname.startsWith('/oma/library')) {
      return ['/oma/library'];
    }
    if (location.pathname.startsWith('/apps/battlefield')) {
      return ['/apps/battlefield'];
    }
    return [];
  };

  const getOpenKeys = () => {
    const keys: string[] = [];
    if (location.pathname.startsWith('/oma') || location.pathname.startsWith('/apps')) {
      keys.push('ontology');
    }
    if (location.pathname.startsWith('/apps')) {
      keys.push('example-apps');
    }
    return keys;
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

