import { test, expect } from '@playwright/test';
import { login } from './helpers/auth.js';
import { formatDate } from '../../js/utils.js';

test('Show All displays multiple periods', async ({ page }) => {
  await login(page);

  await expect(page.locator('#toggle-shifts')).toBeVisible();

  const responsePromise = page.waitForResponse(
    (r) => r.url().includes('/periods') && r.request().method() === 'GET'
  );

  await page.getByRole('button', { name: /show all/i }).click();

  const response = await responsePromise;
  const periods = await response.json();

  expect(periods).toHaveLength(2);

  const firstKey = `${periods[0].period_start}-${periods[0].period_end}`;
  const secondKey = `${periods[1].period_start}-${periods[1].period_end}`;

  const firstHeader = page.locator(`[data-period-key="${firstKey}"]`);

  await expect(firstHeader).toBeVisible();
  await firstHeader.click();

  const shifts = page.locator('#shifts');

  await expect(shifts).toContainText(formatDate(periods[0].shifts[0].date));
  await expect(shifts).toContainText(periods[0].shifts[0].planned);

  const lastShift1 = periods[0].shifts.at(-1);

  await expect(shifts).toContainText(formatDate(lastShift1.date));
  await expect(shifts).toContainText(lastShift1.planned);

  await firstHeader.click();

  const secondHeader = page.locator(`[data-period-key="${secondKey}"]`);

  await expect(secondHeader).toBeVisible();
  await secondHeader.click();

  await expect(shifts).toContainText(formatDate(periods[1].shifts[0].date));
  await expect(shifts).toContainText(periods[1].shifts[0].planned);

  const lastShift2 = periods[1].shifts.at(-1);

  await expect(shifts).toContainText(formatDate(lastShift2.date));
  await expect(shifts).toContainText(lastShift2.planned);
});
