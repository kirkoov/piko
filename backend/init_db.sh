#!/usr/bin/env bash
set -e

DB_FILE="${1:-piko.db}"

rm -f "$DB_FILE"

uv run python init_db.py
uv run python init_with_data.py
