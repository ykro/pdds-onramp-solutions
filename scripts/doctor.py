"""Environment diagnostic tool with clear Spanish guidance (make doctor)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def _check_cmd(name: str, fix: str) -> bool:
    path = shutil.which(name)
    if path:
        print(f"[OK]    {name} encontrado en {path}")
        return True
    print(f"[FALTA] {name} no está instalado. Solución: {fix}")
    return False


def main() -> int:
    print("Diagnóstico del entorno de pdds-onramp\n")
    ok = True
    ok &= _check_cmd("python3", "Instala Python 3.12 o abre el repo en GitHub Codespaces.")
    ok &= _check_cmd("uv", "Corre: curl -LsSf https://astral.sh/uv/install.sh | sh")
    ok &= _check_cmd("node", "Instala Node 22 o abre el repo en GitHub Codespaces.")
    ok &= _check_cmd("git", "Instala Git desde https://git-scm.com/")

    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        print("[OK]    DATABASE_URL definida")
    else:
        print("[AVISO] DATABASE_URL no está definida (necesaria desde el Paso 3). Copia .env.example a .env.")

    # Check if template copy is behind upstream (non-blocking)
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
