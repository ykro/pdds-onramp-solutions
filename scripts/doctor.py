"""Environment diagnostic tool with clear Spanish guidance (make doctor)."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent


def _check_cmd(name: str, fix: str) -> bool:
    path = shutil.which(name)
    if path:
        print(f"[OK]    {name} encontrado en {path}")
        return True
    print(f"[FALTA] {name} no está instalado. Solución: {fix}")
    return False


def _check_postgres(db_url: str) -> None:
    parsed = urlparse(db_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    try:
        with socket.create_connection((host, port), timeout=1.5):
            print(f"[OK]    PostgreSQL responde en {host}:{port}")
    except OSError:
        print(f"[AVISO] PostgreSQL no responde en {host}:{port}. Para Pasos 3 y 5 corre: make db-up")


def _check_docker() -> None:
    """Docker solo hace falta para `make db-up` en los Pasos 3 y 5."""
    if not shutil.which("docker"):
        print(
            "[AVISO] Docker no está instalado. Lo necesitas en los Pasos 3 y 5 para levantar "
            "PostgreSQL con make db-up. Instala Docker Desktop desde "
            "https://www.docker.com/products/docker-desktop/ o usa GitHub Codespaces, que ya lo trae."
        )
        return
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10, check=False)
    except subprocess.TimeoutExpired:
        res = None
    if res is not None and res.returncode == 0:
        print("[OK]    Docker está instalado y corriendo")
    else:
        print(
            "[AVISO] Docker está instalado pero no responde. Abre Docker Desktop y espera a que "
            "diga que está corriendo antes de make db-up."
        )


def _check_path(rel_path: str, fix: str) -> None:
    target = ROOT / rel_path
    if target.exists():
        print(f"[OK]    {rel_path} presente")
    else:
        print(f"[AVISO] Falta {rel_path}. Corre: {fix}")


def main() -> int:
    print("Diagnóstico del entorno de pdds-onramp\n")
    ok = True
    ok &= _check_cmd("python3", "Instala Python 3.12 o abre el repo en GitHub Codespaces.")
    ok &= _check_cmd("uv", "Corre: curl -LsSf https://astral.sh/uv/install.sh | sh")
    ok &= _check_cmd("node", "Instala Node 22 o abre el repo en GitHub Codespaces.")
    ok &= _check_cmd("npm", "Instala Node 22 (incluye npm) o abre el repo en GitHub Codespaces.")
    ok &= _check_cmd("git", "Instala Git desde https://git-scm.com/")
    _check_path(".venv", "uv sync")
    _check_path("frontend/node_modules", "cd frontend && npm ci")
    _check_docker()

    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        print("[OK]    DATABASE_URL definida")
        _check_postgres(db_url)
    else:
        print(
            "[AVISO] DATABASE_URL no está definida en tu shell (Makefile usa la base local "
            "por defecto). Para Pasos 3 y 5 corre: make db-up && make migrate"
        )

    try:
        res = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            print(f"[OK]    Repositorio Git activo ({res.stdout.strip()} commits locales)")
    except Exception:
        pass

    print("\nTodo listo para trabajar." if ok else "\nCorrige los elementos marcados con [FALTA] antes de continuar.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
