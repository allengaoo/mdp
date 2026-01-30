# MDP Platform

多模态本体构建平台 - CEC-AIOS 核心模块

## 项目概述

MDP Platform 是一个**元数据驱动的本体构建平台**，采用"全局资产一致性 (Global Consistency) + 场景化敏捷应用 (Scenario Agility)"的双层设计原则。

### 核心特性

- **元数据驱动架构**：基于本体定义动态生成数据模型和API
- **多版本API支持**：v1（兼容层）+ v3（新架构）并行运行
- **代码执行引擎**：支持内置和子进程两种执行模式
- **运行时上下文API**：为用户代码提供安全的数据操作接口
- **完整测试覆盖**：单元测试、集成测试、E2E测试
- **执行日志系统**：完整的动作执行日志记录和查询

## 项目结构

```
mdp/
├── backend/                    # Python/FastAPI 后端
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── db.py          # 数据库连接
│   │   │   ├── logger.py      # Loguru 日志配置
│   │   │   └── middleware.py  # 请求日志中间件
│   │   ├── models/            # SQLModel 数据模型
│   │   │   ├── meta.py        # Meta层模型（v1）
│   │   │   ├── data.py        # Instance层模型
│   │   │   ├── ontology.py    # 本体模型（v3）
│   │   │   ├── context.py     # 上下文模型
│   │   │   └── ...
│   │   ├── engine/            # 业务逻辑引擎
│   │   │   ├── meta_crud.py   # Meta层CRUD（v1）
│   │   │   ├── instance_crud.py
│   │   │   ├── code_executor.py
│   │   │   ├── runtime_context.py
│   │   │   └── v3/            # v3引擎
│   │   │       ├── ontology_crud.py
│   │   │       ├── project_crud.py
│   │   │       └── context_crud.py
│   │   ├── api/               # API路由
│   │   │   ├── v1/            # v1 API（兼容层）
│   │   │   │   ├── ontology.py
│   │   │   │   └── execute.py
│   │   │   └── v3/            # v3 API（新架构）
│   │   │       ├── ontology.py
│   │   │       └── projects.py
│   │   └── schemas/           # API数据传输对象
│   ├── tests/                 # 测试套件
│   ├── docs/                  # 后端文档
│   ├── requirements.txt       # Python依赖
│   ├── init.sql              # 数据库初始化脚本
│   └── Dockerfile
│
├── frontend/                  # React/TypeScript 前端
│   ├── src/
│   │   ├── App.tsx           # 应用入口和路由
│   │   ├── layouts/          # 布局组件
│   │   │   └── MainLayout.tsx
│   │   ├── platform/         # 平台组件
│   │   │   ├── OMA/          # 本体管理
│   │   │   │   └── OntologyLibrary.tsx
│   │   │   └── Studio/       # 本体工作室
│   │   │       ├── StudioLayout.tsx
│   │   │       ├── TopologyView.tsx
│   │   │       ├── ObjectTypeList.tsx
│   │   │       ├── LinkTypeList.tsx
│   │   │       ├── SharedPropertyList.tsx
│   │   │       ├── FunctionList.tsx
│   │   │       ├── ActionDefinitionList.tsx
│   │   │       ├── ExecutionLogList.tsx
│   │   │       └── OntologyTest.tsx
│   │   ├── api/              # API客户端
│   │   │   ├── client.ts     # 基础客户端
│   │   │   ├── ontology.ts   # 本体API
│   │   │   └── v3/           # v3 API适配器
│   │   └── utils/            # 工具函数
│   ├── e2e/                  # E2E测试（Playwright）
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                     # 项目文档
├── docker-compose.yml        # Docker编排配置
└── README.md
```

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+（或 PostgreSQL 16+）

### 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 复制 env.template 为 .env 并修改数据库连接

# 5. 初始化数据库
python setup_db.py

# 6. 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

### Docker 部署

```bash
docker-compose up -d
```

## 访问地址

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLModel** - 基于Pydantic和SQLAlchemy的ORM
- **MySQL/PostgreSQL** - 关系型数据库
- **Loguru** - 结构化日志库
- **Pydantic Settings** - 配置管理

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design** - UI组件库
- **React Router DOM** - 路由管理

### 测试
- **pytest** - 后端测试
- **Vitest** - 前端单元测试
- **Playwright** - E2E测试

## API 版本

### v1 API（兼容层）
- 前缀：`/api/v1/meta` 和 `/api/v1/execute`
- 用于保持与旧代码的兼容性

### v3 API（新架构）
- 前缀：`/api/v3`
- 支持项目管理、本体版本控制等新特性

## 数据库架构

项目采用**双层架构设计**：

### Meta层（定义层）
| 表名 | 说明 |
|------|------|
| `meta_project` | 项目定义 |
| `meta_object_type` | 对象类型定义 |
| `meta_link_type` | 链接类型定义 |
| `meta_function_def` | 函数定义 |
| `meta_action_def` | 操作定义 |
| `meta_shared_property` | 共享属性定义 |

### Instance层（数据层）
| 表名 | 说明 |
|------|------|
| `sys_object_instance` | 对象实例 |
| `sys_link_instance` | 链接实例 |
| `sys_action_log` | 执行日志 |
| `sys_datasource_table` | 数据源表定义 |

## 测试

### 后端测试
```bash
cd backend
pytest                          # 运行所有测试
pytest tests/test_xxx.py       # 运行特定测试
pytest --cov=app tests/        # 覆盖率报告
```

### 前端测试
```bash
cd frontend
npm run test                   # 单元测试
npm run test:e2e              # E2E测试
npm run test:e2e:ui           # E2E测试（UI模式）
```

## 日志

### 后端日志
- **位置**: `backend/logs/mdp.log`
- **格式**: `{time} | {level} | {request_id} | {message}`
- **轮转**: 10MB，保留10天

### 请求追踪
每个HTTP请求自动生成UUID，通过响应头 `X-Request-ID` 返回。

## 文档

- **API文档**: http://localhost:8000/docs
- **数据库架构**: `backend/docs/database_schema_relationships.md`
- **代码文档**: `docs/CODE_DOCUMENTATION.md`

## 许可证

MIT
