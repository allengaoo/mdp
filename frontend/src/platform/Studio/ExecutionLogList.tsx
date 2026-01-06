/**
 * Execution Log List View component.
 */
import React from 'react';
import { Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';

interface ExecutionLogData {
  id: string;
  time: string;
  actionName: string;
  user: string;
  status: 'SUCCESS' | 'FAILED';
  duration: number;
}

const ExecutionLogList: React.FC = () => {
  // Mock data
  const mockData: ExecutionLogData[] = [
    {
      id: '1',
      time: '2024-01-15 12:30:00',
      actionName: 'Execute Strike Action',
      user: 'user-003',
      status: 'SUCCESS',
      duration: 156,
    },
    {
      id: '2',
      time: '2024-01-15 12:15:00',
      actionName: 'Assign to Mission',
      user: 'user-001',
      status: 'SUCCESS',
      duration: 98,
    },
    {
      id: '3',
      time: '2024-01-15 12:00:00',
      actionName: 'Update Intelligence',
      user: 'user-002',
      status: 'SUCCESS',
      duration: 67,
    },
    {
      id: '4',
      time: '2024-01-15 11:30:00',
      actionName: 'Execute Strike Action',
      user: 'user-003',
      status: 'FAILED',
      duration: 45,
    },
    {
      id: '5',
      time: '2024-01-15 11:15:00',
      actionName: 'Scramble Fighters',
      user: 'user-001',
      status: 'SUCCESS',
      duration: 203,
    },
    {
      id: '6',
      time: '2024-01-15 11:00:00',
      actionName: 'Execute Strike Action',
      user: 'user-002',
      status: 'SUCCESS',
      duration: 142,
    },
    {
      id: '7',
      time: '2024-01-15 10:35:00',
      actionName: 'Refuel Fighter',
      user: 'user-001',
      status: 'SUCCESS',
      duration: 89,
    },
    {
      id: '8',
      time: '2024-01-15 10:30:00',
      actionName: 'Execute Strike Action',
      user: 'user-001',
      status: 'SUCCESS',
      duration: 125,
    },
  ];

  const columns: ColumnsType<ExecutionLogData> = [
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
      width: 180,
      sorter: (a, b) => a.time.localeCompare(b.time),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Action Name',
      dataIndex: 'actionName',
      key: 'actionName',
      width: 200,
    },
    {
      title: 'User',
      dataIndex: 'user',
      key: 'user',
      width: 120,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'SUCCESS' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Duration (ms)',
      dataIndex: 'duration',
      key: 'duration',
      width: 120,
      render: (duration: number) => `${duration}ms`,
    },
  ];

  return (
    <div style={{ background: '#fff', padding: '24px', borderRadius: 8 }}>
      <Table
        columns={columns}
        dataSource={mockData}
        rowKey="id"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  );
};

export default ExecutionLogList;

