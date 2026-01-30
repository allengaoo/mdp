/**
 * MappingEditor - Main page for multimodal mapping
 * 3-column layout: Source | Canvas | Target
 * Bottom panel: Preview
 */
import React, { useState, useCallback } from 'react';
import { Layout, Button, Space, Modal, Select, message, Spin } from 'antd';
import { SaveOutlined, SendOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { Node, Edge } from 'reactflow';

import MappingCanvas from './MappingCanvas';
import SourcePanel from './SourcePanel';
import TargetPanel from './TargetPanel';
import PreviewPanel from './PreviewPanel';
import {
  createMapping,
  updateMapping,
  publishMapping,
  previewMapping,
  TRANSFORM_FUNCTIONS,
  MappingSpec,
} from '../../../api/v3/mapping';

const { Sider, Content } = Layout;

interface MappingEditorProps {
  mappingId?: string;
  initialData?: {
    objectDefId: string;
    connectionId: string;
    tableName: string;
    nodes: Node[];
    edges: Edge[];
  };
}

const MappingEditor: React.FC<MappingEditorProps> = ({
  mappingId,
  initialData,
}) => {
  // State
  const [connectionId, setConnectionId] = useState(initialData?.connectionId || '');
  const [tableName, setTableName] = useState(initialData?.tableName || '');
  const [objectTypeId, setObjectTypeId] = useState(initialData?.objectDefId || '');
  const [nodes, setNodes] = useState<Node[]>(initialData?.nodes || []);
  const [edges, setEdges] = useState<Edge[]>(initialData?.edges || []);
  
  // Preview state
  const [previewColumns, setPreviewColumns] = useState<string[]>([]);
  const [previewData, setPreviewData] = useState<Record<string, any>[]>([]);
  const [previewWarnings, setPreviewWarnings] = useState<string[]>([]);
  const [previewLoading, setPreviewLoading] = useState(false);
  
  // UI state
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [transformModalVisible, setTransformModalVisible] = useState(false);
  const [transformPosition, setTransformPosition] = useState({ x: 0, y: 0 });
  const [selectedTransform, setSelectedTransform] = useState<string>('');

  // Convert React Flow nodes/edges to MappingSpec
  const getMappingSpec = useCallback((): MappingSpec => {
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type as 'source' | 'transform' | 'target',
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    };
  }, [nodes, edges]);

  // Handle preview
  const handlePreview = async () => {
    if (!connectionId || !tableName) {
      message.warning('请先选择数据源和表');
      return;
    }

    if (nodes.length === 0) {
      message.warning('请先添加映射节点');
      return;
    }

    setPreviewLoading(true);
    try {
      const result = await previewMapping({
        source_connection_id: connectionId,
        source_table_name: tableName,
        mapping_spec: getMappingSpec(),
        limit: 5,
      });

      setPreviewColumns(result.columns);
      setPreviewData(result.data);
      setPreviewWarnings(result.warnings || []);
    } catch (error: any) {
      message.error(`预览失败: ${error.message}`);
    } finally {
      setPreviewLoading(false);
    }
  };

  // Handle save
  const handleSave = async () => {
    if (!connectionId || !tableName || !objectTypeId) {
      message.warning('请选择数据源、表和目标对象类型');
      return;
    }

    setSaving(true);
    try {
      if (mappingId) {
        await updateMapping(mappingId, {
          source_table_name: tableName,
          mapping_spec: getMappingSpec(),
        });
        message.success('保存成功');
      } else {
        const result = await createMapping({
          object_def_id: objectTypeId,
          source_connection_id: connectionId,
          source_table_name: tableName,
          mapping_spec: getMappingSpec(),
        });
        message.success(`创建成功: ${result.id}`);
      }
    } catch (error: any) {
      message.error(`保存失败: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Handle publish
  const handlePublish = async () => {
    if (!mappingId) {
      message.warning('请先保存映射定义');
      return;
    }

    setPublishing(true);
    try {
      await publishMapping(mappingId);
      message.success('发布成功，后台索引任务已启动');
    } catch (error: any) {
      message.error(`发布失败: ${error.message}`);
    } finally {
      setPublishing(false);
    }
  };

  // Handle add transform from context menu
  const handleAddTransform = (position: { x: number; y: number }) => {
    setTransformPosition(position);
    setTransformModalVisible(true);
  };

  // Confirm add transform
  const confirmAddTransform = () => {
    if (!selectedTransform) {
      message.warning('请选择转换函数');
      return;
    }

    const func = TRANSFORM_FUNCTIONS.find((f) => f.value === selectedTransform);
    const newNode: Node = {
      id: `transform-${Date.now()}`,
      type: 'transform',
      position: transformPosition,
      data: {
        function: selectedTransform,
        label: func?.label || selectedTransform,
      },
    };

    setNodes((nds) => [...nds, newNode]);
    setTransformModalVisible(false);
    setSelectedTransform('');
  };

  return (
    <Layout style={{ height: '100%', background: '#fff' }}>
      {/* Header */}
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: 16, fontWeight: 500 }}>多模态映射编辑器</span>
        <Space>
          <Button icon={<SaveOutlined />} onClick={handleSave} loading={saving}>
            保存
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handlePublish}
            loading={publishing}
            disabled={!mappingId}
          >
            发布 & 索引
          </Button>
        </Space>
      </div>

      {/* Main content */}
      <Layout style={{ flex: 1 }}>
        {/* Left sidebar - Source */}
        <Sider width={280} style={{ background: '#fafafa', borderRight: '1px solid #f0f0f0' }}>
          <SourcePanel
            connectionId={connectionId}
            tableName={tableName}
            onConnectionChange={setConnectionId}
            onTableChange={setTableName}
          />
        </Sider>

        {/* Center - Canvas + Preview */}
        <Content style={{ display: 'flex', flexDirection: 'column' }}>
          {/* Canvas */}
          <div style={{ flex: 1, minHeight: 0 }}>
            <MappingCanvas
              nodes={nodes}
              edges={edges}
              onNodesChange={setNodes}
              onEdgesChange={setEdges}
              onAddTransform={handleAddTransform}
            />
          </div>

          {/* Preview panel */}
          <div style={{ height: 200, borderTop: '1px solid #f0f0f0' }}>
            <PreviewPanel
              columns={previewColumns}
              data={previewData}
              loading={previewLoading}
              warnings={previewWarnings}
              onRunPreview={handlePreview}
            />
          </div>
        </Content>

        {/* Right sidebar - Target */}
        <Sider width={280} style={{ background: '#fafafa', borderLeft: '1px solid #f0f0f0' }}>
          <TargetPanel
            objectTypeId={objectTypeId}
            onObjectTypeChange={setObjectTypeId}
          />
        </Sider>
      </Layout>

      {/* Transform selection modal */}
      <Modal
        title={
          <span>
            <ThunderboltOutlined style={{ marginRight: 8 }} />
            添加转换函数
          </span>
        }
        open={transformModalVisible}
        onOk={confirmAddTransform}
        onCancel={() => setTransformModalVisible(false)}
        okText="添加"
        cancelText="取消"
      >
        <Select
          style={{ width: '100%' }}
          placeholder="选择转换函数"
          value={selectedTransform || undefined}
          onChange={setSelectedTransform}
          options={TRANSFORM_FUNCTIONS.map((f) => ({
            label: f.label,
            value: f.value,
          }))}
        />
      </Modal>
    </Layout>
  );
};

export default MappingEditor;
