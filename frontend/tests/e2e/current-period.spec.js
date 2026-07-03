import { test, expect } from '@playwright/test';
import { login } from './helpers/auth.js';

test('current period is displayed', async ({ page }) => {
  await login(page);

  await expect(page.locator('#period')).not.toHaveText('');
  await expect(page.locator('#balance')).not.toHaveText('');
});
