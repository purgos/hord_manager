"""Convenience script to run the FastAPI app.

Usage:
  python run_api.py            (development with auto-reload)
  HOST=0.0.0.0 PORT=9000 python run_api.py

Prefer this over executing backend/app/main.py directly, so package-relative
imports resolve correctly.
"""

from __future__ import annotations

import os
import uvicorn


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "1") not in {"0", "false", "False"}
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
