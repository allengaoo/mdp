/**
 * HealthDetailDrawer - Detail drawer with trends and error samples
 */
import React, { useEffect, useState } from 'react';
import {
  Drawer,
  Tabs,
  Table,
  Tag,
  Spin,
  Empty,
  Typography,
  Button,
  Tooltip,
  message,
} from 'antd';
import { CopyOutlined } from '@ant-design/icons';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ColumnsType } from 'antd/es/table';
import type {
  IObjectHealthSummary,
  IIndexJobRun,
  IIndexErrorSample,
  ErrorCategory,
} from '../../../api/v3/health';
import {
  fetchObjectHistory,
  fetchJobErrors,
  getErrorCategoryColor,
} from '../../../api/v3/health';

const { Text, Paragraph } = Typography;

interface HealthDetailDrawerProps {
  open: boolean;
  object: IObjectHealthSummary | null;
  onClose: () => void;
}

const HealthDetailDrawer: React.FC<HealthDetailDrawerProps> = ({
  open,
  object,
  onClose,
}) => {
  const [history, setHistory] = useState<IIndexJobRun[]>([]);
  const [errors, setErrors] = useState<IIndexErrorSample[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingErrors, setLoadingErrors] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  // Load history when object changes
  useEffect(() => {
    if (open && object) {
      loadHistory();
    }
  }, [open, object]);

  const loadHistory = async () => {
    if (!object) return;
    setLoadingHistory(true);
    try {
      const result = await fetchObjectHistory(object.object_def_id, 7, 20);
      setHistory(result.runs);
      // Auto-select first run to show errors
      if (result.runs.length > 0) {
        setSelectedRunId(result.runs[0].id);
        loadErrors(result.runs[0].id);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadErrors = async (runId: string) => {
    setLoadingErrors(true);
    try {
      const result = await fetchJobErrors(runId);
      setErrors(result);
    } catch (error) {
      console.error('Failed to load errors:', error);
    } finally {
      setLoadingErrors(false);
    }
  };

  // Prepare chart data
  const chartData = history
    .slice()
    .reverse()
    .map((run) => ({
      time: new Date(run.start_time).toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
      }),
      indexed: run.rows_indexed,
      errors: run.rows_processed - run.rows_indexed,
      latency: run.metrics_json?.ai_latency_avg_ms || 0,
    }));

  const errorColumns: ColumnsType<IIndexErrorSample> = [
    {
      title: '原始行 ID',
      dataIndex: 'raw_row_id',
      key: 'raw_row_id',
      width: 150,
      render: (id: string) => (
        <Tooltip title="点击复制">
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => {
              navigator.clipboard.writeText(id);
              message.success('已复制');
            }}
          >
            {id.length > 12 ? `${id.substring(0, 12)}...` : id}
          </Button>
        </Tooltip>
      ),
    },
    {
      title: '类别',
      dataIndex: 'error_category',
      key: 'error_category',
      width: 120,
      render: (category: ErrorCategory) => (
        <Tag color={getErrorCategoryColor(category)}>{category}</Tag>
      ),
      filters: [
        { text: 'SEMANTIC', value: 'SEMANTIC' },
        { text: 'AI_INFERENCE', value: 'AI_INFERENCE' },
        { text: 'MEDIA_IO', value: 'MEDIA_IO' },
        { text: 'SYSTEM', value: 'SYSTEM' },
      ],
      onFilter: (value, record) => record.error_category === value,
    },
    {
      title: '错误消息',
      dataIndex: 'error_message',
      key: 'error_message',
      render: (msg: string) => (
        <Paragraph
          ellipsis={{ rows: 2, expandable: true }}
          style={{ margin: 0, fontSize: 12 }}
        >
          {msg}
        </Paragraph>
      ),
    },
  ];

  return (
    <Drawer
      title={
        <span>
          健康详情 - {object?.object_name || object?.object_def_id?.substring(0, 8)}
        </span>
      }
      placement="right"
      width={720}
      open={open}
      onClose={onClose}
    >
      <Tabs
        defaultActiveKey="trends"
        items={[
          {
            key: 'trends',
            label: '趋势分析',
            children: (
              <Spin spinning={loadingHistory}>
                {chartData.length === 0 ? (
                  <Empty description="暂无历史数据" />
                ) : (
                  <>
                    {/* Indexed vs Errors Chart */}
                    <div style={{ marginBottom: 24 }}>
                      <Text strong>索引数量 vs 错误数量</Text>
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="time" fontSize={11} />
                          <YAxis fontSize={11} />
                          <RechartsTooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="indexed"
                            stroke="#52c41a"
                            name="成功索引"
                            strokeWidth={2}
                          />
                          <Line
                            type="monotone"
                            dataKey="errors"
                            stroke="#ff4d4f"
                            name="错误数"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* AI Latency Chart */}
                    <div>
                      <Text strong>AI 推理延迟趋势</Text>
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="time" fontSize={11} />
                          <YAxis fontSize={11} unit=" ms" />
                          <RechartsTooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="latency"
                            stroke="#722ed1"
                            name="AI 延迟 (ms)"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </>
                )}
              </Spin>
            ),
          },
          {
            key: 'errors',
            label: `错误样本 (${errors.length})`,
            children: (
              <Spin spinning={loadingErrors}>
                {errors.length === 0 ? (
                  <Empty description="无错误样本" />
                ) : (
                  <Table
                    columns={errorColumns}
                    dataSource={errors}
                    rowKey="id"
                    size="small"
                    pagination={{ pageSize: 10 }}
                  />
                )}
              </Spin>
            ),
          },
        ]}
      />
    </Drawer>
  );
};

export default HealthDetailDrawer;
