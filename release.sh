#!/usr/bin/env bash
set -euo pipefail

echo "=== Running tests in parallel ==="

(
	cd backend/tests
	./check.sh | sed 's/^/[BACK] /'
) &
BACK_PID=$!

(
	cd frontend/tests
	./check.sh | sed 's/^/[FRONT] /'
) &
FRONT_PID=$!

BACK_RC=0
FRONT_RC=0

wait "$BACK_PID" || BACK_RC=$?
wait "$FRONT_PID" || FRONT_RC=$?

if ((BACK_RC || FRONT_RC)); then
	echo
	echo "❌ Tests failed."
	echo "Backend : $BACK_RC"
	echo "Frontend: $FRONT_RC"
	exit 1
fi

echo "=== Removing caches ==="
find . -type d \( \
	-name "__pycache__" -o \
	-name ".pytest_cache" -o \
	-name ".mypy_cache" -o \
	-name ".ruff_cache" \
	\) -prune -exec rm -rf {} +

find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# OUT="piko-$(date +%Y%m%d).zip"
OUT="piko-$(date +%Y%m%d-%H%M).zip"

echo "=== Package contents ==="
du -sh .

echo "=== Creating $OUT ==="
zip -r "$OUT" . \
	-x \
	"*.zip" \
	"*.log" \
	".git/*" \
	"*/.git/*" \
	".venv/*" \
	"*/.venv/*" \
	"node_modules/*" \
	"*/node_modules/*" \
	"tests/*" \
	"*/tests/*" \
	"test-results/*" \
	"*/test-results/*" \
	"playwright-report/*" \
	"*/playwright-report/*" \
	"coverage/*" \
	"*/coverage/*" \
	"__pycache__/*" \
	"*/__pycache__/*" \
	".pytest_cache/*" \
	"*/.pytest_cache/*" \
	".mypy_cache/*" \
	"*/.mypy_cache/*" \
	".ruff_cache/*" \
	"*/.ruff_cache/*" \
	".vscode/*" \
	".idea/*" \
	"*.DS_Store" \
	"*.swp" \
	"*.swo" \
	"*~" \
	".history/*" \
	"*.sh"

ls -lh "$OUT"

echo
echo "Done."
echo "Created $OUT"
