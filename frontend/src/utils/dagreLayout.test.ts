/**
 * 单元测试: Dagre 布局工具函数
 */
import { describe, it, expect } from 'vitest';
import { getLayoutedElements, DagreLayoutOptions } from './dagreLayout';
import { Node, Edge } from 'reactflow';

describe('dagreLayout', () => {
  describe('getLayoutedElements', () => {
    it('应该返回空数组当输入为空时', () => {
      const result = getLayoutedElements([], []);
      
      expect(result.nodes).toEqual([]);
      expect(result.edges).toEqual([]);
    });

    it('应该为单个节点计算位置', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [];

      const result = getLayoutedElements(nodes, edges);

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0].id).toBe('node-1');
      expect(result.nodes[0].position).toBeDefined();
      expect(typeof result.nodes[0].position.x).toBe('number');
      expect(typeof result.nodes[0].position.y).toBe('number');
    });

    it('应该为多个节点计算不同的位置', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
        { id: 'node-2', data: { label: 'Node 2' }, position: { x: 0, y: 0 } },
        { id: 'node-3', data: { label: 'Node 3' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [
        { id: 'e1-2', source: 'node-1', target: 'node-2' },
        { id: 'e2-3', source: 'node-2', target: 'node-3' },
      ];

      const result = getLayoutedElements(nodes, edges);

      expect(result.nodes).toHaveLength(3);
      
      // 验证节点有不同的 y 坐标（垂直布局）
      const positions = result.nodes.map(n => n.position);
      const yValues = positions.map(p => p.y);
      const uniqueY = new Set(yValues);
      expect(uniqueY.size).toBeGreaterThan(1);
    });

    it('应该保留原始节点数据', () => {
      const nodes: Node[] = [
        { 
          id: 'node-1', 
          data: { label: 'Test', customField: 'value' }, 
          position: { x: 0, y: 0 },
          type: 'custom',
        },
      ];
      const edges: Edge[] = [];

      const result = getLayoutedElements(nodes, edges);

      expect(result.nodes[0].id).toBe('node-1');
      expect(result.nodes[0].data.label).toBe('Test');
      expect(result.nodes[0].data.customField).toBe('value');
      expect(result.nodes[0].type).toBe('custom');
    });

    it('应该返回原始边数据不变', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
        { id: 'node-2', data: { label: 'Node 2' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [
        { id: 'e1-2', source: 'node-1', target: 'node-2', type: 'smoothstep' },
      ];

      const result = getLayoutedElements(nodes, edges);

      expect(result.edges).toEqual(edges);
    });

    it('应该支持自定义布局方向 (LR)', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
        { id: 'node-2', data: { label: 'Node 2' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [
        { id: 'e1-2', source: 'node-1', target: 'node-2' },
      ];
      const options: DagreLayoutOptions = { direction: 'LR' };

      const result = getLayoutedElements(nodes, edges, options);

      expect(result.nodes).toHaveLength(2);
      
      // 在 LR 布局中，节点应该有不同的 x 坐标
      const xValues = result.nodes.map(n => n.position.x);
      expect(xValues[0]).not.toBe(xValues[1]);
    });

    it('应该支持自定义节点尺寸', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
      ];
      const options: DagreLayoutOptions = {
        nodeWidth: 200,
        nodeHeight: 100,
      };

      const result = getLayoutedElements(nodes, [], options);

      // 布局应该成功完成
      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0].position).toBeDefined();
    });

    it('应该支持自定义间距', () => {
      const nodes: Node[] = [
        { id: 'node-1', data: { label: 'Node 1' }, position: { x: 0, y: 0 } },
        { id: 'node-2', data: { label: 'Node 2' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [
        { id: 'e1-2', source: 'node-1', target: 'node-2' },
      ];
      
      const defaultResult = getLayoutedElements(nodes, edges);
      const customResult = getLayoutedElements(nodes, edges, {
        nodeSep: 200,
        rankSep: 300,
      });

      // 自定义间距应该产生不同的布局
      const defaultDistance = Math.abs(
        defaultResult.nodes[0].position.y - defaultResult.nodes[1].position.y
      );
      const customDistance = Math.abs(
        customResult.nodes[0].position.y - customResult.nodes[1].position.y
      );
      
      expect(customDistance).toBeGreaterThan(defaultDistance);
    });

    it('应该处理复杂的图结构', () => {
      // 创建一个菱形图: A -> B, A -> C, B -> D, C -> D
      const nodes: Node[] = [
        { id: 'A', data: { label: 'A' }, position: { x: 0, y: 0 } },
        { id: 'B', data: { label: 'B' }, position: { x: 0, y: 0 } },
        { id: 'C', data: { label: 'C' }, position: { x: 0, y: 0 } },
        { id: 'D', data: { label: 'D' }, position: { x: 0, y: 0 } },
      ];
      const edges: Edge[] = [
        { id: 'e-ab', source: 'A', target: 'B' },
        { id: 'e-ac', source: 'A', target: 'C' },
        { id: 'e-bd', source: 'B', target: 'D' },
        { id: 'e-cd', source: 'C', target: 'D' },
      ];

      const result = getLayoutedElements(nodes, edges);

      expect(result.nodes).toHaveLength(4);
      expect(result.edges).toHaveLength(4);
      
      // 所有节点都应该有有效的位置
      result.nodes.forEach(node => {
        expect(node.position).toBeDefined();
        expect(Number.isFinite(node.position.x)).toBe(true);
        expect(Number.isFinite(node.position.y)).toBe(true);
      });
    });
  });
});
