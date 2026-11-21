"""Vercel Python serverless entrypoint for Tiendita FastAPI + built React SPA."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from tiendita.api.app import app  # noqa: E402

STATIC_DIR = ROOT / "backend" / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
