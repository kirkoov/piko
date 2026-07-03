import { test, expect } from '@playwright/test';

test('user can log out', async ({ page }) => {
  // Login
  await page.goto('/login.html');

  await page.fill('#username', 'Lora');
  await page.fill('#password', 'change_me');

  await page.click('#login-btn');

  await expect(page).toHaveURL(/\/$/);

  // Sanity check
  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
    .not.toBeNull();

  await Promise.all([
    page.waitForURL('**/login.html'),
    page.click('#logout-btn'),
  ]);

  // Local storage should be cleared
  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
    .toBeNull();

  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('user_name')))
    .toBeNull();
});
