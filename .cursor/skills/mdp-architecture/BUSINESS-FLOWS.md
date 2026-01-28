# MDP 平台业务流程

## 流程 1：数据同步

### 业务场景
在连接器管理页面，点击同步任务的"立即执行"按钮，将数据从源数据库同步到 mdp_raw_store，再复制到 ontology_raw_data。

### 调用链

```
用户操作: 点击"立即执行"按钮
    │
    ▼
前端: ConnectorDetail.tsx
    │ handleRunJob(jobId)
    │     └─ runSyncJob(jobId)  [api/v3/connectors.ts]
    │
    ▼ POST /api/v3/sync-jobs/{job_id}/run
后端 API: connectors.py
    │ trigger_sync_job(job_id, background_tasks)
    │     ├─ sync_crud.get_sync_job(session, job_id)
    │     ├─ sync_crud.create_run_log(session, job_id)
    │     └─ background_tasks.add_task(run_sync_job, job_id, run_log_id)
    │
    ▼ 后台任务
后端 Engine: sync_worker.py
    │ run_sync_job(job_id, run_log_id)
    │     ├─ 阶段1: 从源数据库同步到 mdp_raw_store
    │     │     ├─ _get_raw_store_engine()
    │     │     └─ pandas read_sql → to_sql
    │     ├─ 阶段2: 复制到 ontology_raw_data
    │     │     ├─ _get_ontology_raw_data_engine()
    │     │     └─ _copy_to_ontology_raw_data(target_table, sync_mode)
    │     └─ sync_crud.complete_run_log(session, log_id, status)
    │
    ▼
数据库:
    mdp_raw_store.{target_table} ← 源数据
    ontology_raw_data.{target_table} ← 复制数据
```

### 涉及的数据库表
- `sys_sync_job_def` - 同步任务定义
- `sys_sync_run_log` - 执行日志
- `mdp_raw_store.{target_table}` - 原始数据目标表
- `ontology_raw_data.{target_table}` - 业务数据目标表

---

## 流程 2：创建同步任务

### 业务场景
在连接器详情页的数据探索 Tab 中，选择一个表，点击"创建同步任务"按钮。

### 调用链

```
用户操作: 数据探索 → 选择表 → 点击"创建同步任务"
    │
    ▼
前端: ConnectorDetail.tsx
    │ ExplorerTab 组件
    │     ├─ loadExplorer()
    │     │     └─ exploreSource(connectorId)  [api/v3/connectors.ts]
    │     └─ 点击表名 → setSelectedTable()
    │
    │ 点击"创建同步任务"按钮
    │     └─ openCreateJobModal(tableInfo)
    │         └─ 打开 Modal，自动填充表名
    │
    │ 提交表单
    │     └─ handleCreateJob()
    │         └─ createSyncJob(payload)  [api/v3/connectors.ts]
    │
    ▼ POST /api/v3/sync-jobs
后端 API: connectors.py
    │ create_sync_job(data)
    │     └─ sync_crud.create_sync_job(session, data)
    │
    ▼
后端 Engine: sync_crud.py
    │ create_sync_job(session, data)
    │     ├─ check_table_exists_in_raw_store(target_table)
    │     ├─ mapping_crud.list_mappings_by_connection(session, connection_id)
    │     ├─ 生成警告信息 (mapping_exists, mapping_table_mismatch, table_exists)
    │     └─ 创建 SyncJobDef 记录
    │
    ▼
数据库: sys_sync_job_def 新增记录
```

### 表单字段映射
| 前端字段 | 后端字段 | 说明 |
|----------|----------|------|
| 任务名称 | name | 如 "Sync users" |
| 源表名 | source_config.table | 源数据库中的表名 |
| 目标表名 | target_table | mdp_raw_store 中的表名 |
| 同步模式 | sync_mode | FULL_OVERWRITE / INCREMENTAL |

---

## 流程 3：创建对象类型

### 业务场景
在对象类型管理页面，点击"新建"按钮，通过 3 步向导创建对象类型。

### 调用链

```
用户操作: 对象类型管理 → 点击"新建"
    │
    ▼
前端: ObjectTypeList.tsx
    │ 点击"新建"按钮
    │     └─ setWizardVisible(true)
    │
    ▼
前端: ObjectTypeWizard.tsx
    │
    │ 步骤 1: Basic Info
    │     └─ 填写 api_name, display_name, description
    │
    │ 步骤 2: Backing Datasource (数据源选择)
    │     ├─ 方式1: 从同步任务选择 (推荐)
    │     │     ├─ fetchTargetTables(true, false)  [api/v3/connectors.ts]
    │     │     │     └─ GET /api/v3/sync-jobs/target-tables?include_columns=true
    │     │     └─ handleTargetTableSelect(record)
    │     ├─ 方式2: 上传 CSV
    │     │     └─ parseCSVFile(file)
    │     └─ 方式3: 从数据目录选择
    │           └─ fetchDatasources()  [api/ontology.ts]
    │
    │ 步骤 3: Property Mapping
    │     ├─ 选择主键 (primaryKey)
    │     └─ 配置属性映射 (propertyMappings)
    │
    │ 提交创建
    │     └─ handleCreate()
    │         └─ createObjectType(payload)  [api/ontology.ts]
    │
    ▼ POST /api/v1/meta/object-types 或 /api/v3/ontology/object-types
后端 API: ontology.py
    │ create_object_type(data)
    │     └─ ontology_crud.create_object_type(session, data)
    │
    ▼
后端 Engine: ontology_crud.py
    │ create_object_type(session, data)
    │     ├─ 创建 ObjectTypeDef 记录
    │     ├─ 创建 ObjectTypeVer 记录 (初始版本)
    │     └─ 创建 ObjectVerProperty 记录 (属性绑定)
    │
    ▼
数据库:
    meta_object_type_def 新增记录
    meta_object_type_ver 新增记录
    ont_object_ver_property 新增记录
```

### 数据流转
```
同步任务 (sys_sync_job_def)
    │ target_table
    ▼
目标表列表 API (GET /sync-jobs/target-tables)
    │ 返回 target_table + columns
    ▼
对象类型创建向导 (Step 2)
    │ 选择目标表，获取列结构
    ▼
属性映射配置 (Step 3)
    │ columns → property_schema
    ▼
对象类型创建 (POST /object-types)
    │ property_schema
    ▼
元数据存储 (meta_object_type_def, ont_object_ver_property)
```

---

## 流程 4：数据映射配置

### 业务场景
在对象类型编辑器的 Property Mapping Tab 中，配置源表列与对象属性的映射关系。

### 调用链

```
用户操作: 对象类型编辑器 → Property Mapping Tab
    │
    ▼
前端: ObjectTypeEditor.tsx
    │ 加载对象类型详情
    │     └─ fetchObjectType(id)  [api/v3/ontology.ts]
    │         └─ GET /api/v3/ontology/object-types/{id}
    │
    │ 显示属性映射表格
    │     └─ objectType.properties.map(...)
    │
    │ 修改映射
    │     └─ handlePropertyMappingChange(index, field, value)
    │
    │ 保存
    │     └─ handleSave()
    │         └─ updateObjectType(id, payload)  [api/v3/ontology.ts]
    │             └─ PUT /api/v3/ontology/object-types/{id}
    │
    ▼
后端 API: ontology.py
    │ update_object_type(obj_id, data)
    │     └─ ontology_crud.update_object_type(session, obj_id, data)
    │
    ▼
数据库: ont_object_ver_property 更新记录
```

---

## 流程 5：数据探索

### 业务场景
在连接器详情页的数据探索 Tab 中，查看连接器下的所有表和列信息。

### 调用链

```
用户操作: 连接器详情 → 数据探索 Tab
    │
    ▼
前端: ConnectorDetail.tsx (ExplorerTab)
    │ useEffect → loadExplorer()
    │     └─ exploreSource(connectorId)  [api/v3/connectors.ts]
    │
    ▼ GET /api/v3/connectors/{conn_id}/explorer
后端 API: connectors.py
    │ explore_source(conn_id)
    │     ├─ connector_crud.get_connection(session, conn_id)
    │     └─ connector_crud.explore_source(conn_type, config_json)
    │
    ▼
后端 Engine: connector_crud.py
    │ explore_source(conn_type, config_json)
    │     ├─ 创建数据库连接
    │     ├─ SQLAlchemy Inspector 获取表列表
    │     └─ 获取每个表的列信息
    │
    ▼
返回: SourceExplorerResponse
    {
      connection_id: string,
      conn_type: string,
      tables: [
        {
          name: string,
          columns: [{ name, type, nullable }]
        }
      ]
    }
```

---

## 组件与 API 对应关系

### ConnectorDetail.tsx

| 组件/操作 | 触发的 API | 说明 |
|-----------|------------|------|
| ExplorerTab 加载 | `GET /connectors/{id}/explorer` | 获取表列表 |
| 点击"创建同步任务" | `POST /sync-jobs` | 创建同步任务 |
| SyncJobsTab 加载 | `GET /sync-jobs?connection_id=xxx` | 获取任务列表 |
| 点击"立即执行" | `POST /sync-jobs/{id}/run` | 执行同步 |
| 查看执行日志 | `GET /sync-jobs/{id}/logs` | 获取日志 |

### ObjectTypeWizard.tsx

| 组件/操作 | 触发的 API | 说明 |
|-----------|------------|------|
| 向导打开 | `GET /sync-jobs/target-tables` | 获取目标表列表 |
| | `GET /meta/datasources` | 获取数据目录 |
| | `GET /ontology/shared-properties` | 获取共享属性 |
| 提交创建 | `POST /meta/object-types` | 创建对象类型 |

### ObjectTypeEditor.tsx

| 组件/操作 | 触发的 API | 说明 |
|-----------|------------|------|
| 页面加载 | `GET /ontology/object-types/{id}` | 获取对象类型详情 |
| 保存修改 | `PUT /ontology/object-types/{id}` | 更新对象类型 |
