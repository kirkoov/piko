import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',

  use: {
    baseURL: 'http://127.0.0.1:8000',
    headless: true,
  },

  workers: 1, // E2E tests share a SQLite test database.
  // Run serially to avoid cross-test interference.

  webServer: {
    command:
      // 'DATABASE_URL=sqlite+aiosqlite:///./tests/test.db uv run uvicorn app.main:app --reload',
      'DATABASE_URL=sqlite+aiosqlite:///../frontend/tests/test.db uv run uvicorn app.main:app',
    url: 'http://127.0.0.1:8000',
    cwd: '../backend',
    reuseExistingServer: true,
  },
});
