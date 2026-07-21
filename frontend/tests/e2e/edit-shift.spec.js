import { test, expect } from '@playwright/test';
import { login } from './helpers/auth';

test('user can edit a shift', async ({ page }) => {
  await login(page);

  const shiftCard = page.locator('.shift-card').first();

  await expect(shiftCard).toBeVisible();

  await shiftCard.locator('.edit-btn').click();

  await expect(page.locator('#modal')).toBeVisible();

  // Modify the shift.

  await page.locator('#m_planned').fill('15:00-21:45');
  await page.locator('#m_actual').fill('15:00-21:45');
  await page.locator('#m_latest_child_name').fill('Playwright Child');
  await page.locator('#m_latest_child_time').fill('21:45');
  await page.locator('#m_note').fill('Edited by Playwright');

  await page.getByRole('button', { name: /save/i }).click();

  // Wait for the dialog to close.
  await expect(page.locator('#modal')).toBeHidden();

  // Wait until the edited card has been re-rendered.
  await expect(shiftCard).toContainText('15:00-21:45');

  // Verify every edited field.
  await expect(shiftCard).toContainText('Playwright Child');
  await expect(shiftCard).toContainText('21:45');
  await expect(shiftCard).toContainText('Edited by Playwright');
});
