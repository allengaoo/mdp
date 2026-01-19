# 后端测试说明

本文档描述 MDP 平台后端测试的结构和使用方法。

## 测试框架

- **pytest** - 测试运行器
- **pytest-asyncio** - 异步测试支持
- **httpx** - 异步 HTTP 客户端（API 测试）
- **Pydantic** - 数据验证

## 测试文件结构

```
backend/tests/
├── conftest.py              # 测试配置和 fixtures
├── README.md                # 本文档
│
├── # API 集成测试
├── test_actions.py          # ActionDefinition API 测试 (8)
├── test_object_types.py     # ObjectType API 测试 (6)
├── test_link_types.py       # LinkType API 测试 (4)
├── test_projects.py         # Project API 测试 (5)
├── test_functions.py        # FunctionDefinition API 测试 (5)
├── test_shared_properties.py # SharedProperty API 测试 (5)
├── test_datasources.py      # DataSource API 测试 (3)
│
└── # 单元测试
├── test_schemas.py          # Schema 验证测试 (22)
└── test_action_runner.py    # 动作执行器测试 (15)
```

## 测试统计

### API 集成测试

| 测试文件 | 测试数量 | 描述 |
|---------|---------|------|
| `test_actions.py` | 8 | Action CRUD + 别名端点 |
| `test_object_types.py` | 6 | ObjectType CRUD + 分页 |
| `test_link_types.py` | 4 | LinkType 列表 + 分页 |
| `test_projects.py` | 5 | Project CRUD |
| `test_functions.py` | 5 | Function CRUD + 分页 |
| `test_shared_properties.py` | 5 | SharedProperty CRUD |
| `test_datasources.py` | 3 | DataSource 列表 |
| **小计** | **36** | |

### 单元测试

| 测试文件 | 测试数量 | 描述 |
|---------|---------|------|
| `test_schemas.py` | 22 | Pydantic 模型验证 |
| `test_action_runner.py` | 15 | 动作执行引擎 |
| **小计** | **37** | |

### 新增测试

| 测试文件 | 测试数量 | 描述 |
|---------|---------|------|
| `test_execute_api.py` | 20+ | 代码执行 API 测试 |
| `test_execution_logs.py` | 10 | 执行日志 API 测试 |
| `test_runtime_context.py` | 20+ | 运行时上下文测试 |
| `test_code_executor.py` | 30+ | 代码执行引擎测试 |

### 总计

| 类型 | 数量 |
|-----|------|
| API 集成测试 | 66+ |
| 单元测试 | 67+ |
| **总计** | **133+** |

## 运行测试

### 运行所有测试

```bash
cd backend
py -m pytest
```

### 运行指定测试文件

```bash
py -m pytest tests/test_schemas.py -v
```

### 运行指定测试类

```bash
py -m pytest tests/test_schemas.py::TestPropertyDef -v
```

### 运行指定测试方法

```bash
py -m pytest tests/test_schemas.py::TestPropertyDef::test_valid_property_def -v
```

### 只运行单元测试

```bash
py -m pytest tests/test_schemas.py tests/test_action_runner.py -v
```

### 只运行 API 集成测试

```bash
py -m pytest tests/test_actions.py tests/test_object_types.py tests/test_link_types.py tests/test_projects.py tests/test_functions.py tests/test_shared_properties.py tests/test_datasources.py -v
```

### 生成覆盖率报告

```bash
py -m pytest --cov=app --cov-report=html
```

## 测试类型说明

### API 集成测试

这些测试通过 HTTP 请求验证 API 端点的行为：

```python
@pytest.mark.asyncio
async def test_list_object_types(self, client: AsyncClient):
    """测试列出所有对象类型"""
    response = await client.get("/api/v1/meta/object-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

**特点：**
- 使用 `httpx.AsyncClient` 发送请求
- 通过 ASGI Transport 直接调用 FastAPI 应用
- 测试完整的请求/响应流程
- 包含数据清理逻辑

### 单元测试

这些测试直接验证函数和类的行为：

```python
def test_valid_property_def(self):
    """应该创建有效的属性定义"""
    prop = PropertyDef(
        key="fuel",
        label="燃油",
        type="INTEGER",
        required=True
    )
    assert prop.key == "fuel"
```

**特点：**
- 直接调用函数/方法
- 不需要 HTTP 请求
- 快速执行
- 便于测试边界条件

## 测试用例说明

### Schema 验证测试 (`test_schemas.py`)

测试 Pydantic 模型的验证逻辑：

- **PropertyDef** - 属性定义验证
- **LinkMappingConfig** - 链接映射配置验证
- **ObjectTypeRequest** - 对象类型请求验证
- **LinkTypeRequest** - 链接类型请求验证
- **ActionRunRequest** - 动作执行请求验证
- **ProjectResponse** - 项目响应验证

### 动作执行器测试 (`test_action_runner.py`)

测试动作执行引擎：

- **execute_action** - 动作执行
  - Strike 动作执行
  - Refuel 动作执行
  - 未知动作处理
  - 默认参数处理

- **validate_action** - 动作验证
  - 有效动作验证
  - 空 action_id 处理
  - 复杂参数验证

## 编写测试指南

### 1. 测试文件命名

```
test_<module>.py
```

### 2. 测试类命名

```python
class Test<ClassName>:
    """<ClassName> 测试"""
```

### 3. 测试方法命名

```python
def test_<behavior>_<condition>(self):
    """应该 <expected behavior>"""
```

### 4. 异步测试

```python
@pytest.mark.asyncio
async def test_async_function(self):
    result = await some_async_function()
    assert result is not None
```

### 5. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("value1", "result1"),
    ("value2", "result2"),
])
def test_with_parameters(self, input, expected):
    assert some_function(input) == expected
```

## Fixtures

### client fixture

提供异步 HTTP 客户端：

```python
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
```

### db_session fixture

提供数据库会话：

```python
@pytest.fixture
def db_session():
    with Session(engine) as session:
        yield session
```

## 注意事项

1. **异步测试**: 使用 `@pytest.mark.asyncio` 装饰器
2. **数据清理**: API 测试创建数据后应删除
3. **隔离性**: 每个测试应该独立运行
4. **错误处理**: 测试应该覆盖错误情况
5. **边界条件**: 测试空值、None、无效输入等
