# MDP 平台详细架构

## 前端代码结构

### API 层 (`frontend/src/api/`)

#### V3 客户端 (`api/v3/client.ts`)
- 创建 axios 实例，baseURL: `/api/v3`
- 配置请求/响应拦截器

#### 连接器 API (`api/v3/connectors.ts`)

| 函数 | HTTP | 端点 | 说明 |
|------|------|------|------|
| `fetchConnectors()` | GET | /connectors | 获取连接器列表 |
| `fetchConnector(id)` | GET | /connectors/{id} | 获取连接器详情 |
| `createConnector(data)` | POST | /connectors | 创建连接器 |
| `testConnection(data)` | POST | /connectors/test | 测试连接 |
| `exploreSource(id)` | GET | /connectors/{id}/explorer | 探索数据源表 |
| `fetchSyncJobs(connId?)` | GET | /sync-jobs | 获取同步任务列表 |
| `createSyncJob(data)` | POST | /sync-jobs | 创建同步任务 |
| `runSyncJob(id)` | POST | /sync-jobs/{id}/run | 执行同步任务 |
| `fetchTargetTables(includeColumns, onlySynced)` | GET | /sync-jobs/target-tables | 获取目标表列表 |

#### 本体 API (`api/v3/ontology.ts`)

| 函数 | HTTP | 端点 | 说明 |
|------|------|------|------|
| `fetchObjectTypes()` | GET | /ontology/object-types | 获取对象类型列表 |
| `fetchObjectType(id)` | GET | /ontology/object-types/{id} | 获取对象类型详情 |
| `createObjectType(data)` | POST | /ontology/object-types | 创建对象类型 |
| `updateObjectType(id, data)` | PUT | /ontology/object-types/{id} | 更新对象类型 |
| `fetchLinkTypes()` | GET | /ontology/link-types | 获取链接类型列表 |
| `fetchSharedProperties()` | GET | /ontology/shared-properties | 获取共享属性列表 |

### 页面组件

#### ConnectorDetail.tsx

**主要组件结构：**
```
ConnectorDetail
├── SyncJobsTab          # 同步任务管理
│   ├── 任务列表表格
│   ├── 立即执行按钮
│   └── 执行日志查看
├── ExplorerTab          # 数据探索
│   ├── 表树形列表 (左侧)
│   ├── 表详情展示 (右侧)
│   └── 创建同步任务按钮
└── CreateJobModal       # 创建同步任务弹窗
```

**关键函数：**
- `loadExplorer()` - 调用 `exploreSource(connectorId)` 获取表列表
- `handleCreateJob(tableInfo)` - 打开创建同步任务弹窗
- `handleRunJob(jobId)` - 调用 `runSyncJob(jobId)` 执行同步

#### ObjectTypeWizard.tsx

**3 步向导流程：**
1. **Step 1: Basic Info** - 基本信息（api_name, display_name, description）
2. **Step 2: Backing Datasource** - 数据源选择
   - 从同步任务选择（推荐）
   - 上传 CSV
   - 从数据目录选择
3. **Step 3: Property Mapping** - 属性映射配置

**关键函数：**
- `handleTargetTableSelect(record)` - 选择同步任务目标表
- `handleDataSourceSelect(record)` - 选择数据目录数据源
- `parseCSVFile(file)` - 解析 CSV 文件
- `handleCreate()` - 提交创建对象类型

#### ObjectTypeEditor.tsx

**Tab 结构：**
- Basic Info - 基本信息编辑
- Datasource - 数据源信息（只读）
- Property Mapping - 属性映射编辑

---

## 后端代码结构

### API 层 (`backend/app/api/v3/`)

#### connectors.py

**路由前缀：** `/api/v3/connectors` 和 `/api/v3/sync-jobs`

| 端点 | 方法 | 函数 | 调用的 CRUD |
|------|------|------|-------------|
| /connectors | GET | `list_connectors` | `connector_crud.list_connections_summary` |
| /connectors | POST | `create_connector` | `connector_crud.create_connection` |
| /connectors/{id} | GET | `get_connector` | `connector_crud.get_connection` |
| /connectors/{id}/explorer | GET | `explore_source` | `connector_crud.explore_source` |
| /sync-jobs | GET | `list_sync_jobs` | `sync_crud.list_sync_jobs_with_connection` |
| /sync-jobs | POST | `create_sync_job` | `sync_crud.create_sync_job` |
| /sync-jobs/target-tables | GET | `list_target_tables` | `sync_crud.list_target_tables` |
| /sync-jobs/{id}/run | POST | `trigger_sync_job` | `sync_worker.run_sync_job` (BackgroundTask) |

#### ontology.py

**路由前缀：** `/api/v3/ontology`

| 端点 | 方法 | 函数 | 调用的 CRUD |
|------|------|------|-------------|
| /object-types | GET | `list_object_types` | `ontology_crud.list_object_types` |
| /object-types | POST | `create_object_type` | `ontology_crud.create_object_type` |
| /object-types/{id} | GET | `get_object_type` | `ontology_crud.get_object_type_full` |
| /object-types/{id} | PUT | `update_object_type` | `ontology_crud.update_object_type` |

### Engine 层 (`backend/app/engine/`)

#### connector_crud.py

| 函数 | 说明 |
|------|------|
| `create_connection(session, data)` | 创建连接器记录 |
| `get_connection(session, conn_id)` | 获取连接器详情 |
| `list_connections_summary(session)` | 列出连接器摘要 |
| `test_connection(conn_type, config_json)` | 测试连接是否可用 |
| `explore_source(conn_type, config_json)` | 探索数据源表结构 |

#### sync_crud.py

| 函数 | 说明 |
|------|------|
| `create_sync_job(session, data)` | 创建同步任务（返回警告） |
| `list_sync_jobs(session, connection_id)` | 列出同步任务 |
| `list_sync_jobs_with_connection(session)` | 列出同步任务（含连接信息） |
| `list_target_tables(session, include_columns, only_synced)` | 获取目标表列表 |
| `get_target_table_columns(table_name)` | 获取目标表的列结构 |
| `create_run_log(session, job_id)` | 创建执行日志 |
| `complete_run_log(session, log_id, status)` | 完成执行日志 |

#### sync_worker.py

| 函数 | 说明 |
|------|------|
| `run_sync_job(job_id, run_log_id)` | 执行同步任务（后台任务） |
| `_get_raw_store_engine()` | 获取 mdp_raw_store 数据库引擎 |
| `_get_ontology_raw_data_engine()` | 获取 ontology_raw_data 数据库引擎 |
| `_copy_to_ontology_raw_data(target_table, sync_mode)` | 复制数据到 ontology_raw_data |

**同步执行流程：**
1. 从源数据库读取数据（使用 pandas）
2. 写入 mdp_raw_store（目标表）
3. 复制到 ontology_raw_data（第二阶段）
4. 更新执行日志状态

#### ontology_crud.py

| 函数 | 说明 |
|------|------|
| `create_object_type(session, data)` | 创建对象类型 |
| `get_object_type(session, obj_id)` | 获取对象类型 |
| `get_object_type_full(session, obj_id)` | 获取完整对象类型（含属性和数据源） |
| `update_object_type(session, obj_id, data)` | 更新对象类型 |
| `get_object_type_datasource(session, obj_def_id)` | 获取对象类型的数据源信息 |

#### mapping_crud.py

| 函数 | 说明 |
|------|------|
| `create_mapping(session, data)` | 创建映射定义 |
| `list_mappings_by_connection(session, conn_id)` | 按连接ID列出映射 |
| `generate_mapping_spec_from_table(table_name)` | 从表结构生成映射规范 |

---

## 数据模型

### 系统层 (system.py)

#### Connection
```python
class Connection(SQLModel, table=True):
    __tablename__ = "sys_connection"
    id: str                    # UUID
    name: str                  # 连接器名称
    conn_type: str            # MYSQL, POSTGRES, S3, etc.
    config_json: Dict         # 连接配置
    status: str               # ACTIVE, ERROR, TESTING
```

#### SyncJobDef
```python
class SyncJobDef(SQLModel, table=True):
    __tablename__ = "sys_sync_job_def"
    id: str
    connection_id: str        # 关联连接器
    name: str                 # 任务名称
    source_config: Dict       # {"table": "users"}
    target_table: str         # mdp_raw_store 中的表名
    sync_mode: str            # FULL_OVERWRITE, INCREMENTAL
    is_enabled: bool
    last_run_status: str      # SUCCESS, FAILED, RUNNING
    last_run_at: datetime
    rows_synced: int
```

#### SyncRunLog
```python
class SyncRunLog(SQLModel, table=True):
    __tablename__ = "sys_sync_run_log"
    id: str
    job_id: str               # 关联同步任务
    start_time: datetime
    end_time: datetime
    duration_ms: int
    rows_affected: int
    status: str               # RUNNING, SUCCESS, FAILED
    message: str              # 错误信息或成功摘要
```

### 上下文层 (context.py)

#### ObjectMappingDef
```python
class ObjectMappingDef(SQLModel, table=True):
    __tablename__ = "ctx_object_mapping_def"
    id: str
    object_def_id: str        # 关联对象类型
    source_connection_id: str # 关联连接器
    source_table_name: str    # mdp_raw_store 中的表名
    mapping_spec: Dict        # React Flow 节点和边配置
    status: str               # DRAFT, PUBLISHED, ARCHIVED
```

### 本体层 (ontology.py)

#### ObjectTypeDef
```python
class ObjectTypeDef(SQLModel, table=True):
    __tablename__ = "meta_object_type_def"
    id: str
    api_name: str             # 唯一标识符
    display_name: str         # 显示名称
    description: str
    is_abstract: bool
    parent_type_id: str       # 父类型（继承）
```

#### ObjectTypeVer
```python
class ObjectTypeVer(SQLModel, table=True):
    __tablename__ = "meta_object_type_ver"
    id: str
    object_def_id: str        # 关联对象类型定义
    version_number: str       # v1.0, v1.1, etc.
    schema_snapshot: Dict     # 版本快照
    is_latest: bool
```

#### SharedPropertyDef
```python
class SharedPropertyDef(SQLModel, table=True):
    __tablename__ = "meta_shared_property_def"
    id: str
    api_name: str
    display_name: str
    data_type: str            # STRING, INTEGER, DOUBLE, etc.
    description: str
```

---

## 模块依赖关系

```
前端组件
    │
    ▼
前端 API 层 (api/v3/*.ts)
    │
    ▼ HTTP 请求
后端 API 层 (api/v3/*.py)
    │
    ▼ 函数调用
Engine 层 (engine/v3/*.py, engine/sync_worker.py)
    │
    ▼ ORM 操作
Models 层 (models/*.py)
    │
    ▼ SQL
数据库 (MySQL)
```
