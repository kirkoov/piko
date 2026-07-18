#!/usr/bin/env bash
set -e

cd ..

uv run ruff check --fix . && uv run ruff format . && uv run mypy --python-executable "$(uv python find)" .

printf "\n*** Running backend tests ***\n"

export DATABASE_URL="sqlite+aiosqlite:///./tests/test.db"

uv run pytest

rm -f tests/test.db

printf "\n*** Backend checks passed ***\n"