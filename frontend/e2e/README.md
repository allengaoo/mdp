# E2E 测试说明文档

本文档描述了 MDP 平台前端 E2E（端到端）测试套件的结构和功能。

## 概述

E2E 测试使用 [Playwright](https://playwright.dev/) 框架编写，覆盖了 MDP 平台的主要功能模块。所有测试用例都设置了超时时间（30秒或60秒），以防止测试程序无限期等待。

## 测试文件结构

### 1. `navigation.spec.ts` - 导航功能测试

测试应用的主要导航功能。

**测试用例：**
- `should load home page` - 验证首页能够正常加载
- `should navigate to OMA (Ontology Library)` - 验证能够导航到本体库页面
- `should navigate between project sections` - 验证能够在项目不同模块间导航（对象类型、连接类型、拓扑视图）
- `should display sidebar navigation` - 验证侧边栏导航是否正常显示

**超时设置：** 30秒（导航测试为60秒）

### 2. `ontology-library.spec.ts` - 本体库测试

测试本体库（项目列表）页面的核心功能。

**测试用例：**
- `should display project list` - 验证项目列表能够正常显示
- `should show project statistics` - 验证项目统计信息（对象数量、连接数量等）能够显示
- `should navigate to project detail on click` - 验证点击项目卡片能够导航到项目详情页

**超时设置：** 30秒

### 3. `project-management.spec.ts` - 项目管理测试

测试多项目管理功能。

**测试用例：**
- `should display default project` - 验证默认项目（Battlefield）能够正常显示
- `should show project details with statistics` - 验证项目详情和统计信息能够显示
- `should navigate to project workspace on click` - 验证点击项目能够导航到项目工作区
- `should display project workspace with sidebar` - 验证项目工作区及其侧边栏能够正常显示

**超时设置：** 30秒

### 4. `object-type-management.spec.ts` - 对象类型管理测试

测试对象类型管理的核心功能。

**测试用例：**
- `should display object type list` - 验证对象类型列表能够正常显示
- `should open create object type wizard` - 验证能够打开创建对象类型的向导
- `should display object type details when clicking edit` - 验证点击编辑按钮能够显示对象类型详情

**超时设置：** 30秒

### 5. `link-type-management.spec.ts` - 连接类型管理测试

测试连接类型管理的核心功能。

**测试用例：**
- `should display link type list` - 验证连接类型列表能够正常显示
- `should show source and target columns` - 验证表格能够显示源和目标列
- `should open create link type wizard` - 验证能够打开创建连接类型的向导

**超时设置：** 30秒

### 6. `action-function-management.spec.ts` - 动作和函数管理测试

测试动作（Action）和函数（Function）管理的核心功能。

**测试用例：**

**Action Management：**
- `should display action definition list` - 验证动作定义列表能够正常显示
- `should open create action wizard` - 验证能够打开创建动作的向导

**Function Management：**
- `should display function definition list` - 验证函数定义列表能够正常显示
- `should show function code preview` - 验证能够显示函数代码预览

**超时设置：** 30秒

### 7. `topology-view.spec.ts` - 拓扑视图测试

测试拓扑视图的核心功能。

**测试用例：**
- `should display topology graph` - 验证拓扑图容器（React Flow）能够正常显示
- `should display nodes for object types` - 验证对象类型节点能够在图中显示
- `should display edges for link types` - 验证连接类型边能够在图中显示
- `should allow zooming and panning` - 验证拓扑图支持缩放和平移操作

**超时设置：** 30秒

### 8. `chat2app.spec.ts` - Chat2App 测试 (V3.1 新增)

测试 Chat2App 自然语言对话界面。

**测试用例：**
- `should load Chat2App page` - 验证 Chat2App 页面能够正常加载
- `should display health status` - 验证 Ollama 服务状态显示
- `should display suggested questions` - 验证默认建议问题标签
- `should allow typing in input field` - 验证输入框功能正常
- `should click suggestion and fill input` - 验证点击建议标签填充输入
- `should send message and show response` - 验证消息发送和响应显示
- `should show Ollama unavailable warning when service is down` - 验证服务不可用警告

**超时设置：** 30-60秒

## 运行测试

### 前置条件

1. 确保后端服务正在运行（默认端口 8000）
2. 确保前端开发服务器正在运行（默认端口 3000）

### 运行所有测试

```bash
cd frontend
npm run test:e2e
```

### 运行特定测试文件

```bash
cd frontend
npx playwright test e2e/navigation.spec.ts
```

### 以 UI 模式运行（推荐用于调试）

```bash
cd frontend
npm run test:e2e:ui
```

### 以有头模式运行（可以看到浏览器窗口）

```bash
cd frontend
npm run test:e2e:headed
```

### 调试模式

```bash
cd frontend
npm run test:e2e:debug
```

## 测试配置

测试配置位于 `playwright.config.ts`，主要配置包括：

- **测试目录：** `./e2e`
- **基础 URL：** `http://localhost:3000`
- **浏览器：** Chromium
- **并行执行：** 启用（CI 环境除外）
- **重试策略：** CI 环境自动重试 2 次
- **报告：** HTML 报告 + 控制台列表

## 超时设置说明

所有测试用例都设置了明确的超时时间：

- **标准测试：** 30秒 - 适用于大多数单页面操作
- **导航测试：** 60秒 - 适用于需要多次页面跳转的测试

超时时间通过 `test.setTimeout()` 在每个测试用例开始时设置，确保测试不会无限期等待。

## 测试数据

测试使用默认项目 ID：`proj-default`。确保测试环境中存在此项目，或者根据实际情况修改测试文件中的 `projectId` 常量。

## 注意事项

1. **环境依赖：** 测试需要后端和前端服务同时运行
2. **数据依赖：** 某些测试依赖于特定的测试数据（如默认项目）
3. **选择器：** 测试使用 Ant Design 组件的默认类名（如 `.ant-table`、`.ant-card` 等）
4. **容错性：** 部分测试包含条件检查，如果某些元素不存在会跳过相关断言（如创建按钮）

## 故障排查

### 测试失败常见原因

1. **服务未启动：** 确保后端和前端服务都在运行
2. **端口冲突：** 检查 3000 和 8000 端口是否被占用
3. **超时：** 如果网络较慢，可能需要增加超时时间
4. **元素未找到：** 检查页面结构是否发生变化，更新相应的选择器

### 查看测试报告

测试运行后会生成 HTML 报告，位于 `playwright-report` 目录。可以通过以下命令查看：

```bash
npx playwright show-report
```

## 维护建议

1. **定期更新选择器：** 当 UI 组件更新时，及时更新测试中的选择器
2. **添加新功能测试：** 新功能开发完成后，及时添加相应的 E2E 测试
3. **优化测试性能：** 定期检查测试执行时间，优化慢速测试
4. **保持测试独立性：** 确保测试之间不相互依赖，可以独立运行
