import { test } from '@playwright/test';
import { login, logout } from './helpers/auth.js';

test('user can log out', async ({ page }) => {
  await login(page);
  await logout(page);
});
