# MDP 平台 API 参考

## 基础信息

| 项目 | 值 |
|------|-----|
| 前端地址 | http://localhost:3000 |
| 后端地址 | http://localhost:8000 |
| API 前缀 | /api/v3 |
| Swagger UI | http://localhost:8000/docs |

## 连接器 API

### 基础端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /connectors | 列出所有连接器 |
| POST | /connectors | 创建连接器 |
| GET | /connectors/{id} | 获取连接器详情 |
| PUT | /connectors/{id} | 更新连接器 |
| DELETE | /connectors/{id} | 删除连接器 |
| POST | /connectors/test | 测试连接（不保存）|
| POST | /connectors/{id}/test | 测试已保存的连接 |
| GET | /connectors/{id}/explorer | 探索数据源表结构 |

### 请求/响应示例

#### 创建连接器
```json
// POST /api/v3/connectors
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

#### 探索数据源
```json
// GET /api/v3/connectors/{id}/explorer
// Response:
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

---

## 同步任务 API

### 基础端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /sync-jobs | 列出所有同步任务 |
| POST | /sync-jobs | 创建同步任务 |
| GET | /sync-jobs/{id} | 获取任务详情 |
| PUT | /sync-jobs/{id} | 更新任务 |
| DELETE | /sync-jobs/{id} | 删除任务 |
| POST | /sync-jobs/{id}/run | 执行同步 |
| GET | /sync-jobs/{id}/logs | 获取执行日志 |
| GET | /sync-jobs/target-tables | 获取目标表列表 |

### 请求/响应示例

#### 创建同步任务
```json
// POST /api/v3/sync-jobs
{
  "connection_id": "xxx",
  "name": "Sync users table",
  "source_config": {"table": "users"},
  "target_table": "raw_users",
  "sync_mode": "FULL_OVERWRITE"
}

// Response:
{
  "job": {
    "id": "xxx",
    "connection_id": "xxx",
    "name": "Sync users table",
    "target_table": "raw_users",
    "sync_mode": "FULL_OVERWRITE",
    "is_enabled": true,
    "last_run_status": null
  },
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

#### 执行同步
```json
// POST /api/v3/sync-jobs/{id}/run
// Response:
{
  "id": "log-xxx",
  "job_id": "job-xxx",
  "start_time": "2026-01-28T10:00:00Z",
  "status": "RUNNING",
  "triggered_by": "API"
}
```

#### 获取目标表列表
```json
// GET /api/v3/sync-jobs/target-tables?include_columns=true
// Response:
{
  "tables": [
    {
      "target_table": "raw_users",
      "connection_id": "xxx",
      "connection_name": "MySQL Production",
      "sync_job_id": "job-xxx",
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

---

## 本体 API

### 对象类型端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /ontology/object-types | 列出所有对象类型 |
| POST | /ontology/object-types | 创建对象类型 |
| GET | /ontology/object-types/{id} | 获取对象类型详情 |
| PUT | /ontology/object-types/{id} | 更新对象类型 |
| DELETE | /ontology/object-types/{id} | 删除对象类型 |

### 链接类型端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /ontology/link-types | 列出所有链接类型 |
| POST | /ontology/link-types | 创建链接类型 |
| GET | /ontology/link-types/{id} | 获取链接类型详情 |

### 共享属性端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /ontology/shared-properties | 列出所有共享属性 |
| POST | /ontology/shared-properties | 创建共享属性 |

### 请求/响应示例

#### 创建对象类型
```json
// POST /api/v3/ontology/object-types
{
  "api_name": "user",
  "display_name": "User",
  "description": "System user entity",
  "property_schema": [
    {
      "key": "id",
      "label": "ID",
      "type": "INTEGER",
      "required": true
    },
    {
      "key": "name",
      "label": "Name",
      "type": "STRING",
      "required": false
    }
  ],
  "project_id": "project-xxx"
}
```

#### 获取对象类型详情
```json
// GET /api/v3/ontology/object-types/{id}
// Response:
{
  "id": "xxx",
  "api_name": "user",
  "display_name": "User",
  "properties": [
    {
      "api_name": "id",
      "display_name": "ID",
      "data_type": "INTEGER",
      "is_primary_key": true
    }
  ],
  "datasource": {
    "source_table_name": "raw_users",
    "connection_id": "conn-xxx",
    "connection_name": "MySQL Production"
  }
}
```

---

## 映射 API

### 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /mappings | 列出所有映射 |
| POST | /mappings | 创建映射 |
| GET | /mappings/{id} | 获取映射详情 |
| PUT | /mappings/{id} | 更新映射 |
| DELETE | /mappings/{id} | 删除映射 |

### 请求/响应示例

#### 创建映射
```json
// POST /api/v3/mappings
{
  "object_def_id": "obj-xxx",
  "source_connection_id": "conn-xxx",
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

---

## 项目 API

### 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /projects | 列出所有项目 |
| POST | /projects | 创建项目 |
| GET | /projects/{id} | 获取项目详情 |
| PUT | /projects/{id} | 更新项目 |
| DELETE | /projects/{id} | 删除项目 |

---

## 错误响应格式

```json
{
  "detail": "Error message",
  "error_type": "ValidationError",
  "error_msg": "Detailed error description",
  "traceback": "..." // 仅在 DEBUG 模式
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
