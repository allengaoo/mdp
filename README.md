# MDP Platform Demo

一个全栈演示项目，展示 MDP（Meta-Data-Process）平台的核心功能。

## 项目结构

```
mdp-platform-demo/
├── backend/              # Python/FastAPI 后端
│   ├── app/
│   │   ├── main.py      # FastAPI 应用入口
│   │   ├── core/        # 核心模块
│   │   │   ├── config.py      # 应用配置（环境变量）
│   │   │   ├── db.py          # 数据库连接和会话管理
│   │   │   ├── logger.py      # Loguru 日志配置
│   │   │   └── middleware.py  # 请求日志和追踪中间件
│   │   ├── models/      # SQLModel 数据模型
│   │   │   ├── meta.py  # Meta 层模型（ObjectType, LinkType, FunctionDefinition, ActionDefinition）
│   │   │   └── data.py  # Instance 层模型（ObjectInstance）
│   │   ├── engine/      # 业务逻辑引擎
│   │   │   ├── meta_crud.py        # Meta 层 CRUD 操作
│   │   │   ├── instance_crud.py    # Instance 层 CRUD 操作
│   │   │   ├── function_runner.py  # 函数执行引擎
│   │   │   └── action_runner.py    # 操作执行引擎（示例）
│   │   ├── api/         # API 路由
│   │   │   └── v1/
│   │   │       ├── ontology.py  # Meta 层 RESTful API
│   │   │       └── execute.py   # 运行时操作 API（Action 执行、数据查询）
│   │   └── extensions/  # 扩展模块
│   │       └── battlefield/
│   │           └── init_data.py  # Battlefield 场景数据初始化
│   ├── logs/            # 日志文件目录
│   ├── requirements.txt # Python 依赖
│   ├── env.template     # 环境变量模板
│   ├── create_env.py    # 环境变量文件生成脚本
│   ├── setup_db.py      # 数据库初始化脚本
│   ├── init.sql         # 数据库架构 SQL
│   ├── seed_data.sql    # 演示数据（Battlefield 场景）
│   └── Dockerfile       # Docker 镜像定义
│
├── frontend/            # React/Vite/TypeScript 前端
│   ├── src/
│   │   ├── layouts/    # 布局组件
│   │   │   └── MainLayout.tsx  # 主布局（侧边栏导航）
│   │   ├── platform/   # 平台组件
│   │   │   ├── OMA/
│   │   │   │   └── OntologyLibrary.tsx  # 本体库列表
│   │   │   └── Studio/ # 本体项目工作室
│   │   │       ├── StudioLayout.tsx      # 工作室布局
│   │   │       ├── TopologyView.tsx      # 拓扑总览（ReactFlow）
│   │   │       ├── ObjectTypeList.tsx    # 对象类型列表
│   │   │       ├── ObjectTypeWizard.tsx  # 对象类型创建向导
│   │   │       ├── ObjectTypeEditor.tsx # 对象类型编辑器
│   │   │       ├── LinkTypeList.tsx      # 链接类型列表
│   │   │       ├── LinkTypeWizard.tsx    # 链接类型创建向导
│   │   │       ├── LinkTypeEditor.tsx    # 链接类型编辑器
│   │   │       ├── SharedPropertyList.tsx # 公共属性列表
│   │   │       ├── SharedPropertyModal.tsx # 公共属性模态框
│   │   │       ├── PhysicalPropertyList.tsx # 物理属性列表
│   │   │       ├── ActionDefinitionList.tsx # 行为定义列表
│   │   │       ├── FunctionList.tsx      # 函数列表
│   │   │       ├── ExecutionLogList.tsx  # 运行日志列表
│   │   │       └── OntologyTest.tsx      # 本体测试页面
│   │   ├── apps/       # 应用组件
│   │   │   └── Battlefield/
│   │   │       └── Dashboard.tsx      # Battlefield 仪表板（地图可视化）
│   │   └── api/        # API 客户端
│   │       ├── client.ts  # 基础 API 客户端
│   │       └── axios.ts   # Axios 客户端（带日志拦截器）
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml   # Docker 编排配置
└── README.md
```

## 快速开始

### 前置要求

**使用 Docker（推荐）：**
- Docker Desktop for Windows（下载：https://www.docker.com/products/docker-desktop）

**本地开发（无需 Docker）：**
- Python 3.10+
- MySQL 数据库（本地安装）
- Node.js 18+（前端开发）

### 方式一：使用 Docker Compose（推荐）

1. 克隆项目并进入目录：
```bash
cd mdp-platform-demo
```

2. 复制环境变量模板（Windows PowerShell）：
```powershell
Copy-Item backend\env.template backend\.env
```

   或者手动创建 `backend/.env` 文件，复制 `backend/env.template` 的内容。

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问：
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

### 方式二：本地开发（不使用 Docker）

#### 后端开发

1. **安装 MySQL**（如果未安装）：
   - 下载：https://dev.mysql.com/downloads/mysql/
   - 或使用 MySQL Installer for Windows
   - 安装并记住设置的 root 密码

2. **进入后端目录**：
```powershell
cd backend
```

3. **创建虚拟环境**：
```powershell
python -m venv venv
venv\Scripts\activate
```

4. **安装依赖**：
```powershell
pip install -r requirements.txt
```

5. **配置环境变量**：
   
   运行辅助脚本创建 `.env` 文件：
```powershell
py backend\create_env.py
```
   
   或手动创建 `backend/.env` 文件，内容参考 `backend/env.template`：
   ```
   DATABASE_URL=mysql+pymysql://root:您的密码@localhost:3306/ontology
   DEBUG=False
   ```
   
   **注意**：如果 MySQL 用户名不是 `root`，请相应修改。

6. **初始化数据库**：
   
   **方法一：使用 Python 脚本（推荐）**
   
   运行数据库初始化脚本，它会自动创建数据库、应用架构并加载演示数据：
```powershell
py backend\setup_db.py
```
   
   **方法二：手动执行 SQL 脚本**
   
   如果选择手动执行：
```powershell
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ontology CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# 应用架构
mysql -u root -p ontology < backend\init.sql
# 加载演示数据（可选）
mysql -u root -p ontology < backend\seed_data.sql
```
   
   **注意**：
   - 数据库名称：`ontology`（在 setup_db.py 和 .env 中配置）
   - 架构脚本会创建完整的数据库表结构
   - 种子数据包含 Battlefield 场景的完整演示数据

7. **启动服务**：
```powershell
# 从项目根目录运行
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

   或者从项目根目录：
```powershell
uvicorn backend.app.main:app --reload
```

   服务启动后：
   - API 服务: http://localhost:8000
   - API 文档: http://localhost:8000/docs
   - 日志文件: `backend/logs/mdp.log`

#### 前端开发

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 访问: http://localhost:3000

## 技术栈

### 后端
- **FastAPI**: 现代 Python Web 框架
- **SQLModel**: 基于 Pydantic 和 SQLAlchemy 的 ORM
- **MySQL**: 关系型数据库
- **PyMySQL**: MySQL 数据库驱动
- **Loguru**: 结构化日志库
- **Pydantic Settings**: 配置管理

### 前端
- **React 18**: UI 框架
- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 快速的前端构建工具
- **Ant Design**: 企业级 UI 组件库
- **React Router DOM**: 路由管理
- **React Leaflet**: 地图可视化组件
- **ReactFlow**: 图形可视化组件
- **Axios**: HTTP 客户端

## 数据库架构

项目使用 MySQL 数据库，表结构分为两层：

### ER 图

```mermaid
erDiagram
    %% Meta Layer (Definitions)
    meta_project {
        varchar id PK
        varchar name
        varchar description
        datetime created_at
    }
    
    meta_object_type {
        varchar id PK
        varchar api_name UK
        varchar display_name
        varchar description
        json property_schema
        varchar project_id FK
        datetime created_at
        datetime updated_at
    }
    
    meta_link_type {
        varchar id PK
        varchar api_name UK
        varchar display_name
        varchar source_type_id FK
        varchar target_type_id FK
        varchar cardinality
    }
    
    meta_function_def {
        varchar id PK
        varchar api_name UK
        varchar display_name
        longtext code_content
        varchar bound_object_type_id FK
        varchar description
        json input_params_schema
        varchar output_type
    }
    
    meta_action_def {
        varchar id PK
        varchar api_name UK
        varchar display_name
        varchar backing_function_id FK
    }
    
    meta_shared_property {
        varchar id PK
        varchar project_id FK
        varchar api_name
        varchar display_name
        varchar data_type
        varchar formatter
        varchar description
        datetime created_at
    }
    
    meta_test_scenario {
        varchar id PK
        varchar project_id FK
        varchar name
        json steps_config
        datetime created_at
    }
    
    sys_datasource_table {
        varchar id PK
        varchar table_name UK
        varchar db_type
        json columns_schema
        datetime created_at
    }
    
    %% Instance Layer (Data)
    sys_object_instance {
        varchar id PK
        varchar object_type_id FK
        json properties
        datetime created_at
        datetime updated_at
    }
    
    sys_link_instance {
        varchar id PK
        varchar link_type_id FK
        varchar source_instance_id FK
        varchar target_instance_id FK
        json properties
        datetime created_at
    }
    
    %% Runtime & Testing Layer
    sys_action_log {
        varchar id PK
        varchar project_id FK
        varchar action_def_id FK
        varchar trigger_user_id
        json input_params
        varchar execution_status
        text error_message
        int duration_ms
        datetime created_at
    }
    
    %% Relationships - Meta Layer
    meta_project ||--o{ meta_object_type : "contains"
    meta_project ||--o{ meta_shared_property : "contains"
    meta_project ||--o{ meta_test_scenario : "contains"
    meta_project ||--o{ sys_action_log : "logs"
    meta_object_type ||--o{ meta_link_type : "source_type"
    meta_object_type ||--o{ meta_link_type : "target_type"
    meta_object_type ||--o{ meta_function_def : "bound_to"
    meta_object_type ||--o{ sys_object_instance : "instantiates"
    meta_function_def ||--o{ meta_action_def : "backed_by"
    meta_action_def ||--o{ sys_action_log : "executed_as"
    
    %% Relationships - Instance Layer
    meta_link_type ||--o{ sys_link_instance : "instantiates"
    sys_object_instance ||--o{ sys_link_instance : "source"
    sys_object_instance ||--o{ sys_link_instance : "target"
```

### Meta 层（定义层）

- **`meta_project`**: 项目定义
  - 用于组织和管理相关的本体定义
  - 一个项目包含多个对象类型、链接类型等
- **`meta_object_type`**: 对象类型定义（如 "Fighter", "Mission"）
  - 包含属性模式（property_schema）的 JSON 定义
  - 关联到项目（project_id）
- **`meta_link_type`**: 关系类型定义（对象间的连接关系）
  - 支持 1:1, 1:N, M:N 基数
  - 定义源对象类型和目标对象类型之间的关系
- **`meta_shared_property`**: 公共属性定义（标准属性库 SPT）
  - 跨对象类型的统一属性定义
  - 支持数据类型约束（STRING, INTEGER, DOUBLE, BOOLEAN, GEOPOINT, DATE）
  - 约束信息存储在 formatter 字段（JSON 格式）
- **`meta_function_def`**: 函数定义（业务逻辑代码）
  - 存储 Python 代码内容
  - 可绑定到特定对象类型
- **`meta_action_def`**: 操作定义（用户触发操作）
  - 关联到函数定义
- **`meta_test_scenario`**: 测试场景定义
  - 存储动作编排序列（JSON 格式）

### 数据源层

- **`sys_datasource_table`**: 数据源表定义
  - 存储原始数据表的元数据信息
  - 用于对象类型创建时选择数据源
  - 包含列结构定义（columns_schema，JSON 格式）

### Instance 层（数据层）

- **`sys_object_instance`**: 对象实例（实际数据行）
  - 使用 JSON 字段存储动态属性
  - 关联到对象类型
- **`sys_link_instance`**: 链接实例（对象间的关系实例）
  - 存储源对象和目标对象之间的连接
  - 支持链接属性（JSON）

数据库初始化脚本：`backend/init.sql`

**数据库设置工具**：
- `backend/setup_db.py`: Python 脚本，自动创建数据库、应用架构和加载演示数据
- `backend/init.sql`: 数据库架构 SQL 文件
- `backend/seed_data.sql`: Battlefield 场景演示数据

## 日志和可观察性

项目集成了完整的日志和追踪系统：

### 后端日志
- **日志库**: Loguru
- **日志位置**: `backend/logs/mdp.log`
- **日志配置**:
  - 控制台输出：彩色、DEBUG 级别
  - 文件输出：INFO 级别、10MB 轮转、保留 10 天、自动压缩
- **日志格式**: `{time} | {level} | {request_id} | {message}`
- **请求追踪**: 每个 HTTP 请求自动生成 UUID request_id，并在响应头 `X-Request-ID` 中返回

### 前端日志
- **HTTP 拦截器**: Axios 拦截器自动记录所有 API 请求和响应
- **日志格式**:
  - 请求: `>> [Req] {method} {url}`
  - 响应: `<< [Res] {status} {url} ({time}ms) [Request-ID: {request_id}]`

## 开发工具

- **`backend/create_env.py`**: 辅助脚本，用于创建 `.env` 文件
- **`backend/setup_db.py`**: 数据库初始化脚本，一键设置数据库

## 项目模块

### 后端模块

#### 核心模块 (`app/core/`)
- **`config.py`**: 应用配置管理
  - 使用 Pydantic Settings 加载环境变量
  - 数据库连接字符串配置
- **`db.py`**: 数据库连接和会话管理
  - SQLModel 引擎配置
  - Session 依赖注入
- **`logger.py`**: 日志配置
  - Loguru 日志系统配置
  - 控制台输出（带颜色）
  - 文件输出（自动轮转和压缩）
  - 日志格式：`{time} | {level} | {request_id} | {message}`
- **`middleware.py`**: HTTP 中间件
  - 请求 ID 生成和追踪
  - 请求/响应日志记录
  - 处理时间计算

#### 数据模型 (`app/models/`)
- **`meta.py`**: Meta 层数据模型
  - `Project`: 项目定义
  - `ObjectType`: 对象类型定义（包含 JSON 属性模式，关联到项目）
  - `LinkType`: 关系类型定义
  - `SharedProperty`: 公共属性定义（标准属性库）
  - `FunctionDefinition`: 函数定义（业务逻辑代码）
  - `ActionDefinition`: 操作定义（用户触发操作）
  - 每个模型包含 `*Create`、`*Update` 和 `*Read` DTOs
- **`data.py`**: Instance 层数据模型
  - `ObjectInstance`: 对象实例（包含 UUID 主键、类型关联、JSON 属性）
  - `LinkInstance`: 链接实例（对象间的关系实例）
  - `DataSourceTable`: 数据源表定义（原始数据表的元数据）

#### 业务逻辑引擎 (`app/engine/`)
- **`meta_crud.py`**: Meta 层 CRUD 操作
  - 完整的 CRUD 函数：`create_*`, `get_*`, `list_*`, `update_*`, `delete_*`
  - 按 `api_name` 查找函数：`get_object_type_by_name`, `get_action_definition_by_name`, `get_shared_property_by_name`
  - 支持更新操作：`update_object_type`, `update_link_type`, `update_shared_property`
  - 集成日志记录
  - 错误处理和事务管理
- **`instance_crud.py`**: Instance 层 CRUD 操作
  - ObjectInstance CRUD：`create_object`, `get_object`, `update_object` (JSON merge), `delete_object`, `list_objects`
  - LinkInstance CRUD：`create_link`, `get_link`, `delete_link`, `get_links_for_object`
  - DataSourceTable CRUD：`create_datasource_table`, `get_datasource_table`, `get_datasource_table_by_name`, `list_datasource_tables`, `delete_datasource_table`
  - JSON 属性过滤：支持通过 MySQL JSON 函数过滤对象属性
  - 集成日志记录和错误处理
- **`function_runner.py`**: 函数执行引擎
  - `execute_function`: 执行用户定义的 Python 函数代码
  - `validate_syntax`: 语法验证
  - 支持动态代码执行（使用 exec）
  - 集成日志记录和异常处理
- **`action_runner.py`**: 操作执行引擎（示例实现，用于演示）

#### API 端点 (`app/api/v1/`)
- **`ontology.py`**: Meta 层 RESTful API
  - 端点前缀：`/api/v1/meta`
  - Projects: `POST/GET/GET/{id} /projects`
  - ObjectTypes: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /object-types`
  - LinkTypes: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /link-types`
  - SharedProperties: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /shared-properties`
  - DataSourceTables: `POST/GET/GET/{id}/GET/name/{name}/DELETE/{id} /datasource-tables`
  - Functions: `POST/GET/GET/{id}/DELETE/{id} /functions`
  - Actions: `POST/GET/GET/{id}/DELETE/{id} /actions`
  - 所有端点支持分页（skip/limit）
  - 支持更新操作（PUT）用于 ObjectType、LinkType、SharedProperty
- **`execute.py`**: 运行时操作 API
  - 端点前缀：`/api/v1/execute`
  - `POST /action/run`: 执行 Action（通过 api_name）
  - `GET /objects/{type_api_name}`: 按类型查询对象（支持 JSON 属性过滤和分页）
  - `POST /objects/{type_api_name}`: 按类型创建对象实例
  - `GET /project/{project_id}/physical-properties`: 获取项目的物理属性聚合
  - 完整的错误处理和请求验证

#### 扩展模块 (`app/extensions/`)
- **`battlefield/init_data.py`**: Battlefield 场景数据初始化（待实现）

### API 端点概览

访问 API 文档：`http://localhost:8000/docs`

#### Meta 层 API (`/api/v1/meta`)

管理 Meta 层定义（项目、对象类型、关系类型、公共属性、数据源表、函数定义、操作定义）：

- **Projects**: `POST/GET/GET/{id} /projects`
- **ObjectTypes**: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /object-types`
- **LinkTypes**: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /link-types`
- **SharedProperties**: `POST/GET/GET/{id}/PUT/{id}/DELETE/{id} /shared-properties`
  - 支持按项目过滤：`GET /shared-properties?project_id={id}`
- **DataSourceTables**: `POST/GET/GET/{id}/GET/name/{name}/DELETE/{id} /datasource-tables`
  - 支持按表名查找：`GET /datasource-tables/name/{table_name}`
- **Functions**: `POST/GET/GET/{id}/DELETE/{id} /functions`
- **Actions**: `POST/GET/GET/{id}/DELETE/{id} /actions`

每个资源支持：
- `POST /{resource}` - 创建（使用 `*Create` DTO 验证）
- `GET /{resource}` - 列表（支持 skip/limit 分页）
- `GET /{resource}/{id}` - 获取单个（返回 `*Read` DTO）
- `PUT /{resource}/{id}` - 更新（ObjectType、LinkType、SharedProperty 支持）
- `DELETE /{resource}/{id}` - 删除

#### 运行时操作 API (`/api/v1/execute`)

执行操作和查询数据：

- **`POST /action/run`** - 执行 Action
  - 请求体：`{ "action_api_name": "strike", "source_id": "...", "params": {...} }`
  - 流程：查找 ActionDefinition → 获取 backing_function_id → 执行函数 → 返回结果
  
- **`GET /objects/{type_api_name}`** - 查询对象实例
  - 查询参数：
    - `filters`: JSON 字符串（可选），例如：`{"status": "Ready", "fuel": 80}`
    - `skip`: 分页偏移（默认 0）
    - `limit`: 分页限制（默认 100，最大 1000）
  - 示例：`GET /execute/objects/fighter?filters={"status":"Ready"}&skip=0&limit=10`
  
- **`POST /objects/{type_api_name}`** - 创建对象实例
  - 请求体：`{ "properties": {...} }`
  - 用于初始数据加载或程序化创建实例

- **`GET /project/{project_id}/physical-properties`** - 获取项目的物理属性
  - 聚合项目中所有对象类型的 property_schema
  - 返回格式：`[{"property_name": "...", "data_type": "...", "belongs_to_object": "..."}]`

### 前端模块

#### 布局组件 (`src/layouts/`)
- **`MainLayout.tsx`**: 主应用布局
  - 左侧固定侧边栏导航
  - 动态菜单项（根据路由显示 Studio 菜单）
  - 面包屑导航支持

#### 平台组件 (`src/platform/`)

- **`OMA/`**: 本体管理组件
  - `OntologyLibrary.tsx`: 本体库列表（项目列表视图）
  
- **`Studio/`**: 本体项目工作室
  - `StudioLayout.tsx`: 工作室布局（嵌套侧边栏、面包屑）
  - `TopologyView.tsx`: 拓扑总览（使用 ReactFlow 可视化）
  - `ObjectTypeList.tsx`: 对象类型列表（带创建/编辑/删除）
  - `ObjectTypeWizard.tsx`: 对象类型创建向导（3步：基本信息、数据源选择、属性映射）
  - `ObjectTypeEditor.tsx`: 对象类型编辑器（标签页布局）
  - `LinkTypeList.tsx`: 链接类型列表（带创建/编辑/删除）
  - `LinkTypeWizard.tsx`: 链接类型创建向导（动态步骤：2步或3步，根据基数）
  - `LinkTypeEditor.tsx`: 链接类型编辑器（响应式映射策略）
  - `SharedPropertyList.tsx`: 公共属性列表（标准属性库 SPT）
  - `SharedPropertyModal.tsx`: 公共属性模态框（可重用，支持创建/编辑）
  - `PhysicalPropertyList.tsx`: 物理属性列表（聚合视图）
  - `ActionDefinitionList.tsx`: 行为定义列表
  - `FunctionList.tsx`: 函数列表
  - `ExecutionLogList.tsx`: 运行日志列表
  - `OntologyTest.tsx`: 本体测试页面（3列布局：动作库、编排画布、监控面板）

#### 应用组件 (`src/apps/`)

- **`Battlefield/`**: Battlefield 应用
  - `Dashboard.tsx`: 战场态势仪表板
    - 使用 React Leaflet 显示地图
    - 实时显示 Fighter 和 Target 位置
    - 支持执行打击操作

#### API 客户端 (`src/api/`)
- `axios.ts`: Axios 客户端（带请求/响应日志拦截器）
- `client.ts`: 基础 API 客户端配置

## 许可证

MIT


