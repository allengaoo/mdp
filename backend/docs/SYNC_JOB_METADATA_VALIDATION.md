# 同步任务元数据验证功能说明

## 概述

在创建同步任务时，系统会自动验证和检查相关元数据，确保数据一致性。

## 实现的功能

### 1. 表存在性验证

创建同步任务时，系统会检查 `target_table` 是否在 `mdp_raw_store` 数据库中已存在。

- **如果表不存在**：给出警告信息，但不会阻止创建（表会在首次同步时创建）
- **如果表已存在**：正常创建同步任务

### 2. 映射检查

系统会检查是否存在与该连接器关联的映射定义：

- **如果存在映射但表名不同**：返回警告信息，提示用户确认是否更新映射
- **如果不存在映射**：正常创建同步任务（映射在创建对象类型时关联）

### 3. 基于表结构自动生成 mapping_spec

提供了 `generate_mapping_spec_from_table()` 函数，可以根据表结构自动生成基础的映射配置：

- 为每个列创建源节点（sourceColumn）
- 为每个列创建目标节点（targetProperty，属性名待用户填写）
- 创建直接连接边（无转换逻辑）

## API 变更

### POST `/api/v3/sync-jobs`

**请求体**：`SyncJobDefCreate`（不变）

**响应体**：`SyncJobDefCreateResponse`（新增）

```json
{
  "job": {
    "id": "...",
    "connection_id": "...",
    "name": "...",
    "target_table": "...",
    ...
  },
  "warnings": {
    "mapping_exists": true,
    "mapping_table_mismatch": "raw_old_table_name",
    "table_exists": false
  }
}
```

**警告字段说明**：
- `mapping_exists`: 是否存在该连接器的映射
- `mapping_table_mismatch`: 如果存在映射但表名不同，返回现有映射的表名
- `table_exists`: 目标表是否已在 raw_store 中存在

## 新增函数

### mapping_crud.py

1. **`get_mapping_by_table()`**
   - 根据连接ID和表名查找映射

2. **`list_mappings_by_connection()`**
   - 列出指定连接器的所有映射

3. **`generate_mapping_spec_from_table()`**
   - 根据表结构生成基础 mapping_spec

4. **`update_mapping_table_name()`**
   - 更新映射的表名，并自动重新生成 mapping_spec

### sync_crud.py

1. **`check_table_exists_in_raw_store()`**
   - 检查表是否在 raw_store 中存在

2. **`create_sync_job()`**（修改）
   - 现在返回 `(SyncJobDef, warnings_dict)`
   - 自动执行验证和检查

## 使用流程

### 场景 1：创建新同步任务（无映射冲突）

```python
POST /api/v3/sync-jobs
{
  "connection_id": "conn_123",
  "name": "Sync users",
  "target_table": "raw_users",
  ...
}

# 响应
{
  "job": {...},
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

### 场景 2：创建同步任务（存在映射但表名不同）

```python
POST /api/v3/sync-jobs
{
  "connection_id": "conn_123",
  "name": "Sync users",
  "target_table": "raw_new_users",  # 新表名
  ...
}

# 响应
{
  "job": {...},
  "warnings": {
    "mapping_exists": true,
    "mapping_table_mismatch": "raw_old_users",  # 现有映射的表名
    "table_exists": false
  }
}
```

**前端处理**：
1. 检查 `warnings.mapping_table_mismatch` 是否存在
2. 如果存在，显示确认对话框：
   - "检测到现有映射使用表名 'raw_old_users'，是否更新为 'raw_new_users'？"
3. 用户确认后，调用 `PUT /api/v3/mappings/{mapping_id}` 更新映射

### 场景 3：更新映射表名

```python
PUT /api/v3/mappings/{mapping_id}
{
  "source_table_name": "raw_new_users"
}

# 系统会自动：
# 1. 更新 source_table_name
# 2. 根据新表结构重新生成 mapping_spec
# 3. 保留用户已配置的属性映射（如果可能）
```

## 注意事项

1. **表名验证**：表不存在不会阻止创建同步任务，因为表会在首次同步时创建
2. **映射更新**：更新映射表名时会重新生成 mapping_spec，用户需要重新配置属性映射
3. **事务一致性**：创建同步任务和检查映射在同一个数据库会话中，但不包含映射更新（映射更新需要用户确认）

## 后续优化建议

1. **智能映射保留**：更新表名时，尝试保留用户已配置的属性映射（通过列名匹配）
2. **批量检查**：提供 API 批量检查多个同步任务的映射状态
3. **自动修复建议**：当检测到不一致时，提供一键修复选项
