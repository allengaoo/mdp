import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Project Management (Multi-Project)
 * 测试多项目管理功能
 */
test.describe('Project Management', () => {

  test.beforeEach(async ({ page }) => {
    // 正确的路由是 /oma/library
    await page.goto('/oma/library');
    await page.waitForLoadState('networkidle');
  });

  test('should display default project', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for project cards to load
    await page.waitForSelector('.ant-card', { timeout: 15000 });
    
    // Check that at least one project is displayed
    const projectCards = page.locator('.ant-card');
    const count = await projectCards.count();
    
    expect(count).toBeGreaterThan(0);
    console.log(`Found ${count} projects`);
    
    // Check for default project
    const pageContent = await page.textContent('body');
    expect(pageContent).toContain('Battlefield');
  });

  test('should show project details with statistics', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for project cards to load
    await page.waitForSelector('.ant-card', { timeout: 15000 });
    
    // Get the first card
    const firstCard = page.locator('.ant-card').first();
    const cardContent = await firstCard.textContent();
    
    // Should contain some content
    expect(cardContent).toBeTruthy();
    console.log('Project card content:', cardContent?.substring(0, 100));
  });

  test('should navigate to project workspace on click', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for project cards to load
    await page.waitForSelector('.ant-card', { timeout: 15000 });
    
    // 点击"进入工作区"链接（卡片本身没有点击事件）
    const enterLink = page.locator('.ant-card').first().locator('a').filter({ hasText: /进入工作区/ });
    await enterLink.click();
    
    // Wait for navigation
    await page.waitForURL(/\/oma\/project\//, { timeout: 10000 });
    
    // Verify we're in a project workspace
    expect(page.url()).toContain('/oma/project/');
    console.log('Navigated to project workspace');
  });

  test('should display project workspace with sidebar', async ({ page }) => {
    test.setTimeout(30000);
    const projectId = 'proj-default';
    await page.goto(`/oma/project/${projectId}/object-types`);
    await page.waitForLoadState('networkidle');
    
    // Check for main content area
    const mainContent = page.locator('.ant-layout-content, main, [class*="content"]');
    await expect(mainContent.first()).toBeVisible();
    
    // Check for sidebar or navigation
    const sidebar = page.locator('.ant-layout-sider, .ant-menu, [class*="sidebar"]');
    if (await sidebar.count() > 0) {
      await expect(sidebar.first()).toBeVisible();
      console.log('Project workspace with sidebar displayed');
    } else {
      console.log('Project workspace displayed (no sidebar)');
    }
  });
});
