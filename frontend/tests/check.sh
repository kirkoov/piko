#!/usr/bin/env bash
set -e

echo "Formatting frontend..."

npx prettier --write ..

echo "Recreating frontend Playwright database..."

rm -f test.db

cd ../../backend

DATABASE_URL=sqlite+aiosqlite:///../frontend/tests/test.db \
	./init_db.sh

cd ../frontend/tests

echo "Running frontend unit tests..."

npm --prefix .. test

echo "Running Playwright tests..."

# echo "Frontend DATABASE_URL=$DATABASE_URL"

npx playwright test --config=../playwright.config.js

echo "Frontend checks passed."
