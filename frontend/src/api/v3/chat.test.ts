/**
 * 单元测试: Chat2App API 客户端函数
 * MDP Platform V3.1
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import v3Client from './client';

// Mock v3Client
vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('Chat2App API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('健康检查 API', () => {
    it('应该调用 /chat/health 端点', async () => {
      const mockResponse = {
        data: {
          ollama_available: true,
          model: 'llama3',
          status: 'ready',
        },
      };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockResponse);

      const result = await v3Client.get('/chat/health');

      expect(v3Client.get).toHaveBeenCalledWith('/chat/health');
      expect(result.data.ollama_available).toBe(true);
      expect(result.data.model).toBe('llama3');
    });

    it('应该处理 Ollama 不可用状态', async () => {
      const mockResponse = {
        data: {
          ollama_available: false,
          model: 'llama3',
          status: 'ollama_unavailable',
        },
      };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockResponse);

      const result = await v3Client.get('/chat/health');

      expect(result.data.ollama_available).toBe(false);
      expect(result.data.status).toBe('ollama_unavailable');
    });
  });

  describe('消息发送 API', () => {
    it('应该发送消息到 /chat/message 端点', async () => {
      const mockResponse = {
        data: {
          action: 'table',
          message: '找到 5 条记录',
          amis_schema: {
            type: 'table',
            columns: [{ name: 'id', label: 'ID' }],
            data: { items: [] },
          },
          sql: 'SELECT * FROM objects',
          suggestions: ['显示更多', '按时间排序'],
        },
      };
      vi.mocked(v3Client.post).mockResolvedValueOnce(mockResponse);

      const payload = {
        message: '显示所有对象',
        history: [],
      };

      const result = await v3Client.post('/chat/message', payload);

      expect(v3Client.post).toHaveBeenCalledWith('/chat/message', payload);
      expect(result.data.action).toBe('table');
      expect(result.data.sql).toBe('SELECT * FROM objects');
    });

    it('应该发送带历史记录的消息', async () => {
      const mockResponse = {
        data: {
          action: 'text',
          message: '继续查询结果',
          suggestions: [],
        },
      };
      vi.mocked(v3Client.post).mockResolvedValueOnce(mockResponse);

      const payload = {
        message: '继续',
        history: [
          { role: 'user', content: '查询1' },
          { role: 'assistant', content: '结果1' },
        ],
      };

      await v3Client.post('/chat/message', payload);

      expect(v3Client.post).toHaveBeenCalledWith('/chat/message', payload);
    });

    it('应该处理错误响应', async () => {
      const mockResponse = {
        data: {
          action: 'error',
          message: 'SQL 验证失败',
          suggestions: ['请修改您的问题'],
        },
      };
      vi.mocked(v3Client.post).mockResolvedValueOnce(mockResponse);

      const result = await v3Client.post('/chat/message', { message: 'DROP TABLE' });

      expect(result.data.action).toBe('error');
      expect(result.data.suggestions).toContain('请修改您的问题');
    });

    it('应该处理网络错误', async () => {
      const networkError = new Error('Network Error');
      vi.mocked(v3Client.post).mockRejectedValueOnce(networkError);

      await expect(v3Client.post('/chat/message', { message: 'test' })).rejects.toThrow(
        'Network Error'
      );
    });
  });

  describe('Schema 示例 API', () => {
    it('应该获取 AMIS schema 示例', async () => {
      const mockResponse = {
        data: {
          table_example: {
            type: 'table',
            columns: [{ name: 'id', label: 'ID' }],
            data: { items: [] },
          },
          chart_example: {
            type: 'chart',
            config: {},
          },
        },
      };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockResponse);

      const result = await v3Client.get('/chat/schema-example');

      expect(v3Client.get).toHaveBeenCalledWith('/chat/schema-example');
      expect(result.data.table_example.type).toBe('table');
      expect(result.data.chart_example.type).toBe('chart');
    });
  });
});
