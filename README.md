# Hord Manager

Treasure Management, Currency Conversion, and Banking for TTRPGs.

## Overview

Hord Manager is a local web application for hosting and managing tabletop RPG (TTRPG) games. It provides tools for tracking player wealth, banking, currency and precious metal conversion, and business management, all accessible via a web server on your local network. The app is designed for both players and GMs, with password-protected GM controls.

## Key Features

- Player wealth tracking (metals, gemstones, art, real estate, businesses)
- Currency and precious metal value conversion (oz gold as base unit)
- Web scraping of real-world metal prices for up-to-date values
- Banking system with deposits, withdrawals, and loans
- Business management and investment
- Net worth breakdowns and visualizations (pie/line charts)
- Session-based time tracking
- GM screen for approvals, settings, and player management
- Local network accessibility
- Cross-platform packaging (.app for Linux, .exe for Windows)

## Development Checklist (Summary)

- Backend web server and API
- Frontend framework and UI
- User authentication and session management
- Database setup and data models
- Web scraping for metal prices
- Currency, metal, and gemstone management
- Player pages: Treasure Horde, Banking, Business, Net Worth
- Currency and metal price graphs
- GM screen: currency/denomination management, approvals, inbox, session counter
- Packaging and deployment for Linux and Windows
- Testing and documentation

See `docs/DEV_CHECKLIST.md` for the full development checklist and progress tracking.

## Getting Started

Backend quick start (development) using backend-local venv:

1. Create virtual environment (optional but recommended)
2. Install dependencies from `backend/requirements.txt`
3. Run the API with uvicorn

Example commands:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Or use the backend helper script (recreates venv only for backend/):

```bash
cd backend
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
uvicorn app.main:app --reload
```

Root-level unified virtual environment (preferred as project grows):

```bash
chmod +x setup_env.sh
./setup_env.sh
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

Then visit: <http://127.0.0.1:8000> and API docs at <http://127.0.0.1:8000/docs>.

Note: Frontend implementation pending.

### New Convenience Runner

Instead of remembering the uvicorn invocation you can use the helper script added at the project root:

```bash
python run_api.py
```

Environment variables:

```bash
HOST=0.0.0.0 PORT=9001 RELOAD=0 python run_api.py
```

Defaults: HOST=127.0.0.1, PORT=8000, RELOAD=1.

This loads the app via its package path (`backend.app.main:app`) so relative imports work, avoiding the "attempted relative import with no known parent package" error you get if you run `backend/app/main.py` directly.

Planned: a Makefile target (`make dev`) or VS Code task pointing to this script.

## Tooling & Quality

Ruff lint:

```bash
source .venv/bin/activate
ruff check .
```

Type check (mypy):

```bash
mypy .
```

Run tests:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

### Database Migrations (Alembic)

Alembic is used for database schema migrations.

Initial apply (fresh dev environment):

```bash
alembic upgrade head
```

If you already have a local `app.db` created before migrations were added and want to align without recreating:

```bash
alembic stamp head
```

Generating a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Files:
- `alembic.ini` root config
- `migrations/env.py` environment setup pulling in SQLAlchemy `Base`
- `migrations/versions/` individual revision scripts

If you see ModuleNotFoundError for `backend`, ensure you invoke pytest as a module (`python -m pytest`) so the
`[tool.pytest.ini_options] pythonpath` setting in `pyproject.toml` is respected. Alternatively, set `PYTHONPATH=backend/app`.

## Project Structure (Partial)

```text
backend/
  app/
    core/        # config & db
    models/      # ORM models
    routers/     # API endpoints
    services/    # scraping & domain services
docs/
tests/           # pytest suite
pyproject.toml   # tooling config
requirements.txt # backend deps
```

---

---

**Project under active development.**
