# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: logout.spec.js >> user can log out
- Location: e2e/logout.spec.js:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForURL: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/login.html" until "load"
============================================================
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - heading "KindaGrinda" [level=1] [ref=e2]
  - combobox [ref=e3]:
    - option "Choose language" [selected]
    - option "русский"
    - option "Suomi"
    - option "English"
  - heading "Current period - Lora" [level=2] [ref=e4]
  - generic [ref=e5]: Invalid Date - Invalid Date
  - button "Show all shifts" [ref=e6] [cursor=pointer]
  - heading "Balance" [level=2] [ref=e7]
  - generic [ref=e9]: +211 min (3h 31m)
  - heading "Shifts" [level=2] [ref=e10]
  - button "Add Shift" [ref=e11] [cursor=pointer]
  - button "Logout" [active] [ref=e12] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('user can log out', async ({ page }) => {
  4  |   // Login
  5  |   await page.goto('/login.html');
  6  | 
  7  |   await page.fill('#username', 'Lora');
  8  |   await page.fill('#password', 'change_me');
  9  | 
  10 |   await page.click('#login-btn');
  11 | 
  12 |   await expect(page).toHaveURL(/\/$/);
  13 | 
  14 |   // Sanity check
  15 |   await expect
  16 |     .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
  17 |     .not.toBeNull();
  18 | 
  19 |   await Promise.all([
> 20 |     page.waitForURL('**/login.html'),
     |          ^ Error: page.waitForURL: Test timeout of 30000ms exceeded.
  21 |     page.click('#logout-btn'),
  22 |   ]);
  23 | 
  24 |   // Local storage should be cleared
  25 |   await expect
  26 |     .poll(() => page.evaluate(() => localStorage.getItem('access_token')))
  27 |     .toBeNull();
  28 | 
  29 |   await expect
  30 |     .poll(() => page.evaluate(() => localStorage.getItem('user_name')))
  31 |     .toBeNull();
  32 | });
  33 | 
```