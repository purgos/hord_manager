#!/usr/bin/env bash
set -euo pipefail

# Root environment setup for Hord Manager
# This creates ./.venv at repo root and installs backend requirements.

PYTHON_BIN=${1:-python3}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQ_FILE="$ROOT_DIR/backend/requirements.txt"

if [ ! -f "$REQ_FILE" ]; then
  echo "Requirements file not found: $REQ_FILE" >&2
  exit 1
fi

if [ -d "$VENV_DIR" ]; then
  echo "Removing existing virtual environment at $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

echo "Creating virtual environment with $PYTHON_BIN..."
$PYTHON_BIN -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel

pip install -r "$REQ_FILE"

python - <<'PY'
mods = ["fastapi", "sqlalchemy", "pydantic", "pydantic_settings", "requests", "bs4"]
for m in mods:
    __import__(m)
print("All imports succeeded (root venv).")
PY

echo "Done. Activate with: source .venv/bin/activate"
echo "Run API: uvicorn backend.app.main:app --reload" 2>/dev/null || true
