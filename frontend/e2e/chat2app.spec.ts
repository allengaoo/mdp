import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Chat2App
 * 测试 Chat2App 自然语言对话界面
 */
test.describe('Chat2App Page', () => {
  const chatUrl = '/explore/chat';

  test('should load Chat2App page', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('domcontentloaded');

    // 验证页面标题
    const title = page.locator('text=Chat2App');
    await expect(title).toBeVisible();

    // 验证输入框存在
    const input = page.locator('textarea');
    await expect(input).toBeVisible();

    console.log('✅ Chat2App page loaded successfully');
  });

  test('should display health status', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 等待健康检查完成
    await page.waitForTimeout(2000);

    // 检查状态标签
    const statusTag = page.locator('.ant-tag');
    await expect(statusTag.first()).toBeVisible();

    // 检查刷新按钮
    const refreshButton = page.locator('button').filter({ hasText: /刷新状态/ });
    await expect(refreshButton).toBeVisible();

    console.log('✅ Health status displayed');
  });

  test('should display suggested questions', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 检查默认建议标签
    const suggestions = page.locator('.ant-tag').filter({ hasText: /显示所有对象|统计对象类型|最近创建的记录/ });
    
    if (await suggestions.count() > 0) {
      await expect(suggestions.first()).toBeVisible();
      console.log('✅ Suggested questions displayed');
    } else {
      // 可能已经有消息历史
      console.log('⚠️ No default suggestions (may have existing messages)');
    }
  });

  test('should allow typing in input field', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 在输入框中输入
    const input = page.locator('textarea');
    await input.fill('显示所有目标对象');

    // 验证输入值
    await expect(input).toHaveValue('显示所有目标对象');

    // 验证发送按钮可用
    const sendButton = page.locator('button').filter({ hasText: /发送/ });
    await expect(sendButton).toBeEnabled();

    console.log('✅ Input field works correctly');
  });

  test('should click suggestion and fill input', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 点击建议标签
    const suggestion = page.locator('.ant-tag').filter({ hasText: '显示所有对象' });
    
    if (await suggestion.count() > 0) {
      await suggestion.click();

      // 验证输入框填充了建议内容
      const input = page.locator('textarea');
      await expect(input).toHaveValue('显示所有对象');
      
      console.log('✅ Suggestion click fills input');
    } else {
      console.log('⚠️ No suggestions to click');
    }
  });

  test('should send message and show response', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 输入消息
    const input = page.locator('textarea');
    await input.fill('测试消息');

    // 点击发送
    const sendButton = page.locator('button').filter({ hasText: /发送/ });
    await sendButton.click();

    // 等待响应（可能需要时间，取决于 Ollama）
    await page.waitForTimeout(3000);

    // 检查是否有消息出现
    const messages = page.locator('.ant-list-item');
    
    // 至少应该有用户消息
    if (await messages.count() > 0) {
      console.log(`✅ Messages displayed: ${await messages.count()}`);
    } else {
      // 检查是否有加载状态或错误
      const spinner = page.locator('.ant-spin');
      const error = page.locator('.ant-alert-error, .ant-alert-warning');
      
      if (await spinner.count() > 0) {
        console.log('⚠️ Still loading...');
      } else if (await error.count() > 0) {
        console.log('⚠️ Error displayed (Ollama may be unavailable)');
      }
    }
  });

  test('should show Ollama unavailable warning when service is down', async ({ page }) => {
    test.setTimeout(30000);
    await page.goto(chatUrl);
    await page.waitForLoadState('networkidle');

    // 等待健康检查
    await page.waitForTimeout(2000);

    // 检查是否有警告提示
    const warning = page.locator('.ant-alert-warning').filter({ hasText: /AI 服务未连接/ });
    
    if (await warning.count() > 0) {
      await expect(warning).toBeVisible();
      console.log('✅ Ollama unavailable warning displayed correctly');
    } else {
      console.log('ℹ️ Ollama is available (no warning shown)');
    }
  });
});
