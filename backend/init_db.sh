#!/usr/bin/env bash
set -e

echo "Using DATABASE_URL=${DATABASE_URL:-sqlite+aiosqlite:///./piko.db}"

uv run python init_db.py
uv run python init_with_data.py
