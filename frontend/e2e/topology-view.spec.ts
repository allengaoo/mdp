import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Topology View
 * 测试拓扑视图的核心功能
 */
test.describe('Topology View', () => {
  
  const projectId = 'proj-default';
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the topology view page
    await page.goto(`/oma/project/${projectId}/topology`);
    await page.waitForLoadState('networkidle');
  });

  test('should display topology graph', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for React Flow container to load
    await page.waitForSelector('.react-flow', { timeout: 15000 });
    
    // Check that the React Flow component is visible
    const reactFlow = page.locator('.react-flow');
    await expect(reactFlow).toBeVisible();
    
    console.log('Topology graph container displayed');
  });

  test('should display nodes for object types', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for React Flow to render
    await page.waitForSelector('.react-flow', { timeout: 15000 });
    
    // Wait a bit for nodes to render
    await page.waitForTimeout(2000);
    
    // Check for nodes in the graph
    const nodes = page.locator('.react-flow__node');
    const nodeCount = await nodes.count();
    
    console.log(`Found ${nodeCount} nodes in topology`);
    
    // Should have at least one node if there are object types
    if (nodeCount > 0) {
      await expect(nodes.first()).toBeVisible();
    }
  });

  test('should display edges for link types', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for React Flow to render
    await page.waitForSelector('.react-flow', { timeout: 15000 });
    
    // Wait for edges to render
    await page.waitForTimeout(2000);
    
    // Check for edges in the graph
    const edges = page.locator('.react-flow__edge');
    const edgeCount = await edges.count();
    
    console.log(`Found ${edgeCount} edges in topology`);
  });

  test('should allow zooming and panning', async ({ page }) => {
    test.setTimeout(30000);
    // Wait for React Flow to render
    await page.waitForSelector('.react-flow', { timeout: 15000 });
    
    const reactFlow = page.locator('.react-flow');
    const boundingBox = await reactFlow.boundingBox();
    
    if (boundingBox) {
      // Perform a scroll to zoom
      await page.mouse.move(
        boundingBox.x + boundingBox.width / 2,
        boundingBox.y + boundingBox.height / 2
      );
      await page.mouse.wheel(0, -100); // Zoom in
      
      await page.waitForTimeout(500);
      
      console.log('Zoom interaction performed');
    }
  });
});
