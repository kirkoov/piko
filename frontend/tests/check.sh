#!/usr/bin/env bash
set -e

cd ../../backend

echo "Recreating database for Playwright..."

rm -f tests/test.db

DATABASE_URL=sqlite+aiosqlite:///./tests/test.db \
./init_db.sh tests/test.db

# echo "Starting FastAPI..."

cd ../frontend/tests

npx prettier --write ..

npm --prefix .. test

npx playwright test --config=../playwright.config.js