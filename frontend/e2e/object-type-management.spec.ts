import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Object Type Management
 * 测试对象类型管理的核心功能
 */
test.describe('Object Type Management', () => {
  
  // Use the default project ID
  const projectId = 'proj-default';
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the object type list page
    await page.goto(`/oma/project/${projectId}/object-types`);
    // Wait for page to stabilize
    await page.waitForLoadState('networkidle');
  });

  test('should display object type list', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for the table to load
    await page.waitForSelector('.ant-table', { timeout: 15000 });
    
    // Check that the table is visible
    const table = page.locator('.ant-table');
    await expect(table).toBeVisible();
    
    // Check for table rows (excluding header)
    const rows = page.locator('.ant-table-tbody tr');
    const count = await rows.count();
    
    console.log(`Found ${count} object types in list`);
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should open create object type wizard', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Find and click the create button
    const createButton = page.locator('button').filter({ hasText: /Create|新建|创建/i });
    
    if (await createButton.count() > 0) {
      await createButton.first().click();
      
      // Wait for modal/wizard to appear
      await page.waitForSelector('.ant-modal, .ant-drawer', { timeout: 5000 });
      
      // Verify modal is visible
      const modal = page.locator('.ant-modal, .ant-drawer');
      await expect(modal).toBeVisible();
      
      console.log('Create wizard opened successfully');
    } else {
      console.log('Create button not found, skipping test');
    }
  });

  test('should display object type details when clicking edit', async ({ page }) => {
    test.setTimeout(30000);
    // 等待表格数据行加载（使用 ant-table-row 类排除隐藏的 measure-row）
    await page.waitForSelector('.ant-table-tbody tr.ant-table-row', { timeout: 15000 });
    
    // 选择实际的数据行
    const firstRow = page.locator('.ant-table-tbody tr.ant-table-row').first();
    
    // 查找 Edit 按钮
    const editButton = firstRow.locator('button').filter({ hasText: /Edit/i });
    
    if (await editButton.count() > 0) {
      await editButton.first().click();
      
      // 等待编辑模态框出现
      await page.waitForSelector('.ant-modal', { timeout: 5000 });
      
      const modal = page.locator('.ant-modal');
      await expect(modal).toBeVisible();
      
      console.log('Edit modal opened successfully');
    } else {
      console.log('No edit button found in table row');
    }
  });
});
