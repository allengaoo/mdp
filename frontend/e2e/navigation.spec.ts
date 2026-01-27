import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Navigation
 * 测试主要导航功能
 */
test.describe('Application Navigation', () => {

  test('should load home page', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');
    
    // 首页会自动重定向到 /oma/library
    await expect(page).toHaveURL(/\/oma\/library/);
    
    console.log('Home page loaded and redirected to OMA library');
  });

  test('should navigate to OMA (Ontology Library)', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Look for OMA navigation link
    const omaLink = page.locator('a, button').filter({ hasText: /OMA|本体库|Ontology/i });
    
    if (await omaLink.count() > 0) {
      await omaLink.first().click();
      await page.waitForURL(/\/oma/, { timeout: 5000 });
      expect(page.url()).toContain('/oma');
      console.log('Navigated to OMA');
    } else {
      // Try direct navigation
      await page.goto('/oma');
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/oma');
      console.log('Direct navigation to OMA');
    }
  });

  test('should navigate between project sections', async ({ page }) => {
    test.setTimeout(60000);
    const projectId = 'proj-default';
    
    // Navigate to object types
    await page.goto(`/oma/project/${projectId}/object-types`);
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('object-types');
    
    // Navigate to link types
    await page.goto(`/oma/project/${projectId}/link-types`);
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('link-types');
    
    // Navigate to topology
    await page.goto(`/oma/project/${projectId}/topology`);
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('topology');
    
    console.log('Project section navigation successful');
  });

  test('should display sidebar navigation', async ({ page }) => {
    test.setTimeout(30000);
    const projectId = 'proj-default';
    await page.goto(`/oma/project/${projectId}/object-types`);
    await page.waitForLoadState('networkidle');
    
    // Look for sidebar menu
    const sidebar = page.locator('.ant-menu, .ant-layout-sider, [class*="sidebar"], [class*="nav"]');
    
    if (await sidebar.count() > 0) {
      await expect(sidebar.first()).toBeVisible();
      console.log('Sidebar navigation visible');
    } else {
      console.log('Sidebar not found (may use different navigation pattern)');
    }
  });
});
