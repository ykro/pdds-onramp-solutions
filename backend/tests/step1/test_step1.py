"""Step 1 automated checks (CA-1.1, CA-1.2, CA-1.3)."""

from __future__ import annotations

import os
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "log_report.sh"
LOG_FILE = ROOT / "data" / "access.log"
STORY_FILE = ROOT / "docs" / "stories" / "001-order-history.md"


def test_ca_1_1_script_executable_and_missing_file_exit_code() -> None:
    assert SCRIPT.exists(), "CA-1.1: Falta scripts/log_report.sh. Revisa steps/01-terminal-git/README.md."
    assert os.access(SCRIPT, os.X_OK), (
        "CA-1.1: scripts/log_report.sh no tiene permiso de ejecución. "
        "Corre: chmod +x scripts/log_report.sh"
    )
    res = subprocess.run([str(SCRIPT), "data/does-not-exist.log"], capture_output=True, text=True)
    assert res.returncode == 1, (
        f"CA-1.1: Se esperaba código de salida 1 cuando el archivo no existe, "
        f"pero se obtuvo {res.returncode}."
    )
    ok = subprocess.run([str(SCRIPT), str(LOG_FILE)], capture_output=True, text=True)
    assert ok.returncode == 0, (
        f"CA-1.1: scripts/log_report.sh debe salir con código 0 cuando el archivo existe "
        f"(obtenido={ok.returncode})."
    )


def test_ca_1_2_log_report_counts() -> None:
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    expected_total = len(lines)
    expected_5xx = sum(1 for line in lines if line.split()[3].startswith("5"))
    top3 = [ep for ep, _ in Counter(line.split()[2] for line in lines).most_common(3)]

    res = subprocess.run([str(SCRIPT), str(LOG_FILE)], capture_output=True, text=True)
    assert res.returncode == 0, (
        f"CA-1.2: scripts/log_report.sh falló con código {res.returncode}.\n"
        f"Stderr: {res.stderr.strip()}\nRevisa steps/01-terminal-git/hints/1.md."
    )

    parsed: dict[str, str] = {}
    for line in res.stdout.strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            parsed[k.strip()] = v.strip()

    assert parsed.get("total_requests") == str(expected_total), (
        f"CA-1.2: total_requests esperado={expected_total}, obtenido={parsed.get('total_requests')}. "
        "Prueba: wc -l data/access.log"
    )
    assert parsed.get("errors_5xx") == str(expected_5xx), (
        f"CA-1.2: errors_5xx esperado={expected_5xx}, obtenido={parsed.get('errors_5xx')}. "
        "Prueba: awk '$4 ~ /^5/' data/access.log | wc -l"
    )
    reported_top = [item.split(":")[0] for item in parsed.get("top_endpoints", "").split()]
    assert reported_top == top3, (
        f"CA-1.2: top_endpoints esperado={top3}, obtenido={reported_top}. "
        "Revisa steps/01-terminal-git/hints/2.md."
    )


def test_ca_1_3_user_story_structure() -> None:
    assert STORY_FILE.exists(), (
        "CA-1.3: Falta docs/stories/001-order-history.md. "
        "Revisa examples/historia-y-pr.md."
    )
    text = STORY_FILE.read_text(encoding="utf-8").lower()
    for keyword in ("como", "quiero", "para"):
        assert re.search(rf"\b{keyword}\b", text), (
            f"CA-1.3: La historia de usuario necesita la palabra '{keyword}' (formato Como/Quiero/Para)."
        )
    given_count = len(re.findall(r"\bdado\b", text))
    when_count = len(re.findall(r"\bcuando\b", text))
    then_count = len(re.findall(r"\bentonces\b", text))
    assert min(given_count, when_count, then_count) >= 2, (
        "CA-1.3: Incluye al menos dos criterios de aceptación con Dado / Cuando / Entonces "
        f"(actualmente Dado={given_count}, Cuando={when_count}, Entonces={then_count})."
    )
