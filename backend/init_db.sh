#!/bin/bash

rm piko.db
uv run python init_db.py
uv run python init_with_data.py
