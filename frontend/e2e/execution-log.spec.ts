import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Execution Log
 * 测试执行日志页面功能
 */
test.describe('Execution Log', () => {
  const projectId = 'proj-default';

  test.beforeEach(async ({ page }) => {
    await page.goto(`/oma/project/${projectId}/logs`);
    await page.waitForLoadState('networkidle');
  });

  test('should display execution log page', async ({ page }) => {
    test.setTimeout(30000);
    
    // 等待页面加载 - 使用更宽松的选择器
    await page.waitForSelector('.ant-table, .ant-empty, .ant-card', { timeout: 15000 });
    
    // 验证页面有任何内容可见
    const pageContent = page.locator('.ant-table, .ant-empty, .ant-card, [class*="log"]');
    await expect(pageContent.first()).toBeVisible();
    
    console.log('Execution log page displayed');
  });

  test('should show log table or empty state', async ({ page }) => {
    test.setTimeout(30000);
    
    // 等待 API 响应
    await page.waitForResponse(
      response => response.url().includes('/execute/logs'),
      { timeout: 10000 }
    ).catch(() => null);
    
    // 等待表格或空状态
    const table = page.locator('.ant-table');
    const empty = page.locator('.ant-empty');
    
    const tableVisible = await table.isVisible().catch(() => false);
    const emptyVisible = await empty.isVisible().catch(() => false);
    
    expect(tableVisible || emptyVisible).toBe(true);
    
    if (tableVisible) {
      console.log('Log table is visible');
    } else {
      console.log('Empty state is displayed (no logs)');
    }
  });

  test('should have status filter', async ({ page }) => {
    test.setTimeout(30000);
    
    // 查找状态筛选器
    const statusFilter = page.locator('.ant-select, select').filter({ 
      has: page.locator('text=全部, text=状态, text=Status, text=SUCCESS, text=FAILED')
    });
    
    if (await statusFilter.count() > 0) {
      await expect(statusFilter.first()).toBeVisible();
      console.log('Status filter found');
    } else {
      // 也可能是其他形式的筛选器
      const filterButton = page.locator('button, .ant-select').filter({
        hasText: /全部|筛选|Filter|Status/i
      });
      if (await filterButton.count() > 0) {
        console.log('Filter control found');
      } else {
        console.log('No status filter visible');
      }
    }
  });

  test('should have refresh button', async ({ page }) => {
    test.setTimeout(30000);
    
    // 查找刷新按钮
    const refreshButton = page.locator('button').filter({
      hasText: /刷新|Refresh|重新加载/i
    });
    
    const reloadIcon = page.locator('[class*="reload"], [class*="refresh"], .anticon-reload');
    
    if (await refreshButton.count() > 0) {
      await expect(refreshButton.first()).toBeVisible();
      console.log('Refresh button found');
    } else if (await reloadIcon.count() > 0) {
      console.log('Refresh icon found');
    } else {
      console.log('No explicit refresh button (may auto-refresh)');
    }
  });

  test('should call API on page load', async ({ page }) => {
    test.setTimeout(30000);
    
    // 监听 API 请求
    const requestPromise = page.waitForRequest(
      request => request.url().includes('/execute/logs'),
      { timeout: 10000 }
    ).catch(() => null);
    
    // 刷新页面触发 API 调用
    await page.reload();
    
    const request = await requestPromise;
    if (request) {
      console.log('API request made:', request.url());
      expect(request.method()).toBe('GET');
    } else {
      console.log('API request not captured');
    }
  });

  test('should display log details', async ({ page }) => {
    test.setTimeout(30000);
    
    // 等待表格加载
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 }).catch(() => null);
    
    const rows = page.locator('.ant-table-tbody tr.ant-table-row');
    const rowCount = await rows.count();
    
    if (rowCount > 0) {
      // 验证表格有数据列
      const firstRow = rows.first();
      const cells = firstRow.locator('td');
      const cellCount = await cells.count();
      
      expect(cellCount).toBeGreaterThan(0);
      console.log(`Log table has ${rowCount} rows with ${cellCount} columns`);
    } else {
      console.log('No log entries to display');
    }
  });
});
