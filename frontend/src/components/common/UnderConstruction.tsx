import React from 'react';
import { Empty, Typography } from 'antd';
import { ToolOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface UnderConstructionProps {
  title: string;
}

/**
 * 占位组件 - 用于尚未实现的页面
 */
const UnderConstruction: React.FC<UnderConstructionProps> = ({ title }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        padding: '48px',
      }}
    >
      <Empty
        image={<ToolOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
        imageStyle={{ height: 80 }}
        description={
          <div style={{ marginTop: 16 }}>
            <Title level={4} style={{ marginBottom: 8 }}>
              {title}
            </Title>
            <Text type="secondary">页面正在建设中，敬请期待...</Text>
          </div>
        }
      />
    </div>
  );
};

export default UnderConstruction;
