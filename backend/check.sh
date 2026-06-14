#!/bin/bash

DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest
uv run ruff check .
uv run mypy .