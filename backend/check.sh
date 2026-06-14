#!/bin/bash

uv run ruff check --fix . && uv run ruff format . && uv run mypy --python-executable "$(uv python find)" .
DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest -v