/**
 * 单元测试: Ontology API 客户端函数
 * 
 * NOTE: ontology.ts 现在内部使用 V3 API，需要 mock V3 模块进行测试。
 * 只有部分函数（如 fetchDatasources, createObjectType, updateObjectType）仍使用 V1 API。
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  fetchProjects,
  fetchObjectTypes,
  fetchLinkTypes,
  fetchDatasources,
  fetchSharedProperties,
  createObjectType,
  updateObjectType,
  IOntologyProject,
  IObjectType,
  ILinkType,
} from './ontology';
import apiClient from './axios';

// Mock V3 API module (used by most functions now)
vi.mock('./v3/ontology', () => ({
  fetchProjects: vi.fn(),
  fetchProjectById: vi.fn(),
  fetchObjectTypes: vi.fn(),
  fetchLinkTypes: vi.fn(),
  fetchSharedProperties: vi.fn(),
}));

// Mock axios client (still used by some functions)
vi.mock('./axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

// Import mocked V3 API
import * as v3Api from './v3/ontology';

describe('Ontology API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('fetchProjects', () => {
    it('应该通过 V3 API 获取项目列表并适配为 V1 格式', async () => {
      // V3 API 返回的数据格式
      const mockV3Projects = [
        {
          id: 'proj-1',
          name: 'Project 1',
          description: 'Test project',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(v3Api.fetchProjects).mockResolvedValueOnce(mockV3Projects);

      const result = await fetchProjects();

      expect(v3Api.fetchProjects).toHaveBeenCalledTimes(1);
      // 验证适配后的 V1 格式
      expect(result).toEqual([
        {
          id: 'proj-1',
          title: 'Project 1',
          description: 'Test project',
          tags: [],
          objectCount: 0,
          linkCount: 0,
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ]);
    });

    it('应该在 V3 API 返回空时返回空数组', async () => {
      vi.mocked(v3Api.fetchProjects).mockResolvedValueOnce([]);

      const result = await fetchProjects();

      expect(result).toEqual([]);
    });

    it('应该在 V3 API 失败时回退到 V1 API', async () => {
      const error = new Error('V3 API unavailable');
      vi.mocked(v3Api.fetchProjects).mockRejectedValueOnce(error);

      const mockV1Projects: IOntologyProject[] = [
        {
          id: 'proj-fallback',
          title: 'Fallback Project',
          description: 'V1 fallback',
          tags: ['v1'],
          objectCount: 2,
          linkCount: 1,
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ];
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockV1Projects });

      const result = await fetchProjects();

      expect(apiClient.get).toHaveBeenCalledWith('/meta/projects', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockV1Projects);
    });
  });

  describe('fetchObjectTypes', () => {
    const mockV3ObjectTypes = [
      {
        id: 'obj-1',
        api_name: 'unit',
        display_name: 'Unit',
        description: 'A unit type',
        properties: [
          {
            api_name: 'name',
            display_name: 'Name',
            data_type: 'STRING',
            is_required: true,
            is_primary_key: false,
            is_title: true,
            default_value: null,
          },
        ],
      },
    ];

    it('应该通过 V3 API 获取所有对象类型并适配为 V1 格式', async () => {
      vi.mocked(v3Api.fetchObjectTypes).mockResolvedValueOnce(mockV3ObjectTypes);

      const result = await fetchObjectTypes();

      expect(v3Api.fetchObjectTypes).toHaveBeenCalledTimes(1);
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe('obj-1');
      expect(result[0].api_name).toBe('unit');
      expect(result[0].property_schema).toHaveProperty('name');
      expect(result[0].property_schema!.name.type).toBe('STRING');
    });

    it('应该忽略 projectId 过滤（V3 使用绑定机制）', async () => {
      vi.mocked(v3Api.fetchObjectTypes).mockResolvedValueOnce(mockV3ObjectTypes);

      // Console spy to check warning
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const result = await fetchObjectTypes('proj-1');

      expect(v3Api.fetchObjectTypes).toHaveBeenCalledTimes(1);
      expect(consoleSpy).toHaveBeenCalledWith(
        '[V3 Migration] projectId filtering not supported in V3 architecture'
      );
      expect(result).toHaveLength(1);

      consoleSpy.mockRestore();
    });

    it('应该在 V3 API 返回空时返回空数组', async () => {
      vi.mocked(v3Api.fetchObjectTypes).mockResolvedValueOnce([]);

      const result = await fetchObjectTypes();

      expect(result).toEqual([]);
    });

    it('应该在 V3 API 失败时回退到 V1 API', async () => {
      vi.mocked(v3Api.fetchObjectTypes).mockRejectedValueOnce(new Error('V3 unavailable'));

      const mockV1Types: IObjectType[] = [
        {
          id: 'obj-fallback',
          api_name: 'fallback',
          display_name: 'Fallback',
        },
      ];
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockV1Types });

      const result = await fetchObjectTypes();

      expect(apiClient.get).toHaveBeenCalledWith('/meta/object-types', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockV1Types);
    });
  });

  describe('fetchLinkTypes', () => {
    it('应该通过 V3 API 获取所有链接类型并适配为 V1 格式', async () => {
      const mockV3LinkTypes = [
        {
          id: 'link-1',
          api_name: 'belongs_to',
          display_name: 'Belongs To',
          source_object_def_id: 'obj-1',
          target_object_def_id: 'obj-2',
          cardinality: 'MANY_TO_ONE',
        },
      ];

      vi.mocked(v3Api.fetchLinkTypes).mockResolvedValueOnce(mockV3LinkTypes);

      const result = await fetchLinkTypes();

      expect(v3Api.fetchLinkTypes).toHaveBeenCalledTimes(1);
      expect(result).toEqual([
        {
          id: 'link-1',
          api_name: 'belongs_to',
          display_name: 'Belongs To',
          description: null,
          source_type_id: 'obj-1',
          target_type_id: 'obj-2',
          cardinality: 'MANY_TO_ONE',
          mapping_config: undefined,
          created_at: undefined,
          updated_at: undefined,
        },
      ]);
    });

    it('应该在 V3 API 失败时回退到 V1 API', async () => {
      vi.mocked(v3Api.fetchLinkTypes).mockRejectedValueOnce(new Error('V3 unavailable'));

      const mockV1Links: ILinkType[] = [
        {
          id: 'link-fallback',
          api_name: 'fallback_link',
          display_name: 'Fallback Link',
          source_type_id: 'obj-a',
          target_type_id: 'obj-b',
          cardinality: 'ONE_TO_MANY',
        },
      ];
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockV1Links });

      const result = await fetchLinkTypes();

      expect(apiClient.get).toHaveBeenCalledWith('/meta/link-types', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockV1Links);
    });
  });

  describe('fetchDatasources', () => {
    it('应该通过 V1 API 获取所有数据源', async () => {
      const mockDatasources = [
        {
          id: 'ds-1',
          table_name: 'users',
          db_type: 'PostgreSQL',
          columns_schema: [{ name: 'id', type: 'integer' }],
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockDatasources });

      const result = await fetchDatasources();

      expect(apiClient.get).toHaveBeenCalledWith('/meta/datasources', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockDatasources);
    });
  });

  describe('fetchSharedProperties', () => {
    it('应该通过 V3 API 获取所有共享属性并适配为 V1 格式', async () => {
      const mockV3Props = [
        {
          id: 'prop-1',
          api_name: 'location',
          display_name: 'Location',
          data_type: 'GEO_POINT',
          description: 'Geographic location',
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(v3Api.fetchSharedProperties).mockResolvedValueOnce(mockV3Props);

      const result = await fetchSharedProperties();

      expect(v3Api.fetchSharedProperties).toHaveBeenCalledTimes(1);
      expect(result).toEqual([
        {
          id: 'prop-1',
          api_name: 'location',
          display_name: 'Location',
          data_type: 'GEO_POINT',
          formatter: null,
          description: 'Geographic location',
          created_at: '2024-01-01T00:00:00Z',
        },
      ]);
    });

    it('应该在 V3 API 失败时回退到 V1 API', async () => {
      vi.mocked(v3Api.fetchSharedProperties).mockRejectedValueOnce(new Error('V3 unavailable'));

      const mockV1Props = [
        {
          id: 'prop-fallback',
          api_name: 'fallback_prop',
          display_name: 'Fallback Property',
          data_type: 'STRING',
        },
      ];
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockV1Props });

      const result = await fetchSharedProperties();

      expect(apiClient.get).toHaveBeenCalledWith('/meta/shared-properties', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockV1Props);
    });
  });

  describe('createObjectType', () => {
    it('应该通过 V1 API 创建新的对象类型', async () => {
      const newObjectType = {
        api_name: 'vehicle',
        display_name: 'Vehicle',
        description: 'A vehicle type',
      };
      const createdObjectType: IObjectType = {
        id: 'obj-new',
        ...newObjectType,
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: createdObjectType });

      const result = await createObjectType(newObjectType);

      expect(apiClient.post).toHaveBeenCalledWith('/meta/object-types', newObjectType);
      expect(result).toEqual(createdObjectType);
      expect(result.id).toBe('obj-new');
    });

    it('应该正确传播创建错误', async () => {
      const error = new Error('Validation failed');
      vi.mocked(apiClient.post).mockRejectedValueOnce(error);

      await expect(createObjectType({})).rejects.toThrow('Validation failed');
    });
  });

  describe('updateObjectType', () => {
    it('应该通过 V1 API 更新现有的对象类型', async () => {
      const updateData = {
        display_name: 'Updated Name',
      };
      const updatedObjectType: IObjectType = {
        id: 'obj-1',
        api_name: 'unit',
        display_name: 'Updated Name',
      };

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: updatedObjectType });

      const result = await updateObjectType('obj-1', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/meta/object-types/obj-1', updateData);
      expect(result.display_name).toBe('Updated Name');
    });

    it('应该正确传播更新错误', async () => {
      const error = new Error('Not found');
      vi.mocked(apiClient.put).mockRejectedValueOnce(error);

      await expect(updateObjectType('invalid-id', {})).rejects.toThrow('Not found');
    });
  });
});
