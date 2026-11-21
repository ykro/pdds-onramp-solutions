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


def test_ca_1_1_script_validates_missing_file() -> None:
    assert SCRIPT.exists(), "CA-1.1: Falta scripts/log_report.sh."
    assert os.access(SCRIPT, os.X_OK), (
        "CA-1.1: scripts/log_report.sh necesita permiso de ejecución (chmod +x scripts/log_report.sh)."
    )
    missing = subprocess.run([str(SCRIPT), "data/does-not-exist.log"], capture_output=True, text=True)
    assert missing.returncode == 1 and "not found" in missing.stderr.lower(), (
        "CA-1.1: Cuando el archivo no existe debe imprimir un error con 'not found' en stderr "
        f"y salir con código 1 (returncode={missing.returncode}, stderr={missing.stderr.strip()!r})."
    )
    ok = subprocess.run([str(SCRIPT), str(LOG_FILE)], capture_output=True, text=True)
    assert ok.returncode == 0, (
        f"CA-1.1: Cuando el archivo existe debe salir con código 0, se obtuvo {ok.returncode}."
    )


def test_ca_1_2_log_report_counts_5xx_and_top_endpoints() -> None:
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    expected_total = len(lines)
    expected_5xx = sum(1 for line in lines if line.split()[3].startswith("5"))
    top3 = [ep for ep, _ in Counter(line.split()[2] for line in lines).most_common(3)]

    res = subprocess.run([str(SCRIPT), str(LOG_FILE)], capture_output=True, text=True)
    assert res.returncode == 0, f"CA-1.2: scripts/log_report.sh falló: {res.stderr.strip()}"

    parsed: dict[str, str] = {}
    for line in res.stdout.strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            parsed[k.strip()] = v.strip()

    assert parsed.get("total_requests") == str(expected_total), (
        f"CA-1.2: total_requests esperado={expected_total}, obtenido={parsed.get('total_requests')}."
    )
    assert parsed.get("errors_5xx") == str(expected_5xx), (
        f"CA-1.2: errors_5xx esperado={expected_5xx}, obtenido={parsed.get('errors_5xx')}. "
        "Revisa el patrón de códigos 5xx en scripts/log_report.sh."
    )
    reported_top = [item.split(":")[0] for item in parsed.get("top_endpoints", "").split()]
    assert reported_top == top3, (
        f"CA-1.2: top_endpoints esperado={top3}, obtenido={reported_top}."
    )


def test_ca_1_3_user_story_complete() -> None:
    assert STORY_FILE.exists(), "CA-1.3: Falta docs/stories/001-order-history.md."
    raw = STORY_FILE.read_text(encoding="utf-8")
    assert "TODO" not in raw, (
        "CA-1.3: Completa docs/stories/001-order-history.md y elimina los marcadores TODO."
    )
    text = raw.lower()
    for keyword in ("como", "quiero", "para"):
        assert re.search(rf"\b{keyword}\b", text), (
            f"CA-1.3: La historia de usuario necesita '{keyword}' (formato Como / Quiero / Para)."
        )
    given_n = len(re.findall(r"\bdado\b", text))
    when_n = len(re.findall(r"\bcuando\b", text))
    then_n = len(re.findall(r"\bentonces\b", text))
    assert min(given_n, when_n, then_n) >= 2, (
        "CA-1.3: Incluye al menos dos criterios con Dado / Cuando / Entonces."
    )
