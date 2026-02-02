# MDP Platform

**多模态本体构建平台** - CEC-AIOS 核心模块

## 项目概述

MDP (Metadata-Driven Platform) 是一个**元数据驱动的本体构建平台**，遵循 Palantir Foundry 的核心理念，采用"全局资产一致性 (Global Consistency) + 场景化敏捷应用 (Scenario Agility)"的双层设计原则。

### 核心能力

| 能力 | 说明 |
|------|------|
| **数据连接与同步** | 支持 MySQL、PostgreSQL、S3、Kafka、REST API 等数据源的连接和数据同步 |
| **本体建模** | 对象类型、链接类型、共享属性的版本化定义与管理 |
| **多模态映射** | 可视化画布配置原始数据到本体对象的映射规则 |
| **Triple Write 索引** | 同时写入 MySQL、Elasticsearch、ChromaDB 三存储 |
| **混合搜索** | 支持全文搜索 + 向量搜索的混合检索 |
| **图分析** | 基于链接关系的图扩展和最短路径分析 |
| **代码执行沙箱** | 隔离的代码执行环境，支持 builtin、subprocess、remote 三种执行模式 |
| **Chat2App** | 自然语言查询转 AMIS Schema 渲染 |

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (React + TypeScript)                 │
├─────────────────────────────────────────────────────────────────┤
│  Studio      │  OMA        │  Explorer    │  DataLink           │
│  本体建模     │  对象中心    │  数据探索     │  数据连接            │
├─────────────────────────────────────────────────────────────────┤
│                     API 层 (v1 兼容 / v3)                        │
├─────────────────────────────────────────────────────────────────┤
│                        后端 (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│  API 端点    │  Engine 层   │  Models 层   │  Core 层            │
│  路由定义     │  业务逻辑     │  数据模型     │  基础设施            │
├─────────────────────────────────────────────────────────────────┤
│                       数据存储层                                  │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│ MySQL        │ Elasticsearch│ ChromaDB     │ Ollama            │
│ 结构化数据    │ 全文搜索      │ 向量搜索      │ LLM 推理           │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

---

## 项目结构

```
mdp/
├── backend/                       # Python/FastAPI 后端
│   ├── app/
│   │   ├── main.py               # FastAPI 应用入口
│   │   ├── core/                 # 核心模块
│   │   │   ├── config.py         # 应用配置
│   │   │   ├── db.py             # 数据库连接
│   │   │   ├── elastic_store.py  # Elasticsearch 客户端
│   │   │   ├── vector_store.py   # ChromaDB 向量存储
│   │   │   └── logger.py         # Loguru 日志配置
│   │   ├── api/                  # API 路由
│   │   │   ├── v1/               # v1 兼容层 API
│   │   │   │   ├── ontology.py   # 本体 CRUD
│   │   │   │   └── execute.py    # 执行 API
│   │   │   └── v3/               # v3 主 API
│   │   │       ├── ontology.py   # 本体定义
│   │   │       ├── connectors.py # 连接器和同步
│   │   │       ├── mapping.py    # 映射管理
│   │   │       ├── execute.py    # 代码执行
│   │   │       ├── search.py     # 搜索服务
│   │   │       ├── graph.py      # 图分析
│   │   │       ├── health.py     # 健康监控
│   │   │       └── chat.py       # Chat2App
│   │   ├── engine/               # 业务逻辑引擎
│   │   │   ├── meta_crud.py      # 元数据 CRUD
│   │   │   ├── code_executor.py  # 代码执行调度器
│   │   │   ├── sync_worker.py    # 同步执行引擎
│   │   │   ├── indexing_worker.py# 索引工作器
│   │   │   └── v3/               # v3 CRUD 操作
│   │   │       ├── ontology_crud.py
│   │   │       ├── connector_crud.py
│   │   │       ├── mapping_crud.py
│   │   │       └── project_crud.py
│   │   ├── models/               # SQLModel 数据模型
│   │   │   ├── ontology.py       # 本体模型 (Def/Ver/Property)
│   │   │   ├── system.py         # 系统模型 (Connection/SyncJob)
│   │   │   ├── context.py        # 上下文模型 (Binding/Mapping)
│   │   │   └── meta.py           # 旧架构兼容模型
│   │   └── services/             # 服务层
│   │       ├── search_service.py
│   │       ├── graph_service.py
│   │       └── chat_agent.py
│   ├── sandbox/                  # 沙箱服务 (独立部署)
│   │   ├── main.py               # 沙箱服务代码
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── tests/                    # 测试套件
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                     # React/TypeScript 前端
│   ├── src/
│   │   ├── App.tsx               # 应用入口和路由
│   │   ├── api/                  # API 客户端
│   │   │   ├── axios.ts          # v1 Axios 实例
│   │   │   └── v3/               # v3 API 客户端
│   │   │       ├── client.ts     # v3 Axios 实例
│   │   │       ├── ontology.ts   # 本体 API
│   │   │       ├── connectors.ts # 连接器 API
│   │   │       ├── mapping.ts    # 映射 API
│   │   │       ├── search.ts     # 搜索 API
│   │   │       └── graph.ts      # 图分析 API
│   │   ├── platform/             # 业务页面
│   │   │   ├── Studio/           # 本体工作室
│   │   │   │   ├── ObjectTypeList.tsx
│   │   │   │   ├── ObjectTypeEditor.tsx
│   │   │   │   ├── LinkTypeList.tsx
│   │   │   │   ├── FunctionList.tsx
│   │   │   │   ├── FunctionEditor.tsx
│   │   │   │   └── TopologyView.tsx
│   │   │   ├── OMA/              # 对象管理中心
│   │   │   ├── Explorer/         # 数据探索
│   │   │   │   ├── GlobalSearchPage.tsx
│   │   │   │   ├── Object360/
│   │   │   │   ├── GraphAnalysis/
│   │   │   │   └── Chat2App/
│   │   │   └── DataLink/         # 数据连接
│   │   │       ├── ConnectorList.tsx
│   │   │       ├── ConnectorDetail.tsx
│   │   │       ├── MultimodalMapping/
│   │   │       └── IndexHealth/
│   │   └── layouts/              # 布局组件
│   ├── e2e/                      # E2E 测试 (Playwright)
│   └── package.json
│
├── k8s/                          # Kubernetes 部署配置
│   └── sandbox-deployment.yaml   # 沙箱服务部署
│
├── docs/                         # 项目文档
└── docker-compose.yml            # Docker 编排配置
```

---

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架 |
| **SQLModel** | ORM (基于 Pydantic + SQLAlchemy) |
| **MySQL** | 元数据存储 |
| **Elasticsearch** | 全文搜索 |
| **ChromaDB** | 向量存储 |
| **Ollama** | 本地 LLM 推理 |
| **httpx** | HTTP 客户端 (沙箱调用) |
| **Loguru** | 结构化日志 |

### 前端
| 技术 | 用途 |
|------|------|
| **React 18** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Vite** | 构建工具 |
| **Ant Design** | UI 组件库 |
| **React Flow** | 可视化画布 |
| **Axios** | HTTP 客户端 |

### 基础设施
| 技术 | 用途 |
|------|------|
| **Kubernetes** | 容器编排 |
| **Docker** | 容器化 |
| **Nginx** | 前端静态服务 |

---

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Docker & Kubernetes (可选)

### 本地开发

#### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (创建 .env 文件)
cp env.template .env
# 编辑 .env 配置数据库连接

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Kubernetes 部署

```bash
# 构建镜像
docker build -t mdp-backend:v1 ./backend
docker build -t mdp-frontend:v1 ./frontend
docker build -t mdp-sandbox:v1 ./backend/sandbox

# 部署服务
kubectl apply -f k8s/
```

---

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | 用户界面 |
| 后端 API | http://localhost:8000 | API 服务 |
| Swagger UI | http://localhost:8000/docs | API 文档 |
| 沙箱服务 | http://localhost:8001 | 代码执行沙箱 |

---

## API 版本说明

### V1 API (`/api/v1/meta`)
- 用于兼容旧架构
- 主要用于对象类型、链接类型的 CRUD 操作
- 内部自动转发到 V3 逻辑

### V3 API (`/api/v3`)
- 新架构，支持版本化的对象类型和链接类型
- 支持项目管理、映射管理、搜索、图分析等高级功能
- 推荐用于新功能开发

---

## 代码执行引擎

MDP 提供三种代码执行模式：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **builtin** | 内置执行器，直接在进程内执行 | 简单代码，需要数据库访问 |
| **subprocess** | 子进程执行器，隔离执行 | 复杂计算，需要 numpy/pandas |
| **remote** | 远程沙箱执行器，通过 HTTP 调用 | 生产环境，安全隔离 |

使用示例：

```python
# 前端调用
POST /api/v3/execute/code/test
{
  "code_content": "def main(context):\n    return context['x'] * 2",
  "context": {"x": 21},
  "executor_type": "remote",  # auto, builtin, subprocess, remote
  "timeout_seconds": 30
}
```

---

## 数据库架构

项目采用**三层架构设计**：

| 数据库 | 用途 | 主要表 |
|--------|------|--------|
| **ontology_meta_new** | 元数据存储 | `meta_object_type_def`, `meta_object_type_ver`, `sys_connection` |
| **mdp_raw_store** | 原始数据存储 | 同步任务的目标表（动态创建）|
| **ontology_raw_data** | 业务数据存储 | 从 raw_store 复制的最终数据 |

---

## 测试

### 后端测试
```bash
cd backend
pytest                          # 运行所有测试
pytest tests/test_xxx.py        # 运行特定测试
pytest --cov=app tests/         # 覆盖率报告
```

### 前端测试
```bash
cd frontend
npm run test                    # 单元测试
npm run test:e2e                # E2E 测试
npm run test:e2e:ui             # E2E 测试（UI 模式）
```

---

## 日志

### 后端日志
- **位置**: `backend/logs/mdp.log`
- **格式**: `{time} | {level} | {request_id} | {message}`
- **轮转**: 10MB，保留10天

### 请求追踪
每个 HTTP 请求自动生成 UUID，通过响应头 `X-Request-ID` 返回。

---

## 文档

- **API 文档**: http://localhost:8000/docs
- **架构指南**: `.cursor/skills/mdp-architecture/`
- **代码文档**: `docs/CODE_DOCUMENTATION.md`

---

## 许可证

MIT
