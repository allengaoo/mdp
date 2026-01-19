# 数据库 Schema 关联关系文档

## 架构概述

本系统采用**双层架构设计**：
1. **新架构层（底层）**：对标 Palantir Foundry，使用物理表存储数据
2. **兼容视图层（上层）**：为旧的前后端代码提供兼容接口

---

## 一、数据底座层 (Data Foundation Layer)

### 1.1 `sys_dataset` - 数据集注册表
**作用**：注册所有物理数据存储位置

```sql
sys_dataset
├── id (PK)
├── api_name (UK)          -- 数据集 API 名称
├── display_name           -- 显示名称
├── storage_type           -- 存储类型 (MYSQL_TABLE, VIRTUAL, etc.)
└── storage_location       -- 物理表名 (如 'data_fighter')
```

**关联关系**：
- `sys_dataset.id` ← `ont_object_type.backing_dataset_id` (1:N)
- `sys_dataset.id` ← `sys_dataset_column.dataset_id` (1:N)

### 1.2 `sys_dataset_column` - 数据集列定义
**作用**：定义物理表的列结构

```sql
sys_dataset_column
├── id (PK)
├── dataset_id (FK → sys_dataset.id)
├── column_name            -- 物理列名
├── physical_type          -- 数据类型 (VARCHAR, INT, etc.)
└── is_primary_key         -- 是否主键
```

**关联关系**：
- `sys_dataset_column.dataset_id` → `sys_dataset.id` (N:1)
- `sys_dataset_column.id` ← `ont_object_property.mapped_column_id` (1:N)

---

## 二、本体定义层 (Ontology Definition Layer)

### 2.1 `ont_object_type` - 对象类型定义
**作用**：定义业务对象类型（如 Fighter, Mission, Target）

```sql
ont_object_type
├── id (PK)                -- 如 'obj-fighter'
├── api_name (UK)          -- 如 'fighter'
├── display_name           -- 如 'Fighter Jet'
├── description
├── backing_dataset_id (FK → sys_dataset.id)  -- 关联到物理数据集
├── title_property_id      -- 标题属性ID（可选）
└── created_at
```

**关联关系**：
- `ont_object_type.backing_dataset_id` → `sys_dataset.id` (N:1)
- `ont_object_type.id` ← `ont_object_property.object_type_id` (1:N)
- `ont_object_type.id` ← `ont_link_type.source_object_type_id` (1:N)
- `ont_object_type.id` ← `ont_link_type.target_object_type_id` (1:N)

### 2.2 `ont_shared_property_type` - 共享属性类型
**作用**：定义跨对象类型共享的属性格式（如坐标、时间戳）

```sql
ont_shared_property_type
├── id (PK)
├── api_name (UK)          -- 如 'location', 'timestamp'
├── display_name           -- 如 'Location'
├── data_type             -- 数据类型
└── formatter             -- 格式化规则（可选）
```

**关联关系**：
- `ont_shared_property_type.id` ← `ont_object_property.shared_type_id` (1:N)

### 2.3 `ont_object_property` - 对象属性映射
**作用**：将逻辑属性映射到物理列（核心映射层）

```sql
ont_object_property
├── id (PK)
├── object_type_id (FK → ont_object_type.id)
├── api_name               -- 逻辑属性名 (如 'callsign')
├── display_name           -- 显示名称
├── mapped_column_id (FK → sys_dataset_column.id)  -- 映射到物理列
├── shared_type_id (FK → ont_shared_property_type.id)  -- 可选：共享类型
└── is_primary_key         -- 是否主键属性
```

**关联关系**：
- `ont_object_property.object_type_id` → `ont_object_type.id` (N:1)
- `ont_object_property.mapped_column_id` → `sys_dataset_column.id` (N:1)
- `ont_object_property.shared_type_id` → `ont_shared_property_type.id` (N:1)

**映射示例**：
```
逻辑层: ont_object_property.api_name = 'callsign'
   ↓
物理层: sys_dataset_column.column_name = 'callsign'
   ↓
数据层: data_fighter.callsign = 'Ghost-1'
```

### 2.4 `ont_link_type` - 链接类型定义
**作用**：定义对象之间的关联关系类型

```sql
ont_link_type
├── id (PK)                -- 如 'link-part'
├── api_name (UK)          -- 如 'participation'
├── display_name           -- 如 'Participates In'
├── source_object_type_id  -- 源对象类型ID
├── target_object_type_id  -- 目标对象类型ID
└── cardinality            -- 基数 (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY)
```

**关联关系**：
- `ont_link_type.source_object_type_id` → `ont_object_type.id` (N:1)
- `ont_link_type.target_object_type_id` → `ont_object_type.id` (N:1)
- `ont_link_type.id` ← `ont_link_rule.link_type_id` (1:N)

### 2.5 `ont_link_rule` - 链接规则
**作用**：定义如何从物理表构建链接关系

```sql
ont_link_rule
├── id (PK)
├── link_type_id (FK → ont_link_type.id)
├── rule_type              -- 规则类型 (FOREIGN_KEY, JOIN_TABLE)
├── source_column_id       -- 源列ID（外键场景）
├── target_column_id       -- 目标列ID（外键场景）
└── join_table_name        -- 连接表名（多对多场景，如 'link_mission_participation'）
```

**关联关系**：
- `ont_link_rule.link_type_id` → `ont_link_type.id` (N:1)

---

## 三、逻辑与运行时层 (Logic & Runtime Layer)

### 3.1 函数定义表

**新架构表：`logic_function_def`**
```sql
logic_function_def
├── id (PK)
├── api_name (UK)          -- 函数 API 名称
├── code_content           -- Python 代码内容
├── input_schema           -- 输入参数 Schema (JSON)
└── output_type            -- 输出类型
```

**旧架构表：`meta_function_def`**（兼容保留）
```sql
meta_function_def
├── id (PK)
├── api_name (UK)          -- 函数 API 名称
├── display_name           -- 显示名称
├── code_content           -- Python 代码内容
├── bound_object_type_id   -- 绑定的对象类型ID（可选）
├── description            -- 描述
├── input_params_schema    -- 输入参数 Schema (JSON)
└── output_type            -- 输出类型
```

**关联关系**：
- `logic_function_def.id` ← `logic_action_def.backing_function_id` (1:N)
- `meta_function_def.id` ← `meta_action_def.backing_function_id` (1:N)

### 3.2 动作定义表

**新架构表：`logic_action_def`**
```sql
logic_action_def
├── id (PK)
├── api_name (UK)          -- 动作 API 名称
└── backing_function_id (FK → logic_function_def.id)  -- 关联的函数
```

**旧架构表：`meta_action_def`**（兼容保留）
```sql
meta_action_def
├── id (PK)
├── api_name (UK)          -- 动作 API 名称
├── display_name           -- 显示名称
└── backing_function_id (FK → meta_function_def.id)  -- 关联的函数
```

**关联关系**：
- `logic_action_def.backing_function_id` → `logic_function_def.id` (N:1)
- `meta_action_def.backing_function_id` → `meta_function_def.id` (N:1)
- `logic_action_def.id` ← `sys_action_log.action_def_id` (1:N)
- `meta_action_def.id` ← `sys_action_log.action_def_id` (1:N)

**注意**：系统同时支持新旧两套表，代码会自动检测并使用存在的表。

### 3.3 `sys_action_log` - 动作执行日志
**作用**：记录动作执行历史

```sql
sys_action_log
├── id (PK)
├── action_def_id (FK → logic_action_def.id)
├── project_id             -- 项目ID（兼容字段）
├── source_object_id       -- 触发对象ID
├── execution_status       -- 执行状态 (SUCCESS, FAILED)
├── duration_ms            -- 执行时长（毫秒）
├── error_message          -- 错误信息
├── request_params         -- 请求参数 (JSON)
└── created_at             -- 创建时间
```

**关联关系**：
- `sys_action_log.action_def_id` → `logic_action_def.id` (N:1)

---

## 四、物理数据存储层 (Physical Data Storage)

### 4.1 物理表示例

**`data_fighter`** - 战斗机数据表
```sql
data_fighter
├── id (PK)
├── callsign
├── fuel
├── status
├── lat
├── lon
├── altitude
├── squadron_id
└── base_id
```

**`data_target`** - 目标数据表
```sql
data_target
├── id (PK)
├── name
├── threat_level
├── type
├── priority
├── lat
└── lon
```

**`data_mission`** - 任务数据表
```sql
data_mission
├── id (PK)
├── name
├── type
├── status
├── priority
├── start_time
└── end_time
```

**`link_mission_participation`** - 任务参与关系表（多对多）
```sql
link_mission_participation
├── mission_id (PK, FK → data_mission.id)
├── fighter_id (PK, FK → data_fighter.id)
└── role
```

---

## 五、兼容视图层 (Compatibility Views)

### 5.1 `meta_project` - 项目视图（兼容）
**作用**：为旧代码提供项目接口

```sql
CREATE VIEW meta_project AS
SELECT 'proj-default' as id, 'Battlefield System' as name, ...
```

### 5.2 `meta_object_type` - 对象类型视图（兼容）
**作用**：将新架构映射回旧格式

```sql
CREATE VIEW meta_object_type AS
SELECT 
    t.id,
    t.api_name,
    t.display_name,
    t.description,
    'proj-default' as project_id,
    t.created_at,
    NOW() as updated_at,
    -- 动态构建 property_schema JSON
    (SELECT JSON_OBJECTAGG(p.api_name, 'string')
     FROM ont_object_property p 
     WHERE p.object_type_id = t.id) as property_schema
FROM ont_object_type t;
```

**映射关系**：
- `meta_object_type` (视图) ← `ont_object_type` (表)

### 5.3 `meta_link_type` - 链接类型视图（兼容）
**作用**：将新架构的链接类型映射到旧格式

```sql
CREATE VIEW meta_link_type AS
SELECT 
    id,
    api_name,
    display_name,
    source_object_type_id as source_type_id,  -- 字段名映射
    target_object_type_id as target_type_id,  -- 字段名映射
    cardinality,
    NOW() as created_at,
    NOW() as updated_at
FROM ont_link_type;
```

**映射关系**：
- `meta_link_type` (视图) ← `ont_link_type` (表)

### 5.4 `sys_object_instance` - 对象实例视图（兼容）
**作用**：将所有物理表聚合为统一的 JSON 格式视图

```sql
CREATE VIEW sys_object_instance AS
SELECT 
    id, 
    'obj-fighter' as object_type_id, 
    JSON_OBJECT(
        'callsign', callsign, 
        'fuel', fuel, 
        'status', status, 
        'lat', lat, 
        'lon', lon
    ) as properties,
    NOW() as created_at,
    NOW() as updated_at
FROM data_fighter
UNION ALL
SELECT ... FROM data_target
UNION ALL
SELECT ... FROM data_mission;
```

**映射关系**：
- `sys_object_instance` (视图) ← `data_fighter`, `data_target`, `data_mission` (表)

### 5.5 `sys_datasource_table` - 数据源视图（兼容）
**作用**：将新架构的数据集映射到旧格式

```sql
CREATE VIEW sys_datasource_table AS
SELECT 
    ds.id,
    ds.storage_location as table_name,
    'MySQL' as db_type,
    -- 聚合列定义
    (SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'name', dc.column_name,
            'type', dc.physical_type,
            'is_primary_key', dc.is_primary_key
        )
     )
     FROM sys_dataset_column dc
     WHERE dc.dataset_id = ds.id) as columns_schema,
    NOW() as created_at
FROM sys_dataset ds
WHERE ds.storage_type = 'MYSQL_TABLE';
```

**映射关系**：
- `sys_datasource_table` (视图) ← `sys_dataset` + `sys_dataset_column` (表)

### 5.6 `meta_shared_property` - 共享属性视图（兼容）
**作用**：将新架构的共享属性类型映射到旧格式

**注意**：`meta_shared_property` 可能是表或视图，取决于架构版本。

**映射关系**（如果存在视图）：
- `meta_shared_property` (视图) ← `ont_shared_property_type` (表)

---

## 六、完整关联关系图

```
┌─────────────────────────────────────────────────────────────┐
│                    数据底座层                                │
├─────────────────────────────────────────────────────────────┤
│  sys_dataset ──┐                                            │
│                ├──→ sys_dataset_column                      │
└────────────────┴────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  本体定义层                                  │
├─────────────────────────────────────────────────────────────┤
│  ont_object_type ──┐                                        │
│                    ├──→ ont_object_property ──┐             │
│                    │                          ├──→ sys_dataset_column
│                    │                          └──→ ont_shared_property_type
│                    │                                        │
│                    ├──→ ont_link_type ──→ ont_link_rule    │
│                    └──→ ont_link_type (target)              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  逻辑与运行时层                              │
├─────────────────────────────────────────────────────────────┤
│  logic_function_def ──→ logic_action_def ──→ sys_action_log│
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  物理数据存储层                              │
├─────────────────────────────────────────────────────────────┤
│  data_fighter                                               │
│  data_target                                                │
│  data_mission                                               │
│  link_mission_participation                                │
└─────────────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────────────┐
│                  兼容视图层                                  │
├─────────────────────────────────────────────────────────────┤
│  meta_project (视图)                                        │
│  meta_object_type (视图) ← ont_object_type                  │
│  meta_link_type (视图) ← ont_link_type                      │
│  sys_object_instance (视图) ← data_* 表                     │
│  sys_datasource_table (视图) ← sys_dataset                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、关键映射流程

### 7.1 对象类型到物理表的映射

```
1. 查询对象类型
   ont_object_type.id = 'obj-fighter'
   
2. 获取数据集
   ont_object_type.backing_dataset_id → sys_dataset.id
   sys_dataset.storage_location = 'data_fighter'
   
3. 获取属性映射
   ont_object_property.object_type_id = 'obj-fighter'
   ont_object_property.mapped_column_id → sys_dataset_column.id
   sys_dataset_column.column_name = 'callsign'
   
4. 读写物理表
   INSERT INTO data_fighter (id, callsign, fuel, ...) VALUES (...)
```

### 7.2 视图到物理表的映射（读取）

```
1. 查询视图
   SELECT * FROM sys_object_instance WHERE id = 'xxx'
   
2. 视图自动聚合
   sys_object_instance (视图) 
   → UNION ALL 所有 data_* 表
   → JSON_OBJECT 将列转换为 JSON properties
   
3. 返回统一格式
   {
     "id": "...",
     "object_type_id": "obj-fighter",
     "properties": {"callsign": "Ghost-1", "fuel": 90, ...}
   }
```

### 7.3 链接关系的映射

```
1. 定义链接类型
   ont_link_type.api_name = 'participation'
   ont_link_type.source_object_type_id = 'obj-fighter'
   ont_link_type.target_object_type_id = 'obj-mission'
   
2. 定义链接规则
   ont_link_rule.link_type_id = 'link-part'
   ont_link_rule.rule_type = 'JOIN_TABLE'
   ont_link_rule.join_table_name = 'link_mission_participation'
   
3. 查询链接
   SELECT * FROM link_mission_participation
   WHERE fighter_id = 'xxx'
```

---

## 八、数据流向

### 写入流程（新架构）
```
应用层
  ↓
OntologyRepository.resolve_physical_table()
  ↓
ont_object_type → sys_dataset → storage_location
  ↓
instance_crud.create_object()
  ↓
INSERT INTO data_fighter (...)
```

### 读取流程（兼容视图）
```
应用层
  ↓
SELECT * FROM sys_object_instance WHERE ...
  ↓
视图自动 UNION ALL 所有 data_* 表
  ↓
JSON_OBJECT 序列化
  ↓
返回统一 JSON 格式
```

---

## 九、关键设计原则

1. **读写分离**：
   - **写操作**：直接操作物理表（`data_fighter`, `data_target` 等）
   - **读操作**：通过兼容视图（`sys_object_instance`）统一读取

2. **映射层设计**：
   - `ont_object_property` 是核心映射层
   - 将逻辑属性（`api_name`）映射到物理列（`mapped_column_id`）

3. **兼容性保证**：
   - 所有旧代码通过视图访问数据
   - 新代码可以直接操作物理表，性能更好

4. **扩展性**：
   - 新增对象类型只需：
     1. 创建物理表（如 `data_new_type`）
     2. 注册到 `sys_dataset`
     3. 定义 `ont_object_type`
     4. 映射 `ont_object_property`
     5. 更新 `sys_object_instance` 视图

---

## 十、注意事项

1. **视图更新**：新增对象类型后，需要手动更新 `sys_object_instance` 视图
2. **外键约束**：新架构使用软关联，不强制外键约束
3. **数据一致性**：物理表和视图需要保持同步
4. **性能考虑**：大量 UNION ALL 可能影响视图查询性能，建议直接查询物理表
