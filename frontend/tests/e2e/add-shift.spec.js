import { test, expect } from '@playwright/test';
import { login } from './helpers/auth.js';
import { api } from '../../js/api.js';

test('user can add a shift', async ({ page }) => {
  await login(page);

  await page.getByRole('button', { name: /add shift/i }).click();

  await expect(page.locator('#modal')).toBeVisible();

  await page.locator('#m_date').fill('2126-07-18');
  await page.locator('#m_planned').fill('08:00-16:00');
  await page.locator('#m_actual').fill('08:05-16:15');
  await page.locator('#m_latest_child_name').fill('Test Child');
  await page.locator('#m_latest_child_time').fill('15:55');
  await page.locator('#m_note').fill('Playwright test');

  await page.locator('#save-btn').click();

  await expect(page.locator('#modal')).toBeHidden();

  // Open the page that loads GET /api/v0.2/periods
  await page.getByRole('button', { name: /show all/i }).click();
  await page.waitForLoadState('networkidle');

  // Expand the future period
  await page.locator('[data-period-key="2126-07-15-2126-08-04"]').click();

  // Now the shift card is rendered
  const shifts = page.locator('#shifts');

  await expect(shifts).toContainText('07/18/2126');
  await expect(shifts).toContainText('08:05-16:15');

  //
  // ---- Backend verification (authenticated browser) ----
  //

  const url = api('/periods');

  const periods = await page.evaluate(async (url) => {
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

    return response.json();
  }, url);

  const shift = periods
    .flatMap((period) => period.shifts)
    .find((s) => s.date === '2126-07-18');

  expect(shift).toBeTruthy();

  expect(shift.planned).toBe('08:00-16:00');
  expect(shift.actual).toBe('08:05-16:15');
  expect(shift.latest_child_name).toBe('Test Child');
  expect(shift.latest_child_time).toBe('15:55');
  expect(shift.note).toBe('Playwright test');

  //
  // ---- Cleanup ----
  //

  const deleteButton = page.locator('.ask-delete-btn').last();
  await expect(deleteButton).toBeVisible();

  await deleteButton.click();

  // Confirm deletion.
  await page.locator('.delete-btn').click();

  // Wait until refresh completes.
  await page.waitForLoadState('networkidle');

  // Verify the shift is gone.
  await expect(page.locator('#shifts')).not.toContainText('07/18/2126');
});
