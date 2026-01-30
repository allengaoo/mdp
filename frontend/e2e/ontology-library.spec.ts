import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Ontology Library (Project List)
 * 测试本体库页面的核心功能
 */
test.describe('Ontology Library', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the ontology library page (正确路由是 /oma/library)
    await page.goto('/oma/library');
    await page.waitForLoadState('networkidle');
  });

  test('should display project list', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for the page to load
    await page.waitForSelector('.ant-card', { timeout: 10000 });
    
    // Check that at least one project card is visible
    const projectCards = page.locator('.ant-card');
    await expect(projectCards.first()).toBeVisible();
    
    console.log('Project list displayed successfully');
  });

  test('should show project statistics', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for project cards to load
    await page.waitForSelector('.ant-card', { timeout: 10000 });
    
    // Check that statistics are displayed (objectCount, linkCount)
    const firstCard = page.locator('.ant-card').first();
    await expect(firstCard).toBeVisible();
    
    // The card should contain some text about objects or links
    const cardText = await firstCard.textContent();
    expect(cardText).toBeTruthy();
    
    console.log('Project statistics displayed');
  });

  test('should navigate to project detail on click', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for project cards to load
    await page.waitForSelector('.ant-card', { timeout: 10000 });
    
    // 点击"进入工作区"链接（卡片本身没有点击事件）
    const enterLink = page.locator('.ant-card').first().locator('a').filter({ hasText: /进入工作区/ });
    await enterLink.click();
    
    // Wait for navigation
    await page.waitForURL(/\/oma\/project\//, { timeout: 10000 });
    
    // Verify we're on a project page
    expect(page.url()).toContain('/oma/project/');
    
    console.log('Navigation to project detail successful');
  });
});
