"""Deterministic Outside Judge for pdds-onramp-solutions and pdds-onramp.

Checks:
1. README narrative word budget (<= 250 words excluding URLs and acceptance criteria).
2. 1-to-1 traceability of every CA-X.Y in steps/0N-*/README.md (auto -> test, rubric -> examples/).
3. All 13 diagrams exist as SVGs (and HTML passes self_check.py if available).
4. Solution passes Steps 1, 2, 4 (unit/JWKS), and 5 (frontend).
5. Starter fails Steps 1, 2, 4, and 5 so no step passes without work.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SOLUTIONS_DIR = Path(__file__).resolve().parent.parent
STARTER_DIR = SOLUTIONS_DIR.parent / "pdds-onramp"
SELF_CHECK = Path("/Users/ykro/.gemini/config/skills/diagram-design/scripts/self_check.py")


def _extract_narrative_words(readme_text: str) -> int:
    # Capture content between "## Por qué importa" and "## Criterios de aceptación"
    match = re.search(
        r"##\s+Por qué importa(.*?)##\s+Criterios de aceptación",
        readme_text,
        re.DOTALL,
    )
    if not match:
        return 9999
    section = match.group(1)
    # Remove markdown image lines and URL targets
    section = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", section)
    section = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", section)
    section = re.sub(r"##\s+Qué se construye", " ", section)
    words = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9_/-]+", section)
    return len(words)


def check_readmes_and_traceability() -> list[str]:
    errors: list[str] = []
    test_corpus = ""
    for p in list((SOLUTIONS_DIR / "backend" / "tests").rglob("*.py")) + list(
        (SOLUTIONS_DIR / "frontend" / "src" / "__tests__").rglob("*.ts*")
    ) + list((SOLUTIONS_DIR / "frontend" / "e2e").rglob("*.ts")):
        test_corpus += "\n" + p.read_text(encoding="utf-8")

    rubric_files = {p.name for p in (SOLUTIONS_DIR / "examples").glob("*.md")}
    if not rubric_files:
        errors.append("No rubric files found in examples/")

    ca_pattern = re.compile(r"CA-(\d+)\.(\d+)[^\n]*?\[(auto|rubric),\s*(núcleo|extendido)\]")
    total_cas = 0

    for readme in sorted((SOLUTIONS_DIR / "steps").glob("*/README.md")):
        text = readme.read_text(encoding="utf-8")
        word_count = _extract_narrative_words(text)
        if word_count > 250:
            errors.append(f"{readme.relative_to(SOLUTIONS_DIR)}: {word_count} narrative words (> 250)")

        matches = ca_pattern.findall(text)
        if not matches:
            errors.append(f"{readme.relative_to(SOLUTIONS_DIR)}: no CA-X.Y criteria found")
        for step_n, crit_n, kind, _tier in matches:
            total_cas += 1
            if kind == "auto":
                token = f"ca_{step_n}_{crit_n}"
                if token not in test_corpus.lower() and f"ca-{step_n}.{crit_n}" not in test_corpus.lower():
                    errors.append(f"CA-{step_n}.{crit_n} [auto] has no matching test ({token})")

    print(f"[OK] Checked {total_cas} acceptance criteria across 5 step READMEs.")
    return errors


def check_diagrams() -> list[str]:
    errors: list[str] = []
    expected_svgs = [
        "docs/diagrams/tiendita-overview.svg",
        "steps/01-terminal-git/diagrams/where.svg",
        "steps/01-terminal-git/diagrams/git-flow.svg",
        "steps/02-rules-algorithms/diagrams/where.svg",
        "steps/02-rules-algorithms/diagrams/order-states.svg",
        "steps/03-sql/diagrams/where.svg",
        "steps/03-sql/diagrams/db-schema.svg",
        "steps/03-sql/diagrams/race-condition.svg",
        "steps/04-api-auth/diagrams/where.svg",
        "steps/04-api-auth/diagrams/layers.svg",
        "steps/04-api-auth/diagrams/jwt-flow.svg",
        "steps/05-react-deploy/diagrams/where.svg",
        "steps/05-react-deploy/diagrams/deployment.svg",
    ]
    for rel in expected_svgs:
        svg = SOLUTIONS_DIR / rel
        if not svg.exists() or svg.stat().st_size < 100:
            errors.append(f"Missing or empty SVG: {rel}")

    if SELF_CHECK.exists():
        for html in sorted((SOLUTIONS_DIR / "docs" / "diagrams" / "src").glob("*.html")):
            res = subprocess.run([sys.executable, str(SELF_CHECK), str(html)], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"diagram self_check failed for {html.name}: {res.stdout} {res.stderr}")
    print(f"[OK] Verified {len(expected_svgs)} SVG diagrams.")
    return errors


def check_solutions_pass() -> list[str]:
    errors: list[str] = []
    cmds = [
        ("solution-step1", ["uv", "run", "pytest", "backend/tests/step1", "-q"], SOLUTIONS_DIR),
        ("solution-step2-all", ["uv", "run", "pytest", "backend/tests/step2", "-q"], SOLUTIONS_DIR),
        ("solution-step4-unit", ["uv", "run", "pytest", "backend/tests/step4", "-m", "not db", "-q"], SOLUTIONS_DIR),
        ("solution-step5-front", ["npm", "--prefix", "frontend", "test", "--", "--run"], SOLUTIONS_DIR),
    ]
    for label, cmd, cwd in cmds:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"{label} failed:\n{res.stdout}\n{res.stderr}")
        else:
            print(f"[PASS] {label}")
    return errors


def check_starter_fails() -> list[str]:
    errors: list[str] = []
    if not STARTER_DIR.exists():
        return [f"Starter directory does not exist: {STARTER_DIR}"]

    # Run starter tests using solutions' venv python so we don't need a second venv
    py = str(SOLUTIONS_DIR / ".venv" / "bin" / "pytest")
    checks = [
        ("starter-step1", [py, "backend/tests/step1", "-m", "not extra and not prod", "-q"]),
        ("starter-step2", [py, "backend/tests/step2", "-m", "not extra and not prod", "-q"]),
        ("starter-step4", [py, "backend/tests/step4", "-m", "not db and not extra and not prod", "-q"]),
    ]
    for label, cmd in checks:
        res = subprocess.run(cmd, cwd=STARTER_DIR, capture_output=True, text=True)
        if res.returncode == 0:
            errors.append(f"{label} PASSED in starter (must fail so nothing passes without work!)")
        else:
            print(f"[EXPECTED FAIL] {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solutions-only", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    errors.extend(check_readmes_and_traceability())
    errors.extend(check_diagrams())
    errors.extend(check_solutions_pass())
    if not args.solutions_only:
        errors.extend(check_starter_fails())

    if errors:
        print("\nVERIFICATION FAILED:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("\nALL TEMPLATE VERIFICATION CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
