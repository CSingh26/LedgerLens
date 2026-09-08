#!/usr/bin/env bash
set -euo pipefail
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/mypy src/ledgerlens
npm run check:js
npm run lint
.venv/bin/python -m build
npm run test:e2e
.venv/bin/python scripts/check_secrets.py
