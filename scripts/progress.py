"""Visual terminal progress bar across the 5 independent steps (make progress)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS: list[tuple[int, str, list[list[str]]]] = [
    (1, "Terminal, Git y flujo de trabajo", [["uv", "run", "pytest", "backend/tests/step1", "-q"]]),
    (
        2,
        "Reglas de negocio y algoritmos",
        [
            [
                "uv",
                "run",
                "ruff",
                "check",
                "backend/tiendita/pricing.py",
                "backend/tiendita/catalog.py",
                "backend/tiendita/search.py",
                "backend/tests/step2",
            ],
            ["uv", "run", "pytest", "backend/tests/step2", "-q"],
        ],
    ),
    (3, "SQL, modelado y seguridad de consultas", [["uv", "run", "pytest", "backend/tests/step3", "-q"]]),
    (4, "API REST, capas y autorización", [["uv", "run", "pytest", "backend/tests/step4", "-q"]]),
    (
        5,
        "React y TypeScript",
        [
            ["npm", "--prefix", "frontend", "run", "typecheck"],
            ["npm", "--prefix", "frontend", "test", "--", "--run"],
            ["npm", "--prefix", "frontend", "run", "build"],
        ],
    ),
]


def main() -> int:
    print("Progreso en pdds-onramp (cada paso se puede trabajar de forma independiente)\n")
    passed = 0
    for num, title, cmds in STEPS:
        out_parts: list[str] = []
        returncode = 0
        for cmd in cmds:
            res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            out_parts.append((res.stdout or "") + (res.stderr or ""))
            if res.returncode != 0:
                returncode = res.returncode
                break
        out = "\n".join(out_parts)
        if returncode == 0 and "passed" not in out and "skipped" in out:
            badge = "[SKIP]"
        elif returncode == 0:
            passed += 1
            badge = "[PASS]"
        else:
            badge = "[PEND]"
        print(f"  {badge} Paso {num} — {title}")
    print(f"\nCompletados: {passed}/5 pasos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
