#!/usr/bin/env bash
set -e

cd ..

zip -r piko.zip piko \
	-x \
	"*.db" \
	"*.sqlite" \
	"*.pyc" \
	"*.pyo" \
	"*.zip" \
	"*/.git/*" \
	"*/.venv/*" \
	"*/venv/*" \
	"*/node_modules/*" \
	"*/__pycache__/*" \
	"*/.pytest_cache/*" \
	"*/.mypy_cache/*" \
	"*/.ruff_cache/*" \
	"*/.coverage" \
	"*/htmlcov/*" \
	"*/playwright-report/*" \
	"*/test-results/*" \
	"*/dist/*" \
	"*/build/*" \
	"*/coverage/*" \
	"*/.vscode/*" \
	"*/.idea/*" \
	"*/.DS_Store"z \
	"piko/*.sh"
