# CrossRename development tasks
# All commands use `uv run`

.PHONY: help test lint format typecheck check clean

# Default target
help:
	@echo "CrossRename dev tasks:"
	@echo ""
	@echo "  make test       Run the test suite"
	@echo "  make lint       Lint with ruff"
	@echo "  make format     Format code with ruff"
	@echo "  make typecheck  Type-check with ty"
	@echo "  make check      Run lint + typecheck (CI pipeline)"
	@echo "  make all        Run format + lint + typecheck + test"
	@echo "  make clean      Remove build artifacts and caches"

# ── Test ─────────────────────────────────────────────────────────────

test:
	PYTHONPATH=src uv run python -m unittest tests.test_sanitize -v

# ── Lint & Format ─────────────────────────────────────────────────────

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

format-check:
	uv run ruff format --check src/ tests/

# ── Type Check ────────────────────────────────────────────────────────

typecheck:
	uv run ty src/

# ── Combined ──────────────────────────────────────────────────────────

check: lint typecheck
	@echo "✓ Lint and type checks passed"

all: format lint typecheck test
	@echo "✓ All checks and tests passed"

# ── Cleanup ───────────────────────────────────────────────────────────

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Clean"
