# MDP Platform 元数据库设计文档

> **数据库名称**: `ontology_meta_new`  
> **架构版本**: V3.1  
> **最后更新**: 2026-01-23

---

## 一、分层架构概述

MDP Platform 的元数据库采用 **四层分离架构**，每一层有明确的职责边界：

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用层 (Application)                      │
│              前端 UI / API 消费者                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      上下文层 (Context Layer)                    │
│  ctx_*  │  场景化配置、项目绑定、映射定义、血缘追踪               │
├─────────────────────────────────────────────────────────────────┤
│                      本体层 (Ontology Layer)                     │
│  meta_* │  全局元数据定义：对象类型、链接类型、属性定义           │
├─────────────────────────────────────────────────────────────────┤
│                      系统层 (System Layer)                       │
│  sys_*  │  运行时基础设施：项目、连接器、数据集、执行日志         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      原始数据存储 (Raw Store)                    │
│              数据库: mdp_raw_store                               │
│              同步的外部数据、向量索引、ES索引                     │
└─────────────────────────────────────────────────────────────────┘
```

### 分层设计原则

| 层级 | 前缀 | 职责 | 变更频率 |
|------|------|------|----------|
| **System** | `sys_` | 运行时基础设施配置 | 低 |
| **Ontology** | `meta_`, `rel_` | 全局本体定义（单一真相来源） | 中 |
| **Context** | `ctx_` | 场景化配置与绑定 | 高 |

---

## 二、ER 关系图

```
                                    ┌─────────────────────────┐
                                    │      sys_project        │
                                    │  (项目/工作空间)          │
                                    └──────────┬──────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
    ┌───────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────┐
    │ctx_project_object_    │    │    sys_action_log       │    │ ctx_object_mapping_ │
    │       binding         │    │    (执行日志)            │    │        def          │
    │   (项目-对象绑定)       │    └─────────────────────────┘    │    (映射定义)         │
    └───────────┬───────────┘                                   └──────────┬──────────┘
                │                                                          │
                │ references                                               │
                ▼                                                          │
    ┌───────────────────────┐                                              │
    │ meta_object_type_def  │◄─────────────────────────────────────────────┘
    │   (对象类型定义)        │
    └───────────┬───────────┘
                │ 1:N
                ▼
    ┌───────────────────────┐         ┌─────────────────────────┐
    │ meta_object_type_ver  │────────▶│   meta_link_type_ver    │
    │   (对象类型版本)        │◄────────│    (链接类型版本)        │
    └───────────┬───────────┘         └───────────┬─────────────┘
                │                                  │
                │ N:M                              │ N:M
                ▼                                  ▼
    ┌───────────────────────┐         ┌─────────────────────────┐
    │rel_object_ver_property│         │  rel_link_ver_property  │
    │  (对象-属性绑定)        │         │    (链接-属性绑定)        │
    └───────────┬───────────┘         └───────────┬─────────────┘
                │                                  │
                └──────────────┬───────────────────┘
                               ▼
                ┌───────────────────────┐
                │meta_shared_property_  │
                │         def           │
                │    (公共属性池)         │
                └───────────────────────┘


    ╔═══════════════════════════════════════════════════════════════╗
    ║                      数据连接与同步                            ║
    ╚═══════════════════════════════════════════════════════════════╝

    ┌───────────────────────┐
    │     sys_connection    │
    │    (外部数据连接器)     │
    └───────────┬───────────┘
                │
                ├─────────────────┐
                │                 │
                ▼                 ▼
    ┌───────────────────┐   ┌─────────────────────┐
    │    sys_dataset    │   │  sys_sync_job_def   │
    │    (数据集定义)    │   │    (同步任务定义)    │
    └───────────────────┘   └──────────┬──────────┘
                                       │ 1:N
                                       ▼
                            ┌─────────────────────┐
                            │   sys_sync_run_log  │
                            │    (同步执行日志)    │
                            └─────────────────────┘


    ╔═══════════════════════════════════════════════════════════════╗
    ║                      行为与逻辑                                ║
    ╚═══════════════════════════════════════════════════════════════╝

    ┌───────────────────────┐
    │   meta_function_def   │
    │    (函数定义)          │
    └───────────┬───────────┘
                │ 1:1 references
                ▼
    ┌───────────────────────┐
    │   meta_action_def     │
    │    (动作定义)          │
    └───────────────────────┘
```

---

## 三、System Layer（系统层）

### 3.1 sys_project - 项目/工作空间

**用途**: 定义业务场景工作空间，作为对象绑定和应用配置的命名空间。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `name` | VARCHAR(100) | NOT NULL | 项目名称 |
| `description` | TEXT | NULL | 项目描述 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |
| `updated_at` | DATETIME | DEFAULT NOW() | 更新时间 |

```sql
CREATE TABLE sys_project (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

### 3.2 sys_connection - 外部数据连接器

**用途**: 存储外部数据源（MySQL、PostgreSQL、S3、Kafka、REST API）的连接配置。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `name` | VARCHAR(100) | NOT NULL | 连接器名称 |
| `conn_type` | VARCHAR(50) | NOT NULL | 类型: MYSQL, POSTGRES, S3, KAFKA, REST_API, ELASTICSEARCH |
| `config_json` | JSON | NOT NULL | 连接配置（加密存储） |
| `status` | VARCHAR(20) | DEFAULT 'ACTIVE' | 状态: ACTIVE, ERROR, TESTING |
| `error_message` | VARCHAR(500) | NULL | 最后错误信息 |
| `last_tested_at` | DATETIME | NULL | 最后测试时间 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |
| `updated_at` | DATETIME | DEFAULT NOW() | 更新时间 |

**config_json 示例**:
```json
{
  "host": "192.168.1.100",
  "port": 3306,
  "database": "production_db",
  "user": "readonly_user",
  "password": "encrypted_password"
}
```

---

### 3.3 sys_dataset - 数据集定义

**用途**: 指向连接器中的具体数据表/文件/API 端点。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `connection_id` | VARCHAR(36) | FK → sys_connection | 所属连接器 |
| `name` | VARCHAR(100) | NOT NULL | 数据集名称 |
| `location_config` | JSON | NOT NULL | 位置配置（表名/S3路径/API端点） |
| `cached_schema` | JSON | NULL | 缓存的 Schema 信息 |

**location_config 示例**:
```json
// MySQL
{"table": "user_profiles", "schema": "public"}

// S3
{"bucket": "data-lake", "prefix": "raw/events/"}

// REST API
{"endpoint": "/api/v2/users", "method": "GET"}
```

---

### 3.4 sys_sync_job_def - 同步任务定义

**用途**: 定义从外部数据源到 `mdp_raw_store` 的 ETL 同步任务。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `connection_id` | VARCHAR(36) | FK → sys_connection | 关联连接器 |
| `name` | VARCHAR(100) | NOT NULL | 任务名称 |
| `source_config` | JSON | NOT NULL | 源配置 `{"table": "users"}` |
| `target_table` | VARCHAR(100) | NOT NULL | 目标表名（在 mdp_raw_store） |
| `sync_mode` | VARCHAR(50) | DEFAULT 'FULL_OVERWRITE' | 同步模式: FULL_OVERWRITE, INCREMENTAL |
| `schedule_cron` | VARCHAR(100) | NULL | Cron 调度表达式 |
| `is_enabled` | BOOLEAN | DEFAULT TRUE | 是否启用 |
| `last_run_status` | VARCHAR(20) | NULL | 最后运行状态: SUCCESS, FAILED, RUNNING |
| `last_run_at` | DATETIME | NULL | 最后运行时间 |
| `rows_synced` | INT | NULL | 最后同步行数 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |
| `updated_at` | DATETIME | DEFAULT NOW() | 更新时间 |

---

### 3.5 sys_sync_run_log - 同步执行日志

**用途**: 记录每次同步任务的执行历史，用于审计和调试。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `job_id` | VARCHAR(36) | FK → sys_sync_job_def | 关联任务 |
| `start_time` | DATETIME | NOT NULL | 开始时间 |
| `end_time` | DATETIME | NULL | 结束时间 |
| `duration_ms` | INT | NULL | 执行耗时（毫秒） |
| `rows_affected` | INT | NULL | 影响行数 |
| `status` | VARCHAR(20) | DEFAULT 'RUNNING' | 状态: RUNNING, SUCCESS, FAILED |
| `message` | TEXT | NULL | 执行消息/错误堆栈 |
| `triggered_by` | VARCHAR(50) | DEFAULT 'MANUAL' | 触发方式: MANUAL, SCHEDULE, API |

---

### 3.6 sys_action_log - Action 执行日志

**用途**: 记录用户触发的 Action 执行历史。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `project_id` | VARCHAR(36) | INDEX | 项目 ID |
| `action_def_id` | VARCHAR(36) | INDEX | Action 定义 ID |
| `trigger_user_id` | VARCHAR(36) | NULL | 触发用户 |
| `input_params` | JSON | NULL | 执行入参 |
| `execution_status` | VARCHAR(20) | DEFAULT 'SUCCESS' | 状态: SUCCESS, FAILED |
| `error_message` | TEXT | NULL | 错误信息 |
| `duration_ms` | INT | NULL | 执行耗时 |
| `created_at` | DATETIME | INDEX | 创建时间 |

---

## 四、Ontology Layer（本体层）

### 4.1 meta_shared_property_def - 公共属性定义

**用途**: 全局属性池，定义可被多个对象类型复用的属性。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `api_name` | VARCHAR(100) | UNIQUE, INDEX | API 名称（代码引用） |
| `display_name` | VARCHAR(100) | NULL | 显示名称 |
| `data_type` | VARCHAR(50) | NOT NULL | 数据类型（见下表） |
| `description` | TEXT | NULL | 属性描述 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

**支持的 data_type**:

| 类型 | 说明 | 索引支持 |
|------|------|----------|
| `STRING` | 字符串 | ES text/keyword |
| `INT` | 整数 | ES long |
| `DOUBLE` | 双精度浮点 | ES double |
| `BOOLEAN` | 布尔值 | ES boolean |
| `DATETIME` | 日期时间 | ES date |
| `GEO_POINT` | 地理坐标 | ES geo_point |
| `JSON` | 嵌套对象 | ES nested |
| `VECTOR` | 向量嵌入 | Milvus |
| `MEDIA_REF` | 媒体引用 | MinIO/S3 |

---

### 4.2 meta_object_type_def - 对象类型定义

**用途**: 定义对象类型的不可变标识符（Definition），配合 Version 实现版本化管理。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `api_name` | VARCHAR(100) | UNIQUE, INDEX | API 名称（代码引用） |
| `stereotype` | VARCHAR(50) | DEFAULT 'ENTITY' | 原型: ENTITY, EVENT, DOCUMENT, MEDIA, METRIC |
| `current_version_id` | VARCHAR(36) | NULL | 当前使用的版本 ID |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

**stereotype 说明**:

| 原型 | 用途 | 典型示例 |
|------|------|----------|
| `ENTITY` | 业务实体 | 用户、订单、设备 |
| `EVENT` | 事件日志 | 登录事件、交易记录 |
| `DOCUMENT` | 文档数据 | 合同、报告、文章 |
| `MEDIA` | 媒体文件 | 图片、视频、音频 |
| `METRIC` | 度量指标 | 温度、销售额、点击率 |

---

### 4.3 meta_object_type_ver - 对象类型版本

**用途**: 存储对象类型的具体配置（显示名称、图标、索引配置等），支持多版本演进。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `def_id` | VARCHAR(36) | FK → meta_object_type_def | 所属定义 |
| `version_number` | VARCHAR(50) | NOT NULL | 版本号 (e.g., "1.0", "2.0-beta") |
| `display_name` | VARCHAR(100) | NULL | 显示名称 |
| `description` | TEXT | NULL | 描述 |
| `icon` | VARCHAR(255) | NULL | 图标（Ant Design 图标名或 URL） |
| `color` | VARCHAR(20) | NULL | 主题色（#HEX） |
| `status` | VARCHAR(50) | DEFAULT 'DRAFT' | 状态: DRAFT, PUBLISHED, DEPRECATED |
| `enable_global_search` | BOOLEAN | DEFAULT FALSE | 启用全文搜索（ES） |
| `enable_geo_index` | BOOLEAN | DEFAULT FALSE | 启用地理索引 |
| `enable_vector_index` | BOOLEAN | DEFAULT FALSE | 启用向量索引（Milvus） |
| `cache_ttl_seconds` | INT | DEFAULT 0 | 缓存 TTL |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

---

### 4.4 rel_object_ver_property - 对象版本-属性绑定

**用途**: 建立对象类型版本与公共属性的多对多关系，包含属性的使用配置。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | INT | PK, AUTO_INCREMENT | 自增主键 |
| `object_ver_id` | VARCHAR(36) | FK → meta_object_type_ver | 对象版本 ID |
| `property_def_id` | VARCHAR(36) | FK → meta_shared_property_def | 属性定义 ID |
| `local_api_name` | VARCHAR(100) | NULL | 本地别名（覆盖属性 api_name） |
| `is_primary_key` | BOOLEAN | DEFAULT FALSE | 是否主键 |
| `is_required` | BOOLEAN | DEFAULT FALSE | 是否必填 |
| `is_title` | BOOLEAN | DEFAULT FALSE | 是否作为对象标题显示 |
| `default_value` | TEXT | NULL | 默认值 |
| `validation_rules` | JSON | NULL | 验证规则 |
| `is_searchable` | BOOLEAN | DEFAULT FALSE | 启用全文搜索（ES text） |
| `is_filterable` | BOOLEAN | DEFAULT FALSE | 启用过滤聚合（ES keyword） |
| `is_sortable` | BOOLEAN | DEFAULT FALSE | 启用排序 |

**validation_rules 示例**:
```json
{
  "min": 0,
  "max": 100,
  "pattern": "^[A-Z]{2}[0-9]{4}$",
  "enum": ["ACTIVE", "INACTIVE", "PENDING"]
}
```

---

### 4.5 meta_link_type_def - 链接类型定义

**用途**: 定义对象间关系类型的不可变标识符。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `api_name` | VARCHAR(100) | UNIQUE, INDEX | API 名称 |
| `current_version_id` | VARCHAR(36) | NULL | 当前版本 ID |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

---

### 4.6 meta_link_type_ver - 链接类型版本

**用途**: 存储链接类型的具体配置（源/目标对象、基数等）。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `def_id` | VARCHAR(36) | FK → meta_link_type_def | 所属定义 |
| `version_number` | VARCHAR(50) | NOT NULL | 版本号 |
| `display_name` | VARCHAR(100) | NULL | 显示名称 |
| `source_object_def_id` | VARCHAR(36) | FK → meta_object_type_def | 源对象类型 |
| `target_object_def_id` | VARCHAR(36) | FK → meta_object_type_def | 目标对象类型 |
| `cardinality` | VARCHAR(50) | NOT NULL | 基数: ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY |
| `status` | VARCHAR(50) | DEFAULT 'DRAFT' | 状态 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

---

### 4.7 rel_link_ver_property - 链接版本-属性绑定

**用途**: 为链接类型绑定属性（关系可以有自己的属性）。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | INT | PK, AUTO_INCREMENT | 自增主键 |
| `link_ver_id` | VARCHAR(36) | FK → meta_link_type_ver | 链接版本 ID |
| `property_def_id` | VARCHAR(36) | FK → meta_shared_property_def | 属性定义 ID |
| `local_api_name` | VARCHAR(100) | NULL | 本地别名 |

---

### 4.8 meta_function_def - 函数定义

**用途**: 存储业务逻辑代码（Python/TypeScript/SQL）。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `api_name` | VARCHAR(100) | UNIQUE, INDEX | API 名称 |
| `display_name` | VARCHAR(200) | NOT NULL | 显示名称 |
| `description` | VARCHAR(500) | NULL | 函数描述 |
| `code_content` | TEXT | NULL | 代码内容 |
| `bound_object_type_id` | VARCHAR(36) | FK → meta_object_type | 绑定的对象类型（可选） |
| `input_params_schema` | JSON | NULL | 输入参数 Schema |
| `output_type` | VARCHAR(50) | DEFAULT 'VOID' | 返回类型: VOID, JSON, STRING, INT, BOOLEAN |

**input_params_schema 示例**:
```json
[
  {"name": "user_id", "type": "string", "required": true},
  {"name": "amount", "type": "number", "required": true, "default": 0},
  {"name": "notify", "type": "boolean", "required": false, "default": true}
]
```

---

### 4.9 meta_action_def - Action 定义

**用途**: 定义用户可触发的业务动作，绑定底层 Function。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `api_name` | VARCHAR(100) | UNIQUE, INDEX | API 名称 |
| `display_name` | VARCHAR(200) | NOT NULL | 显示名称 |
| `backing_function_id` | VARCHAR(36) | FK → meta_function_def | 绑定的函数 |

---

## 五、Context Layer（上下文层）

### 5.1 ctx_project_object_binding - 项目-对象绑定

**用途**: 定义项目中使用的对象类型及其版本，支持项目级别的显示别名。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `project_id` | VARCHAR(36) | PK, FK → sys_project | 项目 ID |
| `object_def_id` | VARCHAR(36) | PK, FK → meta_object_type_def | 对象类型 ID |
| `used_version_id` | VARCHAR(36) | FK → meta_object_type_ver | 使用的版本 |
| `project_display_alias` | VARCHAR(100) | NULL | 项目内显示别名 |
| `is_visible` | BOOLEAN | DEFAULT TRUE | 是否在项目中可见 |

**业务逻辑**: 项目可以选择使用对象类型的特定版本，并为其设置本地化显示名称。

---

### 5.2 ctx_object_mapping_def - 多模态映射定义

**用途**: 存储从原始数据到本体对象的映射规则（React Flow 格式）。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `object_def_id` | VARCHAR(36) | INDEX | 目标对象类型 |
| `source_connection_id` | VARCHAR(36) | NOT NULL | 源连接器 |
| `source_table_name` | VARCHAR(100) | NOT NULL | 源表名（mdp_raw_store） |
| `mapping_spec` | JSON | NOT NULL | 映射规则（React Flow nodes/edges） |
| `status` | VARCHAR(20) | DEFAULT 'DRAFT' | 状态: DRAFT, PUBLISHED, ARCHIVED |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |
| `updated_at` | DATETIME | DEFAULT NOW() | 更新时间 |

**mapping_spec 结构**:
```json
{
  "nodes": [
    {"id": "source", "type": "sourceColumn", "data": {"column": "user_name"}},
    {"id": "transform", "type": "transform", "data": {"operation": "UPPERCASE"}},
    {"id": "target", "type": "targetProperty", "data": {"property": "name"}}
  ],
  "edges": [
    {"source": "source", "target": "transform"},
    {"source": "transform", "target": "target"}
  ]
}
```

---

### 5.3 ctx_object_instance_lineage - 实例血缘追踪

**用途**: 记录对象实例的来源信息，支持从向量/实例反向追溯原始数据。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | VARCHAR(36) | PK | UUID 主键 |
| `object_def_id` | VARCHAR(36) | INDEX | 对象类型 |
| `instance_id` | VARCHAR(36) | INDEX | 实例 ID（也是 Milvus 向量 ID） |
| `mapping_id` | VARCHAR(36) | INDEX | 来源映射定义 |
| `source_table` | VARCHAR(100) | NOT NULL | 原始表名 |
| `source_row_id` | VARCHAR(100) | NOT NULL | 原始行 ID |
| `source_file_path` | VARCHAR(500) | NULL | 文件路径（非结构化数据） |
| `vector_collection` | VARCHAR(100) | NULL | Milvus 集合名 |
| `created_at` | DATETIME | DEFAULT NOW() | 创建时间 |

---

## 六、表关系总结

### 核心关系链

```
1. 项目 -> 对象绑定 -> 对象定义 -> 对象版本 -> 属性绑定 -> 公共属性
   sys_project -> ctx_project_object_binding -> meta_object_type_def 
              -> meta_object_type_ver -> rel_object_ver_property -> meta_shared_property_def

2. 连接器 -> 同步任务 -> 原始数据 -> 映射定义 -> 对象实例
   sys_connection -> sys_sync_job_def -> mdp_raw_store.* 
                  -> ctx_object_mapping_def -> ctx_object_instance_lineage

3. Action -> Function (执行流)
   meta_action_def -> meta_function_def -> (Python/TS 代码执行) -> sys_action_log
```

### 外键约束图

```
sys_project ─────────────────────┬────────────────────────────────┐
     │                           │                                │
     ▼                           ▼                                ▼
ctx_project_object_binding   sys_action_log            ctx_object_mapping_def
     │                                                            │
     ▼                                                            │
meta_object_type_def ◄────────────────────────────────────────────┘
     │
     ▼
meta_object_type_ver ◄─────── meta_link_type_ver
     │                              │
     ▼                              ▼
rel_object_ver_property      rel_link_ver_property
     │                              │
     └──────────────┬───────────────┘
                    ▼
          meta_shared_property_def

sys_connection
     │
     ├──────────────────────┐
     ▼                      ▼
sys_dataset           sys_sync_job_def
                            │
                            ▼
                      sys_sync_run_log

meta_function_def
     │
     ▼
meta_action_def
```

---

## 七、索引策略

### 主要索引

| 表 | 索引字段 | 类型 | 用途 |
|-----|----------|------|------|
| `meta_object_type_def` | `api_name` | UNIQUE | API 查询 |
| `meta_shared_property_def` | `api_name` | UNIQUE | API 查询 |
| `meta_link_type_def` | `api_name` | UNIQUE | API 查询 |
| `meta_function_def` | `api_name` | UNIQUE | API 查询 |
| `meta_action_def` | `api_name` | UNIQUE | API 查询 |
| `sys_action_log` | `project_id`, `created_at` | INDEX | 日志查询 |
| `sys_sync_job_def` | `connection_id` | INDEX | 连接器关联 |
| `ctx_object_instance_lineage` | `instance_id` | INDEX | 血缘追溯 |

---

## 八、版本演进策略

### Definition-Version 模式

```
                    ┌─────────────────────────────────────┐
                    │         meta_object_type_def        │
                    │   (不可变：ID + api_name)            │
                    └──────────────┬──────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
      ┌──────────┐          ┌──────────┐          ┌──────────┐
      │ Ver 1.0  │          │ Ver 2.0  │          │ Ver 3.0  │
      │  DRAFT   │          │PUBLISHED │          │DEPRECATED│
      └──────────┘          └──────────┘          └──────────┘
```

**优势**:
- 对象类型的 `api_name` 永远不变，代码引用稳定
- 版本化支持 A/B 测试、灰度发布
- 可追溯历史配置

---

## 九、扩展点

### 规划中的表

| 表名 | 用途 | 优先级 |
|------|------|--------|
| `meta_view_def` | 虚拟视图定义（基于对象的聚合查询） | 中 |
| `sys_schedule_job` | 通用调度任务配置 | 中 |
| `ctx_user_preference` | 用户偏好设置 | 低 |
| `audit_change_log` | 元数据变更审计 | 中 |

---

## 十、附录：完整建表脚本

```sql
-- 请参考 backend/seed_data_v3.sql 获取完整的建表和初始化脚本
```

---

*文档生成时间: 2026-01-23*
