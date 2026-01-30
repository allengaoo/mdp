# 同步任务元数据验证功能测试指南

## 前置条件

1. 确保后端服务运行在 `http://localhost:3000`
2. 确保数据库连接正常
3. 至少有一个连接器（Connector）存在

## 测试方法

### 方法1：使用 curl 命令

#### 测试场景1：创建新同步任务（无映射冲突）

```bash
curl -X POST "http://localhost:3000/api/v3/sync-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "name": "测试同步任务1",
    "source_config": {"table": "test_table"},
    "target_table": "raw_test_table_1",
    "sync_mode": "FULL_OVERWRITE",
    "is_enabled": true
  }'
```

**预期响应**：
```json
{
  "job": {
    "id": "...",
    "connection_id": "...",
    "name": "测试同步任务1",
    "target_table": "raw_test_table_1",
    ...
  },
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

#### 测试场景2：创建同步任务（存在映射但表名不同）

**步骤1：先创建一个映射**
```bash
curl -X POST "http://localhost:3000/api/v3/mappings" \
  -H "Content-Type: application/json" \
  -d '{
    "object_def_id": "YOUR_OBJECT_DEF_ID",
    "source_connection_id": "YOUR_CONNECTION_ID",
    "source_table_name": "raw_old_table",
    "mapping_spec": {"nodes": [], "edges": []}
  }'
```

**步骤2：创建同步任务（使用不同的表名）**
```bash
curl -X POST "http://localhost:3000/api/v3/sync-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "name": "测试同步任务2",
    "source_config": {"table": "test_table"},
    "target_table": "raw_new_table",
    "sync_mode": "FULL_OVERWRITE",
    "is_enabled": true
  }'
```

**预期响应**：
```json
{
  "job": {
    "id": "...",
    "name": "测试同步任务2",
    "target_table": "raw_new_table",
    ...
  },
  "warnings": {
    "mapping_exists": true,
    "mapping_table_mismatch": "raw_old_table",
    "table_exists": false
  }
}
```

**⚠️ 注意**：`warnings.mapping_table_mismatch` 字段会显示现有映射的表名，提示用户需要更新映射。

#### 测试场景3：验证表存在性检查

```bash
curl -X POST "http://localhost:3000/api/v3/sync-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "name": "测试同步任务3",
    "source_config": {"table": "test_table"},
    "target_table": "raw_nonexistent_table_12345",
    "sync_mode": "FULL_OVERWRITE",
    "is_enabled": true
  }'
```

**预期响应**：
```json
{
  "job": {...},
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

**说明**：`table_exists: false` 表示表不存在，这是正常的，表会在首次同步时创建。

### 方法2：使用 Python requests

运行测试脚本：
```bash
cd backend
python test_sync_job_simple.py
```

### 方法3：使用 Postman 或 Swagger UI

1. 访问 `http://localhost:3000/docs` 打开 Swagger UI
2. 找到 `POST /api/v3/sync-jobs` 端点
3. 点击 "Try it out"
4. 填写请求体：
```json
{
  "connection_id": "YOUR_CONNECTION_ID",
  "name": "测试同步任务",
  "source_config": {"table": "test_table"},
  "target_table": "raw_test_table",
  "sync_mode": "FULL_OVERWRITE",
  "is_enabled": true
}
```
5. 点击 "Execute"
6. 查看响应中的 `warnings` 字段

## 验证要点

### ✅ 成功标准

1. **API 响应状态码为 201**
2. **响应包含 `job` 和 `warnings` 字段**
3. **警告信息正确**：
   - `mapping_exists`: 正确反映是否存在映射
   - `mapping_table_mismatch`: 如果存在映射但表名不同，返回现有映射的表名
   - `table_exists`: 正确反映表是否存在

### 🔍 检查项

1. **日志输出**：检查后端日志，应该看到：
   - `[SyncJob] Created job: ...`
   - 如果有映射不匹配，应该看到 `[SyncJob] Found existing mapping with different table name: ...`

2. **数据库验证**：
   - 检查 `sys_sync_job_def` 表，确认同步任务已创建
   - 检查 `ctx_object_mapping_def` 表，确认映射信息

3. **警告处理**：
   - 如果 `mapping_table_mismatch` 不为 null，前端应该显示确认对话框
   - 用户确认后，调用 `PUT /api/v3/mappings/{mapping_id}` 更新映射

## 常见问题

### Q1: 连接器不存在
**错误**：`Connection not found: ...`
**解决**：先创建连接器，或使用已存在的连接器ID

### Q2: 服务未运行
**错误**：连接超时或连接被拒绝
**解决**：启动后端服务
```bash
cd backend
uvicorn app.main:app --reload --port 3000
```

### Q3: 数据库连接失败
**错误**：数据库相关错误
**解决**：检查 `.env` 文件中的数据库配置

## 下一步

测试通过后，可以：
1. 在前端集成警告处理逻辑
2. 实现映射表名更新功能
3. 添加更多验证规则
