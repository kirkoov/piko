import { test } from '@playwright/test';
import { login } from './helpers/auth.js';

test('user can log in', async ({ page }) => {
  await login(page);
});
