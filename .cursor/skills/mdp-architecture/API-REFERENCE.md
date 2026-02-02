# MDP 平台 API 参考

## 基础信息

| 项目 | 值 |
|------|-----|
| 前端地址 | http://localhost:3000 |
| 后端地址 | http://localhost:8000 |
| V1 API 前缀 | /api/v1/meta |
| V3 API 前缀 | /api/v3 |
| Swagger UI | http://localhost:8000/docs |

---

## 一、V1 兼容 API (推荐用于 CRUD 操作)

### 1.1 对象类型 API

#### 创建对象类型
```http
POST /api/v1/meta/object-types
Content-Type: application/json

{
  "api_name": "user",
  "display_name": "用户",
  "description": "系统用户实体",
  "project_id": "project-uuid",
  "source_connection_id": "conn-uuid",      // 可选：数据源连接
  "source_table_name": "raw_users",         // 可选：源表名
  "property_schema": {
    "id": {
      "label": "ID",
      "type": "INTEGER",
      "required": true,
      "is_primary_key": true
    },
    "name": {
      "label": "姓名",
      "type": "STRING",
      "required": false
    },
    "email": {
      "label": "邮箱",
      "type": "STRING",
      "required": false,
      "shared_property_id": "shared-prop-uuid"  // 可选：引用共享属性
    }
  }
}
```

**响应：**
```json
{
  "id": "obj-uuid",
  "api_name": "user",
  "display_name": "用户",
  "description": "系统用户实体",
  "property_schema": {...},
  "created_at": "2026-01-29T10:00:00Z",
  "updated_at": "2026-01-29T10:00:00Z"
}
```

#### 获取对象类型列表
```http
GET /api/v1/meta/object-types?project_id=xxx
```

#### 获取对象类型详情
```http
GET /api/v1/meta/object-types/{obj_id}
```

**响应（含 V3 详细信息）：**
```json
{
  "id": "obj-uuid",
  "api_name": "user",
  "display_name": "用户",
  "properties": [
    {
      "binding_id": 1,
      "property_def_id": "shared-prop-uuid",
      "shared_property_api_name": "email",
      "api_name": "email",
      "display_name": "邮箱",
      "data_type": "STRING",
      "is_primary_key": false,
      "is_indexed": false
    },
    {
      "binding_id": 2,
      "property_def_id": null,
      "shared_property_api_name": null,
      "api_name": "name",
      "display_name": "姓名",
      "data_type": "STRING",
      "is_primary_key": false,
      "is_indexed": false
    }
  ],
  "datasource": {
    "source_table_name": "raw_users",
    "connection_id": "conn-uuid",
    "connection_name": "MySQL Production"
  }
}
```

#### 更新对象类型
```http
PUT /api/v1/meta/object-types/{obj_id}
Content-Type: application/json

{
  "display_name": "更新后的名称",
  "description": "更新后的描述",
  "property_schema": {...}
}
```

#### 删除对象类型
```http
DELETE /api/v1/meta/object-types/{obj_id}
```

### 1.2 链接类型 API

```http
POST   /api/v1/meta/link-types
GET    /api/v1/meta/link-types
GET    /api/v1/meta/link-types/{id}
PUT    /api/v1/meta/link-types/{id}
DELETE /api/v1/meta/link-types/{id}
```

### 1.3 共享属性 API

```http
POST   /api/v1/meta/shared-properties
GET    /api/v1/meta/shared-properties
GET    /api/v1/meta/shared-properties/{id}
PUT    /api/v1/meta/shared-properties/{id}
DELETE /api/v1/meta/shared-properties/{id}
```

### 1.4 项目 API

```http
POST   /api/v1/meta/projects
GET    /api/v1/meta/projects          # 返回带统计信息
GET    /api/v1/meta/projects/{id}
PUT    /api/v1/meta/projects/{id}
DELETE /api/v1/meta/projects/{id}
```

### 1.5 函数定义 API

```http
POST   /api/v1/meta/functions
GET    /api/v1/meta/functions
GET    /api/v1/meta/functions/{id}
PUT    /api/v1/meta/functions/{id}
DELETE /api/v1/meta/functions/{id}
```

### 1.6 动作定义 API

```http
POST   /api/v1/meta/actions
GET    /api/v1/meta/actions
GET    /api/v1/meta/actions/{id}
PUT    /api/v1/meta/actions/{id}
DELETE /api/v1/meta/actions/{id}
```

### 1.7 执行 API

```http
# 执行动作
POST /api/v1/execute/action/run
{
  "action_id": "action-uuid",
  "object_id": "obj-instance-uuid",
  "params": {...}
}

# 查询执行日志
GET /api/v1/execute/logs?action_id=xxx&object_id=xxx

# 查询对象实例
GET /api/v1/execute/objects/{type_api_name}?limit=100&offset=0

# 测试代码 (V1 - 旧版)
POST /api/v1/execute/code/test
{
  "code": "print('hello')",
  "test_input": {...}
}

# 验证代码语法
POST /api/v1/execute/code/validate
{
  "code": "print('hello')"
}
```

### 1.8 代码执行 API (V3 - 推荐)

```http
# 测试代码执行
POST /api/v3/execute/code/test
{
  "code_content": "def main(context):\n    return context['x'] * 2",
  "context": {"x": 21},
  "executor_type": "auto",      # auto, builtin, subprocess, remote
  "timeout_seconds": 30
}

# 响应
{
  "success": true,
  "result": 42,
  "stdout": "",
  "stderr": "",
  "execution_time_ms": 15,
  "executor_used": "builtin",
  "error_message": null,
  "error_type": null,
  "traceback": null
}

# 测试函数执行 (by ID)
POST /api/v3/execute/function/{function_id}/test
{
  "context": {"x": 21},
  "executor_type": "auto",
  "timeout_seconds": 30
}
```

**执行器类型说明：**

| executor_type | 说明 | 适用场景 |
|---------------|------|----------|
| `auto` | 自动选择最佳执行器 | 默认推荐 |
| `builtin` | 进程内执行，可访问数据库 | 简单代码，需要 DB 操作 |
| `subprocess` | 子进程隔离执行 | numpy/pandas 等复杂计算 |
| `remote` | 远程沙箱执行 (K8s) | 生产环境，安全隔离 |

---

## 二、V3 API

### 2.1 本体 API (`/api/v3/ontology`)

#### 共享属性

```http
GET    /api/v3/ontology/properties
POST   /api/v3/ontology/properties
GET    /api/v3/ontology/properties/{prop_id}
PATCH  /api/v3/ontology/properties/{prop_id}
DELETE /api/v3/ontology/properties/{prop_id}
```

**创建共享属性：**
```json
POST /api/v3/ontology/properties
{
  "api_name": "email",
  "display_name": "邮箱地址",
  "data_type": "STRING",
  "description": "用户邮箱"
}
```

#### 对象类型

```http
# 对象类型列表（带统计）
GET /api/v3/ontology/objects/with-stats

# 对象类型 CRUD
GET    /api/v3/ontology/object-types
POST   /api/v3/ontology/object-types
GET    /api/v3/ontology/object-types/{def_id}

# 版本管理
GET    /api/v3/ontology/object-types/{def_id}/versions
POST   /api/v3/ontology/object-types/{def_id}/versions
PATCH  /api/v3/ontology/object-types/{def_id}/versions/{ver_id}

# 属性管理
GET    /api/v3/ontology/object-types/{def_id}/properties
POST   /api/v3/ontology/object-types/{def_id}/properties
```

**对象统计响应示例：**
```json
GET /api/v3/ontology/objects/with-stats

[
  {
    "id": "obj-uuid",
    "api_name": "user",
    "display_name": "用户",
    "stereotype": "ENTITY",
    "status": "PUBLISHED",
    "property_count": 5,
    "instance_count": 1000,
    "created_at": "2026-01-29T10:00:00Z",
    "updated_at": "2026-01-29T10:00:00Z"
  }
]
```

#### 链接类型

```http
GET    /api/v3/ontology/link-types
POST   /api/v3/ontology/link-types
GET    /api/v3/ontology/link-types/{def_id}
```

#### 拓扑图

```http
GET /api/v3/ontology/topology

# 响应
{
  "nodes": [
    {"id": "user", "type": "object", "label": "用户", "stereotype": "ENTITY"},
    {"id": "order", "type": "object", "label": "订单", "stereotype": "EVENT"}
  ],
  "edges": [
    {"id": "edge-1", "source": "user", "target": "order", "label": "下单"}
  ]
}
```

#### 动作和函数

```http
GET /api/v3/ontology/actions/with-functions
GET /api/v3/ontology/functions/for-list
GET /api/v3/ontology/actions/{action_id}/details
POST /api/v3/ontology/actions/{action_id}/execute
```

### 2.2 连接器 API (`/api/v3/connectors`)

```http
GET    /api/v3/connectors
POST   /api/v3/connectors
GET    /api/v3/connectors/{conn_id}
PUT    /api/v3/connectors/{conn_id}
DELETE /api/v3/connectors/{conn_id}

# 测试连接
POST   /api/v3/connectors/test
POST   /api/v3/connectors/{conn_id}/test

# 探索数据源
GET    /api/v3/connectors/{conn_id}/explorer
```

**创建连接器：**
```json
POST /api/v3/connectors
{
  "name": "MySQL Production",
  "conn_type": "MYSQL",
  "config_json": {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "root",
    "password": "xxx"
  }
}
```

**探索数据源响应：**
```json
GET /api/v3/connectors/{id}/explorer

{
  "connection_id": "xxx",
  "conn_type": "MYSQL",
  "tables": [
    {
      "name": "users",
      "columns": [
        {"name": "id", "type": "INT", "nullable": false},
        {"name": "name", "type": "VARCHAR(100)", "nullable": true}
      ]
    }
  ]
}
```

### 2.3 同步任务 API (`/api/v3/sync-jobs`)

```http
GET    /api/v3/sync-jobs
POST   /api/v3/sync-jobs
GET    /api/v3/sync-jobs/{job_id}
PUT    /api/v3/sync-jobs/{job_id}
DELETE /api/v3/sync-jobs/{job_id}

# 触发执行
POST   /api/v3/sync-jobs/{job_id}/run

# 执行日志
GET    /api/v3/sync-jobs/{job_id}/logs

# 目标表列表（用于对象类型创建）
GET    /api/v3/sync-jobs/target-tables?include_columns=true&only_synced=false
```

**创建同步任务：**
```json
POST /api/v3/sync-jobs
{
  "connection_id": "conn-uuid",
  "name": "Sync users table",
  "source_config": {"table": "users"},
  "target_table": "raw_users",
  "sync_mode": "FULL_OVERWRITE"
}

# 响应（含警告信息）
{
  "job": {...},
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

**目标表列表响应：**
```json
GET /api/v3/sync-jobs/target-tables?include_columns=true

{
  "tables": [
    {
      "target_table": "raw_users",
      "connection_id": "conn-uuid",
      "connection_name": "MySQL Production",
      "sync_job_id": "job-uuid",
      "sync_job_name": "Sync users",
      "last_sync_status": "SUCCESS",
      "columns": [
        {"name": "id", "type": "INT", "nullable": false},
        {"name": "name", "type": "VARCHAR(100)", "nullable": true}
      ]
    }
  ],
  "total": 1
}
```

### 2.4 项目 API (`/api/v3/projects`)

```http
GET    /api/v3/projects
GET    /api/v3/projects/with-stats
POST   /api/v3/projects
GET    /api/v3/projects/{project_id}
PATCH  /api/v3/projects/{project_id}
DELETE /api/v3/projects/{project_id}

# 项目-对象绑定
GET    /api/v3/projects/{project_id}/objects
POST   /api/v3/projects/{project_id}/objects
PATCH  /api/v3/projects/{project_id}/objects/{object_def_id}
DELETE /api/v3/projects/{project_id}/objects/{object_def_id}

# 项目作用域查询
GET    /api/v3/projects/{project_id}/object-types
GET    /api/v3/projects/{project_id}/link-types
GET    /api/v3/projects/{project_id}/shared-properties
```

### 2.5 映射 API (`/api/v3/mappings`)

```http
GET    /api/v3/mappings
POST   /api/v3/mappings
GET    /api/v3/mappings/{mapping_id}
PUT    /api/v3/mappings/{mapping_id}
DELETE /api/v3/mappings/{mapping_id}

# 预览转换
POST   /api/v3/mappings/preview

# 发布映射（触发索引）
POST   /api/v3/mappings/{mapping_id}/publish

# 血缘查询
GET    /api/v3/mappings/lineage/instance/{instance_id}
GET    /api/v3/mappings/lineage/mapping/{mapping_id}
GET    /api/v3/mappings/lineage/file?path=xxx
```

**创建映射：**
```json
POST /api/v3/mappings
{
  "object_def_id": "obj-uuid",
  "source_connection_id": "conn-uuid",
  "source_table_name": "raw_users",
  "mapping_spec": {
    "nodes": [
      {"id": "src_id", "type": "sourceColumn", "data": {"column": "id"}},
      {"id": "tgt_id", "type": "targetProperty", "data": {"property": "id"}}
    ],
    "edges": [
      {"id": "edge_1", "source": "src_id", "target": "tgt_id"}
    ]
  }
}
```

### 2.6 搜索 API (`/api/v3/search`)

```http
# 健康检查
GET /api/v3/search/health

# 混合搜索
POST /api/v3/search/objects
{
  "query": "搜索关键词",
  "object_types": ["user", "order"],  // 可选
  "filters": {                        // 可选
    "status": ["ACTIVE"]
  },
  "page": 1,
  "size": 20
}

# 获取分面
GET /api/v3/search/objects/facets

# 确保索引存在
POST /api/v3/search/objects/ensure-index
```

**搜索响应：**
```json
{
  "hits": [
    {
      "id": "instance-uuid",
      "object_type": "user",
      "properties": {
        "name": "张三",
        "email": "zhang@example.com"
      },
      "score": 0.95,
      "highlight": {
        "name": ["<em>张三</em>"]
      }
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20,
  "facets": {
    "object_type": [
      {"key": "user", "count": 50},
      {"key": "order", "count": 50}
    ]
  }
}
```

### 2.7 图分析 API (`/api/v3/graph`)

```http
# 图扩展
POST /api/v3/graph/expand
{
  "seed_ids": ["node-uuid-1", "node-uuid-2"],
  "depth": 2,
  "node_types": ["user", "order"],  // 可选
  "time_range": {                   // 可选
    "start": "2026-01-01",
    "end": "2026-01-31"
  }
}

# 最短路径
POST /api/v3/graph/shortest-path
{
  "source_id": "node-uuid-1",
  "target_id": "node-uuid-2",
  "max_depth": 5
}

# 图统计
GET /api/v3/graph/stats

# 节点邻居
GET /api/v3/graph/node/{node_id}

# 节点类型
GET /api/v3/graph/types
```

### 2.8 健康监控 API (`/api/v3/health`)

```http
# 系统健康摘要
GET /api/v3/health/summary

# 对象类型历史任务
GET /api/v3/health/objects/{object_def_id}/history

# 任务运行详情
GET /api/v3/health/jobs/{run_id}

# 任务错误样本
GET /api/v3/health/jobs/{run_id}/errors

# 触发重新索引
POST /api/v3/health/objects/{object_def_id}/reindex
```

### 2.9 Chat2App API (`/api/v3/chat`)

```http
# 健康检查
GET /api/v3/chat/health

# 发送消息
POST /api/v3/chat/message
{
  "message": "查询最近一周的订单",
  "history": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助您的？"}
  ]
}

# 响应
{
  "action": "SEARCH",
  "response_text": "为您找到以下订单...",
  "amis_schema": {...},  // 可选：AMIS 渲染 Schema
  "sql_query": "SELECT * FROM orders WHERE...",  // 可选
  "search_results": [...]  // 可选
}
```

---

## 三、错误响应格式

```json
{
  "detail": "Error message",
  "error_type": "ValidationError",
  "error_msg": "Detailed error description",
  "traceback": "..."  // 仅在 DEBUG 模式
}
```

### 常见状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容）|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器内部错误 |

---

## 四、常见问题

### Q: V1 和 V3 API 的区别？

- **V1 API** (`/api/v1/meta/`): 兼容旧架构，内部会自动转发到 V3 逻辑
- **V3 API** (`/api/v3/`): 新架构，支持版本化的对象类型和链接类型

**推荐**：
- 对象类型的 CRUD 操作使用 V1 API（自动处理版本逻辑）
- 查询统计、搜索、图分析使用 V3 API

### Q: 如何关联对象类型和数据源？

创建对象类型时传入 `source_connection_id` 和 `source_table_name`：

```json
POST /api/v1/meta/object-types
{
  "api_name": "user",
  "source_connection_id": "conn-uuid",
  "source_table_name": "raw_users",
  ...
}
```

这会自动创建 `ObjectMappingDef` 记录。

### Q: 如何区分共享属性和本地属性？

- **共享属性**: 在 `property_schema` 中包含 `shared_property_id`
- **本地属性**: 不包含 `shared_property_id`

```json
"property_schema": {
  "email": {
    "shared_property_id": "shared-prop-uuid",  // 共享属性
    "label": "邮箱"
  },
  "nickname": {
    "label": "昵称",  // 本地属性
    "type": "STRING"
  }
}
```
