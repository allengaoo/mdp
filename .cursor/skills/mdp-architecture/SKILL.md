---
name: mdp-architecture
description: MDP 多模态本体构建平台的代码架构和业务逻辑指南。包含前后端代码结构、API 调用链、数据模型和业务流程。用于理解代码结构、定位功能实现、分析调用关系时使用。
---

# MDP 平台架构指南

## 项目概述

MDP（Metadata-Driven Platform）是一个多模态本体构建平台，支持：
- 数据连接器管理和数据同步
- 本体（Ontology）定义：对象类型、链接类型、属性
- 数据映射：将原始数据映射到本体对象
- 搜索和图谱分析

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React + TypeScript + Vite + Ant Design |
| 后端 | FastAPI + SQLModel + Python 3.11 |
| 数据库 | MySQL (ontology_meta_new, mdp_raw_store, ontology_raw_data) |
| 搜索 | Elasticsearch |
| 向量存储 | ChromaDB |

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite) | 3000 | 用户访问入口 |
| 后端 (FastAPI) | 8000 | API 服务 |
| Swagger UI | 8000/docs | API 文档 |

## 核心模块

### 前端模块

```
frontend/src/
├── api/                    # API 客户端
│   ├── axios.ts           # Axios 配置
│   ├── ontology.ts        # V1 API (兼容层)
│   └── v3/                # V3 API 客户端
│       ├── client.ts      # V3 axios 实例
│       ├── connectors.ts  # 连接器和同步任务 API
│       ├── ontology.ts    # 本体定义 API
│       └── types.ts       # 类型定义
├── platform/              # 业务页面
│   ├── DataLink/          # 数据连接模块
│   │   ├── ConnectorList.tsx    # 连接器列表
│   │   └── ConnectorDetail.tsx  # 连接器详情(含数据探索)
│   ├── Studio/            # 本体工作室
│   │   ├── ObjectTypeList.tsx   # 对象类型列表
│   │   ├── ObjectTypeEditor.tsx # 对象类型编辑器
│   │   ├── ObjectTypeWizard.tsx # 对象类型创建向导
│   │   ├── LinkTypeList.tsx     # 链接类型列表
│   │   └── SharedPropertyList.tsx # 共享属性列表
│   └── Explorer/          # 数据探索
│       └── Chat2App/      # 对话式应用
└── layouts/               # 布局组件
```

### 后端模块

```
backend/app/
├── api/v3/               # API 端点
│   ├── connectors.py     # 连接器和同步任务
│   ├── mapping.py        # 对象映射
│   ├── ontology.py       # 本体定义
│   ├── projects.py       # 项目管理
│   └── search.py         # 搜索服务
├── engine/               # 业务逻辑引擎
│   ├── v3/               # V3 CRUD 操作
│   │   ├── connector_crud.py  # 连接器 CRUD
│   │   ├── sync_crud.py       # 同步任务 CRUD
│   │   ├── mapping_crud.py    # 映射 CRUD
│   │   └── ontology_crud.py   # 本体 CRUD
│   └── sync_worker.py    # 同步执行引擎
├── models/               # 数据模型
│   ├── system.py         # 系统层 (Connection, SyncJobDef)
│   ├── context.py        # 上下文层 (ObjectMappingDef)
│   └── ontology.py       # 本体层 (ObjectTypeDef, LinkTypeDef)
├── core/                 # 核心配置
│   ├── config.py         # 配置管理
│   └── db.py             # 数据库连接
└── services/             # 服务层
```

## 数据库架构

### 数据库分层

| 数据库 | 用途 |
|--------|------|
| ontology_meta_new | 元数据存储（本体定义、映射配置）|
| mdp_raw_store | 原始数据存储（同步任务的目标表）|
| ontology_raw_data | 业务数据存储（最终数据目标）|

### 核心表

详见 [ARCHITECTURE.md](ARCHITECTURE.md) 中的数据模型部分。

## 关键业务流程

### 流程 1：数据同步

```
连接器管理 → 数据探索 → 创建同步任务 → 执行同步
```

详见 [BUSINESS-FLOWS.md](BUSINESS-FLOWS.md)

### 流程 2：对象类型创建

```
对象类型管理 → 新建向导 → 选择数据源 → 配置属性映射 → 创建
```

### 流程 3：数据映射

```
映射编辑器 → 配置源表到目标属性 → 保存映射规则
```

## 快速定位

### 常见功能定位

| 功能 | 前端文件 | 后端文件 |
|------|----------|----------|
| 连接器列表 | DataLink/ConnectorList.tsx | api/v3/connectors.py |
| 数据探索 | DataLink/ConnectorDetail.tsx (ExplorerTab) | engine/v3/connector_crud.py |
| 创建同步任务 | DataLink/ConnectorDetail.tsx | engine/v3/sync_crud.py |
| 执行同步 | - | engine/sync_worker.py |
| 对象类型列表 | Studio/ObjectTypeList.tsx | api/v3/ontology.py |
| 对象类型创建 | Studio/ObjectTypeWizard.tsx | engine/v3/ontology_crud.py |
| 对象类型编辑 | Studio/ObjectTypeEditor.tsx | engine/v3/ontology_crud.py |

## 详细参考

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细架构和数据模型
- [BUSINESS-FLOWS.md](BUSINESS-FLOWS.md) - 业务流程和调用链
- [API-REFERENCE.md](API-REFERENCE.md) - API 端点参考
