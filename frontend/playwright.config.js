import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',

  use: {
    baseURL: 'http://127.0.0.1:8000',
    headless: true,
  },
  // });

  webServer: {
    command:
      'DATABASE_URL=sqlite+aiosqlite:///./tests/test.db uv run uvicorn app.main:app --reload',
    url: 'http://127.0.0.1:8000',
    cwd: '../backend',
    reuseExistingServer: false,
  },
});
