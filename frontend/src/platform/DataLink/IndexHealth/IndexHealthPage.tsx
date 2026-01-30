/**
 * IndexHealthPage - Main page for Index Health monitoring
 */
import React, { useEffect, useState, useCallback } from 'react';
import { Card, Button, Space, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import KPICards from './KPICards';
import ObjectHealthTable from './ObjectHealthTable';
import HealthDetailDrawer from './HealthDetailDrawer';
import {
  fetchHealthSummary,
  triggerReindex,
  ISystemHealthSummary,
  IObjectHealthSummary,
} from '../../../api/v3/health';

const IndexHealthPage: React.FC = () => {
  const [summary, setSummary] = useState<ISystemHealthSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [reindexing, setReindexing] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedObject, setSelectedObject] = useState<IObjectHealthSummary | null>(null);

  // Load health summary
  const loadSummary = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchHealthSummary();
      setSummary(data);
    } catch (error: any) {
      console.error('Failed to load health summary:', error);
      message.error('加载健康数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  // Handle view detail
  const handleViewDetail = (record: IObjectHealthSummary) => {
    setSelectedObject(record);
    setDrawerOpen(true);
  };

  // Handle reindex
  const handleReindex = async (objectDefId: string) => {
    setReindexing(objectDefId);
    try {
      await triggerReindex(objectDefId);
      message.success('重新索引任务已触发');
      // Reload after a delay
      setTimeout(loadSummary, 2000);
    } catch (error: any) {
      message.error(`重新索引失败: ${error.message}`);
    } finally {
      setReindexing(null);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <div
        style={{
          marginBottom: 24,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h2 style={{ margin: 0 }}>索引健康监控</h2>
          <p style={{ margin: '8px 0 0', color: '#8c8c8c' }}>
            监控数据索引管道的健康状态和性能指标
          </p>
        </div>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadSummary}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* KPI Cards */}
      <div style={{ marginBottom: 24 }}>
        <KPICards data={summary} loading={loading} />
      </div>

      {/* Object Health Table */}
      <Card title="对象健康状态" bordered={false}>
        <ObjectHealthTable
          data={summary?.objects || []}
          loading={loading}
          onViewDetail={handleViewDetail}
          onReindex={handleReindex}
          reindexing={reindexing}
        />
      </Card>

      {/* Detail Drawer */}
      <HealthDetailDrawer
        open={drawerOpen}
        object={selectedObject}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
};

export default IndexHealthPage;
