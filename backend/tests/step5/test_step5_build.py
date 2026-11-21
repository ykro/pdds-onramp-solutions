"""Step 5 frontend typecheck and build verification (CA-5.1)."""

from __future__ import annotations

import subprocess
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"


def test_ca_5_1_frontend_typecheck_and_build() -> None:
    tsc = subprocess.run(["npx", "tsc", "--noEmit"], cwd=FRONTEND_DIR, capture_output=True, text=True)
    assert tsc.returncode == 0, f"CA-5.1: tsc --noEmit falló.\n{tsc.stdout}\n{tsc.stderr}"
    build = subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, capture_output=True, text=True)
    assert build.returncode == 0, f"CA-5.1: npm run build falló.\n{build.stdout}\n{build.stderr}"
