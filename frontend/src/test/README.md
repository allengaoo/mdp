# 前端单元测试说明

本文档描述 MDP 平台前端单元测试的结构和使用方法。

## 测试框架

- **Vitest** - 测试运行器（与 Vite 深度集成）
- **React Testing Library** - React 组件测试工具
- **jsdom** - 浏览器环境模拟

## 测试文件结构

```
frontend/src/
├── test/
│   ├── setup.ts          # 测试环境配置
│   └── README.md         # 本文档
├── api/
│   ├── ontology.ts       # API 客户端函数
│   ├── ontology.test.ts  # API 测试 (13 个测试)
│   ├── formatters.ts     # 格式化工具函数
│   └── formatters.test.ts # 格式化工具测试 (38 个测试)
└── utils/
    ├── dagreLayout.ts    # Dagre 布局算法
    └── dagreLayout.test.ts # 布局算法测试 (9 个测试)
```

## 测试统计

| 测试文件 | 测试数量 | 描述 |
|---------|---------|------|
| `ontology.test.ts` | 13 | API 客户端函数测试 |
| `formatters.test.ts` | 38 | 数据格式化工具测试 |
| `dagreLayout.test.ts` | 9 | 图布局算法测试 |
| **总计** | **60** | |

## 运行测试

### 运行所有测试

```bash
npm run test:run
```

### 监听模式（开发时使用）

```bash
npm run test
```

### 生成覆盖率报告

```bash
npm run test:coverage
```

### UI 模式

```bash
npm run test:ui
```

## 测试用例说明

### 1. API 客户端测试 (`ontology.test.ts`)

测试 API 客户端函数，使用 `vi.mock` 模拟 axios 请求：

- `fetchProjects` - 获取项目列表
- `fetchObjectTypes` - 获取对象类型（支持按项目过滤）
- `fetchLinkTypes` - 获取链接类型
- `fetchDatasources` - 获取数据源
- `fetchSharedProperties` - 获取共享属性
- `createObjectType` - 创建对象类型
- `updateObjectType` - 更新对象类型

### 2. 格式化工具测试 (`formatters.test.ts`)

测试纯函数，无需模拟：

- `formatDate` - 日期格式化
- `formatFileSize` - 文件大小格式化
- `truncateText` - 文本截断
- `snakeToTitleCase` - snake_case 转 Title Case
- `camelToTitleCase` - camelCase 转 Title Case
- `generateId` - 生成随机 ID
- `isEmpty` - 判断对象是否为空

### 3. 布局算法测试 (`dagreLayout.test.ts`)

测试 ReactFlow 图布局算法：

- 空图处理
- 单节点布局
- 多节点布局
- 保留原始数据
- 自定义布局方向
- 自定义节点尺寸
- 自定义间距
- 复杂图结构

## 编写测试指南

### 1. 文件命名

测试文件与源文件同名，添加 `.test.ts` 或 `.test.tsx` 后缀：

```
source.ts → source.test.ts
Component.tsx → Component.test.tsx
```

### 2. 测试结构

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('功能模块', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该执行某个行为', () => {
    // 准备
    const input = 'test';
    
    // 执行
    const result = someFunction(input);
    
    // 断言
    expect(result).toBe('expected');
  });
});
```

### 3. Mock 外部依赖

```typescript
// Mock 模块
vi.mock('./axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// 使用 mock
vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });
```

### 4. 异步测试

```typescript
it('应该处理异步操作', async () => {
  vi.mocked(api.fetch).mockResolvedValueOnce(mockData);
  
  const result = await fetchSomething();
  
  expect(result).toEqual(mockData);
});
```

## 覆盖率目标

建议覆盖率目标：

- **工具函数**: 90%+
- **API 客户端**: 80%+
- **React 组件**: 70%+

## 注意事项

1. **隔离测试**: 每个测试应该独立运行，使用 `beforeEach` 清理状态
2. **Mock 清理**: 使用 `vi.clearAllMocks()` 确保 mock 状态不会污染其他测试
3. **异步等待**: 使用 `await` 和 `waitFor` 处理异步操作
4. **描述性命名**: 使用中文描述测试用例，便于理解测试意图
