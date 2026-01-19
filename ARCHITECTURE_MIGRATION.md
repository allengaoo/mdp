# MDP 架构迁移指南

## 架构变更概述

从 **NoSQL JSON 存储** 迁移到 **Ontology-based 物理表架构**（对标 Palantir Foundry）

### 核心原则

1. **读取（GET）**: 使用兼容视图 `sys_object_instance` - 保持向后兼容
2. **写入（POST/PUT/DELETE）**: 写入物理表（如 `data_fighter`）- 需要 Writeback Layer
3. **前端兼容**: 继续返回 `properties: { key: value }` JSON 格式
4. **动态解析**: 通过 OntologyRepository 解析 `object_type_id` → `backing_dataset_id` → `storage_location`

## 新架构表结构

```
sys_dataset (数据源注册)
  └─> storage_location: "data_fighter"
      └─> ont_object_type.backing_dataset_id
          └─> ont_object_property (属性映射)
              └─> sys_dataset_column (物理列)
```

## 数据流

### 读取流程（兼容模式）
```
GET /api/v1/objects/fighter
  ↓
查询视图: sys_object_instance (WHERE object_type_id = 'obj-fighter')
  ↓
视图自动将物理表列转换为 JSON properties
  ↓
返回: { id, object_type_id, properties: { callsign, fuel, ... } }
```

### 写入流程（新架构）
```
POST /api/v1/objects/fighter
  ↓
接收: { properties: { callsign: "Ghost-3", fuel: 90 } }
  ↓
OntologyRepository.resolve_table('obj-fighter')
  ↓
解析: object_type_id → backing_dataset_id → storage_location = "data_fighter"
  ↓
获取属性映射: ont_object_property (callsign → col-f-call, fuel → col-f-fuel)
  ↓
动态构建 SQL: INSERT INTO data_fighter (id, callsign, fuel, ...) VALUES (...)
  ↓
执行写入物理表
  ↓
通过视图读取返回（保持兼容格式）
```

## 实现要点

### 1. OntologyRepository 职责

- **resolve_physical_table(object_type_id)**: 解析到物理表名
- **get_property_mappings(object_type_id)**: 获取属性到列的映射
- **serialize_to_physical_row(properties, mappings)**: JSON → 物理列
- **deserialize_from_physical_row(row, mappings)**: 物理列 → JSON（视图已处理）

### 2. Writeback Layer

所有写入操作必须：
1. 不直接操作 `sys_object_instance` 视图
2. 通过 OntologyRepository 解析目标表
3. 动态构建 SQL 插入/更新物理表
4. 返回时通过视图读取（保持兼容）

### 3. 兼容性保证

- 前端 API 接口不变
- 返回格式不变（`properties: {...}`）
- 视图自动处理序列化

## 迁移检查清单

- [ ] 实现 OntologyRepository
- [ ] 更新 instance_crud.py 的 create_object
- [ ] 更新 instance_crud.py 的 update_object
- [ ] 更新 instance_crud.py 的 delete_object
- [ ] 保持 list_objects 使用视图（兼容）
- [ ] 保持 get_object 使用视图（兼容）
- [ ] 测试 Fighter CRUD 操作
- [ ] 测试其他对象类型（Target, Mission）

