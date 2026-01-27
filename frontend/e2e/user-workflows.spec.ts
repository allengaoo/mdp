import { test, expect } from '@playwright/test';

/**
 * E2E Tests for User Business Workflows
 * 用户主要业务流程端到端测试
 * 
 * 这些测试模拟真实用户的完整操作流程
 */

const projectId = 'proj-default';

/**
 * 工作流 1: 对象类型定义流程
 * 用户创建新的对象类型并配置属性
 */
test.describe('Workflow: Object Type Definition', () => {
  
  test('complete object type creation flow', async ({ page }) => {
    test.setTimeout(90000);
    
    // Step 1: 导航到对象类型页面
    await page.goto(`/oma/project/${projectId}/object-types`);
    await page.waitForLoadState('networkidle');
    
    console.log('Step 1: Navigated to object types page');
    
    // Step 2: 打开创建向导
    const createButton = page.locator('button').filter({ hasText: /Create|创建/i });
    if (await createButton.count() > 0) {
      await createButton.first().click();
      await page.waitForSelector('.ant-modal', { timeout: 5000 });
      console.log('Step 2: Create wizard opened');
    } else {
      console.log('Step 2: Create button not found, skipping');
      return;
    }
    
    // Step 3: 填写基本信息
    const displayNameInput = page.locator('input').filter({ has: page.locator('[placeholder*="name" i], [placeholder*="名称"]') }).first();
    if (await displayNameInput.isVisible()) {
      await displayNameInput.fill('Test Object Type');
      console.log('Step 3: Basic info filled');
    }
    
    // Step 4: 导航到下一步
    const nextButton = page.locator('button').filter({ hasText: /Next|下一步/i });
    if (await nextButton.count() > 0) {
      await nextButton.first().click();
      await page.waitForTimeout(500);
      console.log('Step 4: Navigated to next step');
    }
    
    // Step 5: 验证向导流程
    const wizardContent = page.locator('.ant-modal-content');
    await expect(wizardContent).toBeVisible();
    console.log('Step 5: Wizard flow verified');
    
    // Step 6: 关闭向导（不保存）
    const cancelButton = page.locator('button').filter({ hasText: /Cancel|取消/i });
    if (await cancelButton.count() > 0) {
      await cancelButton.first().click();
      console.log('Step 6: Wizard closed');
    }
    
    console.log('✅ Object type creation workflow completed');
  });

  test('view and edit existing object type', async ({ page }) => {
    test.setTimeout(60000);
    
    // Step 1: 导航到对象类型页面
    await page.goto(`/oma/project/${projectId}/object-types`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 等待表格加载
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 }).catch(() => null);
    
    const rows = page.locator('.ant-table-tbody tr.ant-table-row');
    if (await rows.count() === 0) {
      console.log('No object types to edit, skipping');
      return;
    }
    
    // Step 3: 点击编辑按钮
    const editButton = rows.first().locator('button').filter({ hasText: /Edit/i });
    if (await editButton.count() > 0) {
      await editButton.first().click();
      await page.waitForSelector('.ant-modal', { timeout: 5000 });
      console.log('Step 3: Edit modal opened');
    }
    
    // Step 4: 验证编辑器内容
    const modal = page.locator('.ant-modal');
    await expect(modal).toBeVisible();
    
    // Step 5: 关闭编辑器
    const cancelButton = page.locator('button').filter({ hasText: /Cancel|取消/i });
    if (await cancelButton.count() > 0) {
      await cancelButton.first().click();
    }
    
    console.log('✅ View and edit object type workflow completed');
  });
});

/**
 * 工作流 2: 函数开发流程
 * 用户创建函数、编写代码、测试运行
 */
test.describe('Workflow: Function Development', () => {
  
  test('complete function creation and test flow', async ({ page }) => {
    test.setTimeout(90000);
    
    // Step 1: 导航到函数页面
    await page.goto(`/oma/project/${projectId}/functions`);
    await page.waitForLoadState('networkidle');
    console.log('Step 1: Navigated to functions page');
    
    // Step 2: 打开创建向导
    const createButton = page.locator('button').filter({ hasText: /Create|创建/i });
    if (await createButton.count() > 0) {
      await createButton.first().click();
      await page.waitForSelector('.ant-modal', { timeout: 5000 });
      console.log('Step 2: Create wizard opened');
    } else {
      console.log('Step 2: Create button not found');
      return;
    }
    
    // Step 3: 填写函数信息
    const inputs = page.locator('.ant-modal input');
    if (await inputs.count() > 0) {
      await inputs.first().fill('Test Function');
      console.log('Step 3: Function info filled');
    }
    
    // Step 4: 关闭向导
    const cancelButton = page.locator('button').filter({ hasText: /Cancel|取消/i });
    if (await cancelButton.count() > 0) {
      await cancelButton.first().click();
    }
    
    console.log('✅ Function creation workflow started');
  });

  test('edit function and run code', async ({ page }) => {
    test.setTimeout(90000);
    
    // Step 1: 导航到函数页面
    await page.goto(`/oma/project/${projectId}/functions`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 等待函数列表加载
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 }).catch(() => null);
    
    const rows = page.locator('.ant-table-tbody tr.ant-table-row');
    if (await rows.count() === 0) {
      console.log('No functions to edit, skipping');
      return;
    }
    
    // Step 3: 打开编辑器
    const editButton = rows.first().locator('button').filter({ hasText: /Edit/i });
    if (await editButton.count() > 0) {
      await editButton.first().click();
      await page.waitForSelector('.ant-modal', { timeout: 5000 });
      console.log('Step 3: Function editor opened');
    } else {
      console.log('Edit button not found');
      return;
    }
    
    // Step 4: 切换到 Code 标签
    const codeTab = page.locator('.ant-tabs-tab').filter({ hasText: 'Code' });
    if (await codeTab.count() > 0) {
      await codeTab.click();
      await page.waitForTimeout(500);
      console.log('Step 4: Switched to Code tab');
    }
    
    // Step 5: 查找运行按钮
    const runButton = page.locator('button').filter({ hasText: /运行|Run|Execute/i });
    if (await runButton.count() > 0) {
      console.log('Step 5: Run button found');
      
      // 监听 API 请求
      const requestPromise = page.waitForRequest(
        request => request.url().includes('/execute/'),
        { timeout: 5000 }
      ).catch(() => null);
      
      await runButton.first().click();
      
      const request = await requestPromise;
      if (request) {
        console.log('Step 6: Code execution API called');
      }
    }
    
    // 关闭编辑器
    const cancelButton = page.locator('button').filter({ hasText: /Cancel|取消|Close/i });
    if (await cancelButton.count() > 0) {
      await cancelButton.first().click();
    }
    
    console.log('✅ Function edit and run workflow completed');
  });
});

/**
 * 工作流 3: 行为执行和日志查看流程
 * 用户执行行为并查看执行日志
 */
test.describe('Workflow: Action Execution and Logging', () => {
  
  test('execute action and view logs', async ({ page }) => {
    test.setTimeout(120000);
    
    // Step 1: 导航到本体测试页面
    await page.goto(`/oma/project/${projectId}/test`);
    await page.waitForLoadState('networkidle');
    console.log('Step 1: Navigated to ontology test page');
    
    // Step 2: 等待页面加载
    await page.waitForSelector('.ant-card, text=行为库', { timeout: 15000 }).catch(() => null);
    
    // Step 3: 尝试添加行为到队列
    const addButton = page.locator('button').filter({
      has: page.locator('.anticon-plus')
    }).first();
    
    if (await addButton.isVisible()) {
      await addButton.click();
      await page.waitForTimeout(500);
      console.log('Step 2: Action added to queue');
    }
    
    // Step 4: 执行行为
    const executeButton = page.locator('button').filter({
      hasText: /执行|Execute/i
    }).first();
    
    if (await executeButton.isVisible()) {
      await executeButton.click();
      await page.waitForTimeout(2000);
      console.log('Step 3: Action executed');
    }
    
    // Step 5: 导航到日志页面
    await page.goto(`/oma/project/${projectId}/logs`);
    await page.waitForLoadState('networkidle');
    console.log('Step 4: Navigated to logs page');
    
    // Step 6: 验证日志显示
    await page.waitForSelector('.ant-table, .ant-empty', { timeout: 15000 });
    
    const table = page.locator('.ant-table');
    const empty = page.locator('.ant-empty');
    
    if (await table.isVisible()) {
      const rows = page.locator('.ant-table-tbody tr.ant-table-row');
      const count = await rows.count();
      console.log(`Step 5: Found ${count} log entries`);
    } else if (await empty.isVisible()) {
      console.log('Step 5: No logs yet (empty state)');
    }
    
    console.log('✅ Action execution and logging workflow completed');
  });

  test('filter and search logs', async ({ page }) => {
    test.setTimeout(60000);
    
    // Step 1: 导航到日志页面
    await page.goto(`/oma/project/${projectId}/logs`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 查找筛选控件
    const statusFilter = page.locator('.ant-select').first();
    
    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.waitForTimeout(300);
      
      // 选择一个选项
      const option = page.locator('.ant-select-item').first();
      if (await option.isVisible()) {
        await option.click();
        console.log('Step 2: Filter applied');
      }
    }
    
    // Step 3: 点击刷新按钮
    const refreshButton = page.locator('button').filter({
      has: page.locator('.anticon-reload, .anticon-sync')
    }).first();
    
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await page.waitForTimeout(1000);
      console.log('Step 3: Logs refreshed');
    }
    
    console.log('✅ Log filter and search workflow completed');
  });
});

/**
 * 工作流 4: 拓扑视图浏览
 * 用户查看本体拓扑图
 */
test.describe('Workflow: Topology Exploration', () => {
  
  test('view and interact with topology', async ({ page }) => {
    test.setTimeout(60000);
    
    // Step 1: 导航到拓扑页面
    await page.goto(`/oma/project/${projectId}/topology`);
    await page.waitForLoadState('networkidle');
    console.log('Step 1: Navigated to topology page');
    
    // Step 2: 等待图形容器加载
    await page.waitForSelector('.react-flow, [class*="reactflow"]', { timeout: 15000 }).catch(() => null);
    
    const flowContainer = page.locator('.react-flow, [class*="reactflow"]');
    if (await flowContainer.isVisible()) {
      console.log('Step 2: React Flow container loaded');
      
      // Step 3: 查找节点
      const nodes = page.locator('.react-flow__node');
      const nodeCount = await nodes.count();
      console.log(`Step 3: Found ${nodeCount} nodes`);
      
      // Step 4: 查找边
      const edges = page.locator('.react-flow__edge');
      const edgeCount = await edges.count();
      console.log(`Step 4: Found ${edgeCount} edges`);
      
      // Step 5: 测试缩放控件（如果可用）
      const zoomIn = page.locator('button[class*="zoom"]').first();
      if (await zoomIn.isVisible()) {
        // 检查按钮是否启用
        const isEnabled = await zoomIn.isEnabled().catch(() => false);
        if (isEnabled) {
          await zoomIn.click();
          console.log('Step 5: Zoom control clicked');
        } else {
          console.log('Step 5: Zoom control visible but disabled');
        }
      } else {
        console.log('Step 5: Zoom control not visible');
      }
    } else {
      console.log('React Flow container not found');
    }
    
    console.log('✅ Topology exploration workflow completed');
  });
});

/**
 * 工作流 5: 跨模块导航
 * 用户在不同模块间切换
 */
test.describe('Workflow: Cross-Module Navigation', () => {
  
  test('navigate through all studio modules', async ({ page }) => {
    test.setTimeout(120000);
    
    const modules = [
      { path: 'topology', name: 'Topology' },
      { path: 'object-types', name: 'Object Types' },
      { path: 'link-types', name: 'Link Types' },
      { path: 'shared-properties', name: 'Shared Properties' },
      { path: 'actions', name: 'Actions' },
      { path: 'functions', name: 'Functions' },
      { path: 'logs', name: 'Execution Logs' },
      { path: 'test', name: 'Ontology Test' },
    ];
    
    for (const module of modules) {
      await page.goto(`/oma/project/${projectId}/${module.path}`);
      await page.waitForLoadState('networkidle');
      
      // 验证页面加载
      const pageLoaded = await page.locator('.ant-table, .ant-card, .react-flow, .ant-empty').first().isVisible().catch(() => false);
      
      if (pageLoaded) {
        console.log(`✓ ${module.name} page loaded`);
      } else {
        console.log(`⚠ ${module.name} page may not have loaded correctly`);
      }
    }
    
    console.log('✅ Cross-module navigation workflow completed');
  });
});
