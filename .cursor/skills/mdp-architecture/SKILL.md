---
name: mdp-architecture
description: MDP 多模态本体构建平台的代码架构和业务逻辑指南。包含前后端代码结构、API 调用链、数据模型和业务流程。用于理解代码结构、定位功能实现、分析调用关系时使用。
---

# MDP 平台架构指南

## 项目概述

MDP（Metadata-Driven Platform）是一个多模态本体构建平台，是 CEC-AIOS 的核心模块。遵循"全局资产一致性 (Global Consistency) + 场景化敏捷应用 (Scenario Agility)"的双层设计原则。

### 核心能力

| 能力 | 说明 |
|------|------|
| 数据连接与同步 | 支持 MySQL、PostgreSQL、S3、Kafka、REST API 等数据源的连接和数据同步 |
| 本体建模 | 对象类型、链接类型、共享属性的版本化定义与管理 |
| 多模态映射 | 可视化画布配置原始数据到本体对象的映射规则 |
| Triple Write 索引 | 同时写入 MySQL、Elasticsearch、ChromaDB 三存储 |
| 混合搜索 | 支持全文搜索 + 向量搜索的混合检索 |
| 图分析 | 基于链接关系的图扩展和最短路径分析 |
| 代码执行沙箱 | 隔离的代码执行环境，支持 builtin、subprocess、remote 三种模式 |
| Chat2App | 自然语言查询转 AMIS Schema 渲染 |

## 核心文档索引

- [Ontology Concepts](./ONTOLOGY_CONCEPTS.md): **[必读]** 详细介绍了基于 Palantir 理念的本体论核心概念，包括对象、链接（1:1, 1:N, M:N 实现机制）、行为与函数的关系。
- [Architecture Detail](./ARCHITECTURE.md): 详细的代码架构、文件职责、数据模型和 API 映射。
- [Business Flows](./BUSINESS-FLOWS.md): 关键业务流程的调用链分析（Frontend -> API -> Engine -> DB）。
- [API Reference](./API-REFERENCE.md): API 端点参考手册。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React + TypeScript + Vite + Ant Design + ReactFlow |
| 后端 | FastAPI + SQLModel + Python 3.11 |
| 元数据库 | MySQL (ontology_meta_new) |
| 原始数据库 | MySQL (mdp_raw_store) |
| 业务数据库 | MySQL (ontology_raw_data) |
| 全文搜索 | Elasticsearch |
| 向量存储 | ChromaDB |
| LLM 服务 | Ollama |
| 代码沙箱 | 独立 FastAPI 微服务 |
| 容器编排 | Kubernetes |

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite) | 3000 | 用户访问入口，代理 /api 到后端 |
| 后端 (FastAPI) | 8000 | API 服务 |
| 沙箱 (Sandbox) | 8001 | 代码执行沙箱服务 |
| Swagger UI | 8000/docs | API 文档 |

## 架构分层

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (React)                              │
├─────────────────────────────────────────────────────────────────┤
│  Studio      │  OMA        │  Explorer    │  DataLink          │
│  本体建模     │  对象中心    │  数据探索     │  数据连接           │
├─────────────────────────────────────────────────────────────────┤
│                     API 层 (v1 兼容 / v3)                        │
├─────────────────────────────────────────────────────────────────┤
│                        后端 (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│  API 端点    │  Engine 层   │  Models 层   │  Core 层           │
│  路由定义     │  业务逻辑     │  数据模型     │  基础设施           │
├─────────────────────────────────────────────────────────────────┤
│                       数据存储层                                  │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│ MySQL        │ Elasticsearch│ ChromaDB     │ Ollama            │
│ 结构化数据    │ 全文搜索      │ 向量搜索      │ LLM 推理           │
└──────────────┴──────────────┴──────────────┴───────────────────┘
        │
        ▼
┌──────────────────────┐
│  Sandbox 沙箱服务     │
│  (K8s Pod / 端口 8001) │
│  隔离代码执行环境      │
└──────────────────────┘
```

## 数据库分层

| 数据库 | 用途 | 主要表 |
|--------|------|--------|
| ontology_meta_new | 元数据存储 | meta_object_type_def, meta_object_type_ver, sys_connection, sys_sync_job_def |
| mdp_raw_store | 原始数据存储 | 同步任务的目标表（动态创建）|
| ontology_raw_data | 业务数据存储 | 从 raw_store 复制的最终数据 |

## V3 架构核心概念

### 对象类型的版本化设计

```
ObjectTypeDef (定义)
    │
    ├── ObjectTypeVer (版本 v1.0)
    │       └── ObjectVerProperty (属性绑定)
    │               ├── 引用 SharedPropertyDef (共享属性)
    │               └── 或存储 local_* 字段 (本地属性)
    │
    └── ObjectTypeVer (版本 v1.1)
            └── ObjectVerProperty (属性绑定)
```

### 项目绑定设计

```
Project (项目/场景)
    │
    └── ProjectObjectBinding (项目-对象绑定)
            ├── object_def_id → ObjectTypeDef
            ├── used_version_id → ObjectTypeVer
            └── local_alias (本地别名)
```

## 前端模块结构

```
frontend/src/
├── api/                    # API 客户端
│   ├── axios.ts           # V1 Axios 配置 (baseURL: /api/v1)
│   ├── ontology.ts        # V1 API (内部转发 V3)
│   └── v3/                # V3 API 客户端
│       ├── client.ts      # V3 axios 实例 (baseURL: /api/v3)
│       ├── connectors.ts  # 连接器和同步任务
│       ├── ontology.ts    # 本体定义
│       ├── objects.ts     # 对象统计
│       ├── search.ts      # 全局搜索
│       ├── graph.ts       # 图分析
│       ├── mapping.ts     # 多模态映射
│       ├── health.ts      # 索引健康
│       ├── chat.ts        # Chat2App
│       └── types.ts       # 类型定义
├── platform/              # 业务页面
│   ├── Studio/            # 本体工作室
│   │   ├── ObjectTypeList.tsx
│   │   ├── ObjectTypeEditor.tsx
│   │   ├── ObjectTypeWizard.tsx
│   │   ├── LinkTypeList.tsx
│   │   ├── FunctionList.tsx
│   │   ├── FunctionEditor.tsx
│   │   ├── TopologyView.tsx
│   │   └── ...
│   ├── OMA/               # 对象管理
│   │   ├── ObjectCenter.tsx
│   │   ├── OntologyLibrary.tsx
│   │   └── ...
│   ├── Explorer/          # 数据探索
│   │   ├── GlobalSearchPage.tsx
│   │   ├── Chat2App/
│   │   ├── Object360/
│   │   ├── GraphAnalysis/
│   │   └── ...
│   └── DataLink/          # 数据连接
│       ├── ConnectorList.tsx
│       ├── ConnectorDetail.tsx
│       ├── IndexHealth/
│       └── MultimodalMapping/
└── layouts/               # 布局组件
```

## 后端模块结构

```
backend/app/
├── api/                   # API 端点
│   ├── v1/               # V1 兼容层
│   │   ├── ontology.py   # 本体 CRUD
│   │   └── execute.py    # 执行 API
│   └── v3/               # V3 主 API
│       ├── ontology.py   # 本体定义
│       ├── connectors.py # 连接器和同步
│       ├── mapping.py    # 映射管理
│       ├── execute.py    # 代码执行 (支持 remote)
│       ├── projects.py   # 项目管理
│       ├── search.py     # 搜索服务
│       ├── graph.py      # 图分析
│       ├── chat.py       # Chat2App
│       └── health.py     # 健康监控
├── engine/               # 业务逻辑引擎
│   ├── meta_crud.py      # 元数据 CRUD (兼容层)
│   ├── code_executor.py  # 代码执行调度器 (builtin/subprocess/remote)
│   ├── v3/               # V3 CRUD 操作
│   │   ├── ontology_crud.py
│   │   ├── connector_crud.py
│   │   ├── sync_crud.py
│   │   ├── mapping_crud.py
│   │   ├── project_crud.py
│   │   └── context_crud.py
│   ├── sync_worker.py    # 同步执行引擎
│   ├── indexing_worker.py# 索引工作器
│   └── es_indexer.py     # ES 索引器
├── models/               # 数据模型
│   ├── ontology.py       # 本体层 (Def/Ver/Property)
│   ├── system.py         # 系统层 (Connection/SyncJob)
│   ├── context.py        # 上下文层 (Binding/Mapping)
│   ├── meta.py           # 旧架构兼容
│   └── ...
├── core/                 # 核心配置
│   ├── config.py         # 配置管理 (含 sandbox 配置)
│   ├── db.py             # 数据库连接
│   ├── vector_store.py   # ChromaDB
│   └── elastic_store.py  # Elasticsearch
├── services/             # 服务层
│   ├── search_service.py
│   ├── graph_service.py
│   └── chat_agent.py
└── sandbox/              # 沙箱服务 (独立部署)
    ├── main.py           # FastAPI 沙箱服务
    ├── Dockerfile
    └── requirements.txt
```

## 代码执行架构

MDP 支持三种代码执行模式：

```
┌─────────────────────────────────────────────────────────────────┐
│                     code_executor.py                             │
│                     (代码执行调度器)                              │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   BUILTIN       │   SUBPROCESS    │        REMOTE               │
│   内置执行器     │   子进程执行器   │        远程沙箱              │
│                 │                 │                             │
│ function_runner │ subprocess_runner│    httpx -> Sandbox        │
│     .py         │     .py         │    (K8s Pod:8001)          │
│                 │                 │                             │
│ 快速、可访问DB   │ 隔离、支持超时   │    安全隔离、资源限制        │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### 执行模式选择逻辑 (auto)

1. 检测代码中的 import 语句
2. 如果使用 numpy/pandas 等 → subprocess
3. 如果使用数据库 API 且有 session → builtin
4. 其他情况 → builtin（更快）
5. 显式指定 remote → 调用 K8s Sandbox 服务

## 关键业务流程

### 流程 1：数据同步

```
连接器管理 → 数据探索 → 创建同步任务 → 执行同步 → 数据写入 raw_store + raw_data
```

### 流程 2：对象类型创建

```
对象类型向导 → 选择数据源(同步任务) → 配置属性映射 → 创建 Def + Ver + Property + Mapping
```

### 流程 3：数据映射与索引

```
映射编辑器 → 配置转换规则 → 发布映射 → 触发索引任务 → Triple Write
```

### 流程 4：混合搜索

```
用户输入 → Elasticsearch 全文搜索 + ChromaDB 向量搜索 → 结果融合 → 返回
```

### 流程 5：代码执行

```
前端提交代码 → POST /api/v3/execute/code/test → code_executor 调度 →
  ├── builtin: 进程内执行
  ├── subprocess: 子进程隔离执行
  └── remote: HTTP 调用 K8s Sandbox Pod
```

## 快速定位

### 常见功能定位

| 功能 | 前端文件 | 后端 API | 后端 Engine |
|------|----------|----------|-------------|
| 连接器列表 | DataLink/ConnectorList.tsx | v3/connectors.py | v3/connector_crud.py |
| 数据探索 | DataLink/ConnectorDetail.tsx | v3/connectors.py | v3/connector_crud.py |
| 同步任务 | DataLink/ConnectorDetail.tsx | v3/connectors.py | v3/sync_crud.py |
| 执行同步 | - | v3/connectors.py | sync_worker.py |
| 对象类型列表 | Studio/ObjectTypeList.tsx | v3/ontology.py | v3/ontology_crud.py |
| 对象类型创建 | Studio/ObjectTypeWizard.tsx | v1/ontology.py | meta_crud.py |
| 对象类型编辑 | Studio/ObjectTypeEditor.tsx | v1/ontology.py | meta_crud.py |
| 函数编辑 | Studio/FunctionEditor.tsx | v3/execute.py | code_executor.py |
| 代码执行测试 | Studio/FunctionEditor.tsx | v3/execute.py | code_executor.py |
| 对象中心 | OMA/ObjectCenter.tsx | v3/ontology.py | v3/ontology_crud.py |
| 全局搜索 | Explorer/GlobalSearchPage.tsx | v3/search.py | es_indexer.py |
| 图分析 | Explorer/GraphAnalysis/ | v3/graph.py | - |
| 映射编辑 | DataLink/MultimodalMapping/ | v3/mapping.py | v3/mapping_crud.py |
| 索引健康 | DataLink/IndexHealth/ | v3/health.py | indexing_worker.py |

### API 端点速查

| 功能 | 端点 |
|------|------|
| 对象类型 CRUD | POST/GET/PUT/DELETE /api/v1/meta/object-types |
| 对象类型列表(V3) | GET /api/v3/ontology/object-types |
| 对象统计 | GET /api/v3/ontology/objects/with-stats |
| 连接器 CRUD | /api/v3/connectors |
| 同步任务 | /api/v3/sync-jobs |
| 目标表列表 | GET /api/v3/sync-jobs/target-tables |
| 映射管理 | /api/v3/mappings |
| 项目管理 | /api/v3/projects |
| 全局搜索 | POST /api/v3/search/objects |
| 图分析 | POST /api/v3/graph/expand |
| 代码测试 | POST /api/v3/execute/code/test |
| 函数执行 | POST /api/v3/execute/function/{function_id}/test |

## Kubernetes 部署

### Pod 清单

| Pod | 端口 | 说明 |
|-----|------|------|
| mdp-backend | 8000 | 后端 API 服务 |
| mdp-frontend | 80 | 前端静态服务 |
| mdp-sandbox | 8001 | 代码执行沙箱 |
| mysql | 3306 | MySQL 数据库 |
| elasticsearch | 9200 | 全文搜索 |
| milvus/chromadb | - | 向量存储 |

### 配置文件

```
k8s/
└── sandbox-deployment.yaml   # Sandbox Deployment + Service
```

## 详细参考

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细架构和数据模型
- [BUSINESS-FLOWS.md](BUSINESS-FLOWS.md) - 业务流程和调用链
- [API-REFERENCE.md](API-REFERENCE.md) - API 端点参考
- [ONTOLOGY_CONCEPTS.md](ONTOLOGY_CONCEPTS.md) - 本体核心概念
