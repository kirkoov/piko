import { test, expect } from '@playwright/test';
import { login } from './helpers/auth.js';

test('Show All displays multiple periods', async ({ page }) => {
  await login(page);

  await expect(page.locator('#toggle-shifts')).toBeVisible();

  // Switch from current period to all periods
  await page.getByRole('button', { name: /show all/i }).click();

  const periodHeaders = page.locator('.period-header');

  await expect(periodHeaders).toHaveCount(3);

  // First seeded period
  const firstHeader = page.locator('[data-period-key="2026-06-08-2026-06-28"]');

  await expect(firstHeader).toBeVisible();
  await firstHeader.click({ trial: true });
  await firstHeader.click();

  const shifts = page.locator('#shifts');

  await expect(shifts).toContainText('06/08/2026');
  await expect(shifts).toContainText('13:30-21:30');
  await expect(shifts).toContainText('06/12/2026');
  await expect(shifts).toContainText('14:30-21:30');

  // Collapse again
  await page.locator('[data-period-key="2026-06-08-2026-06-28"]').click();

  // Second seeded period
  await page.locator('[data-period-key="2026-06-29-2026-07-19"]').click();

  await expect(shifts).toContainText('06/29/2026');
  await expect(shifts).toContainText('14:30-21:30');
  await expect(shifts).toContainText('07/02/2026');
  await expect(shifts).toContainText('14:30-21:30');
});
