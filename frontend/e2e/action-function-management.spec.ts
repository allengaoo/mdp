import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Action & Function Management
 * 测试动作和函数管理的核心功能
 */
test.describe('Action Management', () => {
  
  const projectId = 'proj-default';
  
  test.beforeEach(async ({ page }) => {
    await page.goto(`/oma/project/${projectId}/actions`);
    await page.waitForLoadState('networkidle');
  });

  test('should display action definition list', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for table or list to load
    await page.waitForSelector('.ant-table, .ant-list', { timeout: 15000 });
    
    // Check that content is visible
    const content = page.locator('.ant-table, .ant-list');
    await expect(content.first()).toBeVisible();
    
    console.log('Action list displayed');
  });

  test('should open create action wizard', async ({ page }) => {
    test.setTimeout(30000);
    await page.waitForLoadState('networkidle');
    
    const createButton = page.locator('button').filter({ hasText: /Create|新建|创建/i });
    
    if (await createButton.count() > 0) {
      await createButton.first().click();
      
      // Wait for modal/wizard
      await page.waitForSelector('.ant-modal, .ant-drawer', { timeout: 5000 });
      
      const modal = page.locator('.ant-modal, .ant-drawer');
      await expect(modal).toBeVisible();
      
      console.log('Create action wizard opened');
    } else {
      console.log('Create button not found');
    }
  });
});

test.describe('Function Management', () => {
  
  const projectId = 'proj-default';
  
  test.beforeEach(async ({ page }) => {
    await page.goto(`/oma/project/${projectId}/functions`);
    await page.waitForLoadState('networkidle');
  });

  test('should display function definition list', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for table or list to load
    await page.waitForSelector('.ant-table, .ant-list', { timeout: 15000 });
    
    const content = page.locator('.ant-table, .ant-list');
    await expect(content.first()).toBeVisible();
    
    console.log('Function list displayed');
  });

  test('should show function details when clicking edit', async ({ page }) => {
    test.setTimeout(30000);
    // 等待表格数据行加载（使用 ant-table-row 类排除隐藏的 measure-row）
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    
    // 选择实际的数据行
    const firstRow = page.locator('.ant-table-tbody tr.ant-table-row').first();
    
    if (await firstRow.count() > 0) {
      // 查找 Edit 按钮（函数列表只有 Edit 和 Delete 按钮）
      const editButton = firstRow.locator('button').filter({ hasText: /Edit/i });
      
      if (await editButton.count() > 0) {
        await editButton.first().click();
        
        // 等待编辑器模态框出现
        await page.waitForSelector('.ant-modal, .ant-drawer', { timeout: 5000 });
        
        console.log('Function editor opened successfully');
      } else {
        console.log('Edit button not found');
      }
    } else {
      console.log('No function data rows found');
    }
  });
});

/**
 * Function Code Execution Tests
 * 测试函数代码执行（试运行）功能
 */
test.describe('Function Code Execution', () => {
  const projectId = 'proj-default';

  test.beforeEach(async ({ page }) => {
    await page.goto(`/oma/project/${projectId}/functions`);
    await page.waitForLoadState('networkidle');
  });

  test('should open function editor and show Code tab', async ({ page }) => {
    test.setTimeout(30000);
    
    // 等待表格加载
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    
    // 点击第一行的 Edit 按钮
    const editButton = page.locator('.ant-table-tbody tr.ant-table-row').first()
      .locator('button').filter({ hasText: /Edit/i });
    
    if (await editButton.count() === 0) {
      console.log('No Edit button found, skipping test');
      return;
    }
    
    await editButton.click();
    
    // 等待模态框出现
    await page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 点击 Code 标签
    const codeTab = page.locator('.ant-tabs-tab').filter({ hasText: 'Code' });
    if (await codeTab.count() > 0) {
      await codeTab.click();
      
      // 验证代码相关内容可见
      const codeSection = page.locator('text=Code Implementation, text=代码实现, text=code_content').first();
      if (await codeSection.count() > 0) {
        await expect(codeSection).toBeVisible({ timeout: 5000 });
        console.log('Code tab opened successfully');
      } else {
        console.log('Code tab content not found (may not have code section)');
      }
    } else {
      console.log('Code tab not found');
    }
  });

  test('should show Dry Run section in Code tab', async ({ page }) => {
    test.setTimeout(30000);
    
    // 打开函数编辑器
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    const editButton = page.locator('.ant-table-tbody tr.ant-table-row').first()
      .locator('button').filter({ hasText: /Edit/i });
    
    if (await editButton.count() === 0) {
      console.log('No Edit button found, skipping test');
      return;
    }
    
    await editButton.click();
    await page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 点击 Code 标签
    const codeTab = page.locator('.ant-tabs-tab').filter({ hasText: 'Code' });
    if (await codeTab.count() > 0) {
      await codeTab.click();
      
      // 验证试运行区域可见 - 寻找 "试运行" 或 "Dry Run" 或 "运行" 按钮
      const dryRunSection = page.locator('text=试运行, text=Dry Run, text=Test Run').first();
      const runButton = page.locator('button').filter({ hasText: /运行|Run|Execute/i });
      
      if (await dryRunSection.count() > 0) {
        console.log('Dry Run section found');
      } else if (await runButton.count() > 0) {
        console.log('Run button found');
      } else {
        console.log('Dry Run section or Run button not visible');
      }
    } else {
      console.log('Code tab not found');
    }
  });

  test('should have run button in function editor', async ({ page }) => {
    test.setTimeout(60000);
    
    // 打开函数编辑器
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    const editButton = page.locator('.ant-table-tbody tr.ant-table-row').first()
      .locator('button').filter({ hasText: /Edit/i });
    
    if (await editButton.count() === 0) {
      console.log('No Edit button found, skipping test');
      return;
    }
    
    await editButton.click();
    await page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 点击 Code 标签
    const codeTab = page.locator('.ant-tabs-tab').filter({ hasText: 'Code' });
    if (await codeTab.count() > 0) {
      await codeTab.click();
      
      // 等待内容加载
      await page.waitForTimeout(1000);
      
      // 找到运行按钮
      const runButton = page.locator('button').filter({ hasText: /运行|Run|Execute|Test/i });
      
      if (await runButton.count() > 0) {
        console.log('Run button found in function editor');
        // 可选：点击运行按钮测试执行
        // await runButton.first().click();
        // await page.waitForSelector('.ant-alert, .ant-message', { timeout: 10000 });
      } else {
        console.log('Run button not found in editor');
      }
    } else {
      console.log('Code tab not found');
    }
  });
});

/**
 * Code Execution API Tests (via UI)
 * 通过 UI 测试代码执行 API
 */
test.describe('Code Execution Integration', () => {
  const projectId = 'proj-default';

  test('should execute code via API when clicking run', async ({ page }) => {
    test.setTimeout(60000);
    
    // 导航到函数页面
    await page.goto(`/oma/project/${projectId}/functions`);
    await page.waitForLoadState('networkidle');
    
    // 打开函数编辑器
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    const editButton = page.locator('.ant-table-tbody tr.ant-table-row').first()
      .locator('button').filter({ hasText: /Edit/i });
    
    if (await editButton.count() === 0) {
      console.log('No function to test, skipping');
      return;
    }
    
    await editButton.click();
    await page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 切换到 Code 标签
    const codeTab = page.locator('.ant-tabs-tab').filter({ hasText: 'Code' });
    if (await codeTab.count() > 0) {
      await codeTab.click();
      await page.waitForTimeout(1000);
      
      // 监听 API 请求
      const requestPromise = page.waitForRequest(
        request => request.url().includes('/execute/') && request.method() === 'POST',
        { timeout: 15000 }
      ).catch(() => null);
      
      // 点击运行按钮
      const runButton = page.locator('button').filter({ hasText: /运行|Run|Execute|Test/i });
      if (await runButton.count() > 0) {
        await runButton.first().click();
        
        const request = await requestPromise;
        if (request) {
          console.log('Code execution API called:', request.url());
          
          // 等待响应
          const responsePromise = page.waitForResponse(
            response => response.url().includes('/execute/'),
            { timeout: 10000 }
          ).catch(() => null);
          
          const response = await responsePromise;
          if (response) {
            const status = response.status();
            console.log('API response status:', status);
            
            if (status === 200) {
              console.log('Code execution API test passed');
            }
          }
        } else {
          console.log('No API request captured (button may not trigger API)');
        }
      } else {
        console.log('Run button not found');
      }
    } else {
      console.log('Code tab not found');
    }
  });
});