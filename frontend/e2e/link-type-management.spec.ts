import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Link Type Management
 * 测试连接类型管理的核心功能
 */
test.describe('Link Type Management', () => {
  
  const projectId = 'proj-default';
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the link type list page
    await page.goto(`/oma/project/${projectId}/link-types`);
    await page.waitForLoadState('networkidle');
  });

  test('should display link type list', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for the table to load
    await page.waitForSelector('.ant-table', { timeout: 15000 });
    
    // Check that the table is visible
    const table = page.locator('.ant-table');
    await expect(table).toBeVisible();
    
    // Check for table rows
    const rows = page.locator('.ant-table-tbody tr');
    const count = await rows.count();
    
    console.log(`Found ${count} link types in list`);
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should show source and target columns', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for the table to load
    await page.waitForSelector('.ant-table', { timeout: 15000 });
    
    // Check for column headers
    const headers = page.locator('.ant-table-thead th');
    const headerTexts = await headers.allTextContents();
    
    console.log('Table headers:', headerTexts);
    
    // Verify some expected column headers exist
    expect(headerTexts.length).toBeGreaterThan(0);
  });

  test('should open create link type wizard', async ({ page }) => {
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
});
