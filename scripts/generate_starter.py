"""Generate the student starter template repo (../pdds-onramp) from pdds-onramp-solutions.

Replaces SOLUTION_START ... SOLUTION_REPLACE ... SOLUTION_END blocks in:
- Python / Bash (# markers)
- SQL (-- markers)
- TypeScript / TSX (// markers)
- Markdown (<!-- SOLUTION_START --> ... <!-- SOLUTION_REPLACE --> ... <!-- SOLUTION_END -->)
"""

from __future__ import annotations

import os
import re
import shutil
import stat
from pathlib import Path

SOLUTIONS_DIR = Path(__file__).resolve().parent.parent
STARTER_DIR = SOLUTIONS_DIR.parent / "pdds-onramp"

IGNORE_DIRS = {
    ".git",
    ".venv",
    ".vercel",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "public",
    "screenshots",
    "playwright-report",
    "test-results",
}

SOLUTIONS_ONLY_FILES = {
    ".github/workflows/monthly-health.yml",
    "scripts/generate_starter.py",
    "scripts/verify_template.py",
}

TEXT_EXTS = {".py", ".sh", ".sql", ".ts", ".tsx", ".md", ".yml", ".yaml", ".json", ".toml", ".css", ".html"}


def strip_solution_blocks(text: str, ext: str) -> str:
    if ext == ".md":
        pattern = re.compile(
            r"<!--\s*SOLUTION_START\s*-->.*?<!--\s*SOLUTION_REPLACE\s*-->\n?(.*?)<!--\s*SOLUTION_END\s*-->",
            re.DOTALL,
        )
        return pattern.sub(lambda m: m.group(1), text)

    prefix = {".sql": "--", ".ts": "//", ".tsx": "//"}.get(ext, "#")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    state = "normal"

    start_tok = f"{prefix} SOLUTION_START"
    replace_tok = f"{prefix} SOLUTION_REPLACE"
    end_tok = f"{prefix} SOLUTION_END"

    for line in lines:
        stripped = line.strip()
        if stripped == start_tok:
            state = "skip"
            continue
        if stripped == replace_tok:
            state = "replace"
            continue
        if stripped == end_tok:
            state = "normal"
            continue

        if state == "normal":
            out.append(line)
        elif state == "replace":
            # Strip leading comment marker while preserving indentation
            idx = line.find(prefix)
            if idx != -1:
                after = line[idx + len(prefix) :]
                if after.startswith(" "):
                    after = after[1:]
                out.append(line[:idx] + after)
            else:
                out.append(line)
    return "".join(out)


def generate() -> None:
    if STARTER_DIR.exists():
        # Preserve .git inside STARTER_DIR if already initialized
        for child in STARTER_DIR.iterdir():
            if child.name == ".git":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        STARTER_DIR.mkdir(parents=True, exist_ok=True)

    transformed_count = 0
    for root, dirs, files in os.walk(SOLUTIONS_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        rel_root = Path(root).relative_to(SOLUTIONS_DIR)
        target_dir = STARTER_DIR / rel_root
        target_dir.mkdir(parents=True, exist_ok=True)

        for fname in files:
            rel_file = (rel_root / fname).as_posix()
            if rel_file in SOLUTIONS_ONLY_FILES or fname == ".DS_Store":
                continue
            src = Path(root) / fname
            dst = target_dir / fname
            if rel_file == "deploy.json":
                dst.write_text('{\n  "app_url": ""\n}\n', encoding="utf-8")
                transformed_count += 1
                continue
            if src.suffix in TEXT_EXTS:
                raw = src.read_text(encoding="utf-8")
                cleaned = strip_solution_blocks(raw, src.suffix)
                if cleaned != raw:
                    transformed_count += 1
                dst.write_text(cleaned, encoding="utf-8")
                # Preserve executable bit
                mode = src.stat().st_mode
                if mode & stat.S_IXUSR:
                    dst.chmod(mode)
            else:
                shutil.copy2(src, dst)

    print(f"Generated starter in {STARTER_DIR} ({transformed_count} files transformed from solutions).")


if __name__ == "__main__":
    generate()
