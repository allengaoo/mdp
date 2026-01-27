/**
 * KPICards - Top dashboard KPI statistics cards
 */
import React from 'react';
import { Row, Col, Card, Statistic, Progress } from 'antd';
import {
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  FileExclamationOutlined,
} from '@ant-design/icons';
import type { ISystemHealthSummary } from '../../../api/v3/health';

interface KPICardsProps {
  data: ISystemHealthSummary | null;
  loading: boolean;
}

const KPICards: React.FC<KPICardsProps> = ({ data, loading }) => {
  // Calculate overall health percentage
  const healthPercentage = data
    ? Math.round((data.healthy_count / Math.max(data.total_objects, 1)) * 100)
    : 0;

  // Determine health status color
  const getHealthColor = () => {
    if (healthPercentage >= 90) return '#52c41a';
    if (healthPercentage >= 70) return '#faad14';
    return '#ff4d4f';
  };

  return (
    <Row gutter={[16, 16]}>
      {/* System Health */}
      <Col xs={24} sm={12} lg={6}>
        <Card loading={loading}>
          <Statistic
            title="系统健康度"
            value={healthPercentage}
            suffix="%"
            valueStyle={{ color: getHealthColor() }}
            prefix={
              healthPercentage >= 90 ? (
                <CheckCircleOutlined />
              ) : healthPercentage >= 70 ? (
                <WarningOutlined />
              ) : (
                <CloseCircleOutlined />
              )
            }
          />
          <Progress
            percent={healthPercentage}
            showInfo={false}
            strokeColor={getHealthColor()}
            size="small"
            style={{ marginTop: 8 }}
          />
          <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
            {data?.healthy_count || 0} 健康 / {data?.degraded_count || 0} 降级 / {data?.failed_count || 0} 失败
          </div>
        </Card>
      </Col>

      {/* Success Rate */}
      <Col xs={24} sm={12} lg={6}>
        <Card loading={loading}>
          <Statistic
            title="索引成功率"
            value={data?.overall_success_rate || 0}
            precision={2}
            suffix="%"
            valueStyle={{
              color: (data?.overall_success_rate || 0) >= 95 ? '#52c41a' : '#faad14',
            }}
          />
          <div style={{ marginTop: 16, fontSize: 12, color: '#8c8c8c' }}>
            基于最近一次作业运行
          </div>
        </Card>
      </Col>

      {/* AI Latency */}
      <Col xs={24} sm={12} lg={6}>
        <Card loading={loading}>
          <Statistic
            title="AI 推理延迟"
            value={data?.avg_ai_latency_ms || 0}
            suffix="ms"
            prefix={<ThunderboltOutlined />}
            valueStyle={{
              color: (data?.avg_ai_latency_ms || 0) < 500 ? '#52c41a' : '#faad14',
            }}
          />
          <div style={{ marginTop: 16, fontSize: 12, color: '#8c8c8c' }}>
            {(data?.avg_ai_latency_ms || 0) < 500 ? '性能正常' : '性能偏慢'}
          </div>
        </Card>
      </Col>

      {/* Media Integrity */}
      <Col xs={24} sm={12} lg={6}>
        <Card loading={loading}>
          <Statistic
            title="损坏媒体文件"
            value={data?.total_corrupt_files || 0}
            prefix={<FileExclamationOutlined />}
            valueStyle={{
              color: (data?.total_corrupt_files || 0) === 0 ? '#52c41a' : '#ff4d4f',
            }}
          />
          <div style={{ marginTop: 16, fontSize: 12, color: '#8c8c8c' }}>
            {(data?.total_corrupt_files || 0) === 0 ? '无损坏文件' : '需要检查'}
          </div>
        </Card>
      </Col>
    </Row>
  );
};

export default KPICards;
