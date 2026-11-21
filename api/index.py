"""Vercel Python serverless entrypoint for Tiendita FastAPI."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from tiendita.api.app import app  # noqa: E402, F401
