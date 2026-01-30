# 同步任务元数据验证功能 - 测试总结

## ✅ 实现完成

所有功能已实现并通过代码检查：

1. ✅ 表存在性验证
2. ✅ 映射检查与警告
3. ✅ 基于表结构自动生成 mapping_spec
4. ✅ API 响应增强（包含警告信息）

## 🧪 测试方法

### 快速测试（推荐）

1. **启动后端服务**（如果未运行）：
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 3000
   ```

2. **访问 Swagger UI**：
   打开浏览器访问：`http://localhost:3000/docs`

3. **测试创建同步任务**：
   - 找到 `POST /api/v3/sync-jobs` 端点
   - 点击 "Try it out"
   - 填写请求体（需要替换真实的 connection_id）：
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
   - 点击 "Execute"
   - 查看响应中的 `warnings` 字段

### 使用 curl 测试

```bash
# 获取连接ID（先执行）
curl http://localhost:3000/api/v3/connectors

# 创建同步任务（替换 YOUR_CONNECTION_ID）
curl -X POST "http://localhost:3000/api/v3/sync-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "name": "测试同步任务",
    "source_config": {"table": "test_table"},
    "target_table": "raw_test_table_123",
    "sync_mode": "FULL_OVERWRITE",
    "is_enabled": true
  }'
```

### 预期响应格式

```json
{
  "job": {
    "id": "uuid",
    "connection_id": "...",
    "name": "测试同步任务",
    "target_table": "raw_test_table_123",
    ...
  },
  "warnings": {
    "mapping_exists": false,
    "mapping_table_mismatch": null,
    "table_exists": false
  }
}
```

## 📋 测试检查清单

- [ ] API 返回状态码 201
- [ ] 响应包含 `job` 字段
- [ ] 响应包含 `warnings` 字段
- [ ] `warnings.mapping_exists` 正确反映映射状态
- [ ] `warnings.table_exists` 正确反映表存在状态
- [ ] 如果存在映射但表名不同，`warnings.mapping_table_mismatch` 返回现有映射的表名
- [ ] 后端日志显示相应的警告信息

## 🔍 验证映射表名不匹配场景

1. **创建映射**（使用旧表名）：
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

2. **创建同步任务**（使用新表名）：
   ```bash
   curl -X POST "http://localhost:3000/api/v3/sync-jobs" \
     -H "Content-Type: application/json" \
     -d '{
       "connection_id": "YOUR_CONNECTION_ID",
       "name": "测试同步任务",
       "source_config": {"table": "test_table"},
       "target_table": "raw_new_table",
       "sync_mode": "FULL_OVERWRITE",
       "is_enabled": true
     }'
   ```

3. **验证响应**：
   - `warnings.mapping_exists` 应该为 `true`
   - `warnings.mapping_table_mismatch` 应该为 `"raw_old_table"`

## 📝 代码文件

- `backend/app/engine/v3/sync_crud.py` - 同步任务 CRUD 和验证逻辑
- `backend/app/engine/v3/mapping_crud.py` - 映射 CRUD 和生成逻辑
- `backend/app/api/v3/connectors.py` - API 端点
- `backend/app/models/system.py` - 响应模型

## 📚 文档

- `backend/docs/SYNC_JOB_METADATA_VALIDATION.md` - 功能说明
- `backend/TEST_SYNC_JOB_API.md` - 详细测试指南

## ⚠️ 注意事项

1. 确保数据库连接正常
2. 确保至少有一个连接器存在
3. 表不存在不会阻止创建同步任务（表会在首次同步时创建）
4. 如果检测到映射表名不匹配，前端应该显示确认对话框

## 🚀 下一步

测试通过后，可以：
1. 在前端集成警告处理逻辑
2. 实现映射表名更新功能
3. 添加更多验证规则
