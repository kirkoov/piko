import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('/login.html');

  await page.fill('#username', 'Lora');
  await page.fill('#password', 'change_me');

  await page.click('#login-btn');

  await expect(page).toHaveURL(/\/$/);

  await expect
    .poll(async () => page.evaluate(() => localStorage.getItem('user_name')))
    .toBe('Lora');

  await expect
    .poll(async () => page.evaluate(() => localStorage.getItem('access_token')))
    .not.toBeNull();
});
