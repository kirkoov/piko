// tests/e2e/helpers/auth.js

import { expect } from '@playwright/test';

export async function login(page) {
  await page.addInitScript(() => {
    localStorage.setItem('language', 'en');
  });

  await page.goto('/login.html');

  await page.fill('#username', 'Lora');
  await page.fill('#password', 'change_me');

  await Promise.all([page.waitForURL(/\/$/), page.click('#login-btn')]);

  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
    .not.toBeNull();

  await expect
    .poll(async () => page.evaluate(() => localStorage.getItem('user_name')))
    .toBe('Lora');
}

export async function logout(page) {
  await Promise.all([
    page.waitForURL('**/login.html'),
    page.click('#logout-btn'),
  ]);

  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
    .toBeNull();

  await expect
    .poll(() => page.evaluate(() => localStorage.getItem('user_name')))
    .toBeNull();
}
