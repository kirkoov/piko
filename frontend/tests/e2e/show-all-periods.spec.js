import { test, expect } from '@playwright/test';
import { login } from './helpers/auth.js';

test('Show All displays multiple periods', async ({ page }) => {
  await login(page);

  await page.click('#toggle-shifts');

  await expect(page.locator('#toggle-shifts')).toHaveText(
    /Show current period/i
  );

  await expect(page.locator('#period-title')).toContainText(/All shifts/i);

  // await expect(page.locator('#shifts h3')).toHaveCount(1);
  await expect(page.locator('.shift-card').first()).toBeVisible();
});
