# 数据库备份说明

## 备份时间
在执行新schema之前，已保存以下备份文件：

## 备份文件

### 1. 原始Schema备份
- **文件**: `database_schema.sql`
- **内容**: 完整的数据库表结构定义（不包含数据）
- **包含表**: 
  - meta_project
  - meta_object_type
  - meta_link_type
  - meta_function_def
  - meta_action_def
  - meta_shared_property
  - sys_object_instance
  - sys_link_instance
  - sys_datasource_table
  - sys_action_log
  - meta_test_scenario

### 2. 原始示例数据备份
- **文件**: `database_sample_data.sql`
- **内容**: 所有表的示例数据
- **数据量**:
  - 1 个项目
  - 6 个共享属性
  - 12 个对象类型定义
  - 12 个关系类型定义
  - 12 个函数定义
  - 12 个动作定义
  - 60 个对象实例
  - 44 个关系实例
  - 5 个数据源表定义
  - 8 条动作执行日志
  - 4 个测试场景

## 新Schema信息

### 新架构特点
- 对标 Palantir Foundry 架构
- 数据存储在物理表中，而非JSON
- 包含兼容层（视图）以支持旧的前后端代码

### 新表结构
- **数据底座层**: `sys_dataset`, `sys_dataset_column`
- **本体定义层**: `ont_object_type`, `ont_shared_property_type`, `ont_object_property`, `ont_link_type`, `ont_link_rule`
- **逻辑层**: `logic_function_def`, `logic_action_def`
- **运行时层**: `sys_action_log`, `meta_test_scenario`
- **物理数据表**: `data_fighter`, `data_target`, `data_mission`, `link_mission_participation`
- **兼容视图**: `meta_project`, `meta_object_type`, `sys_object_instance`

## 恢复方法

如果需要恢复到旧的schema，可以执行：

```bash
# 1. 恢复表结构
mysql -u root -p ontology < database_schema.sql

# 2. 恢复示例数据
mysql -u root -p ontology < database_sample_data.sql
```

## 注意事项

1. 新schema已删除旧表并创建新表
2. 兼容视图确保旧代码可以继续工作
3. 新架构使用物理表存储数据，性能更好
4. 数据迁移需要手动进行（从JSON properties迁移到物理列）

