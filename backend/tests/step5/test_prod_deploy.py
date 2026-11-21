"""Step 5 production smoke test (CA-5.3) with 3 retries for cold starts."""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[3]
DEPLOY_JSON = ROOT / "deploy.json"


def _get_with_retries(url: str, retries: int = 3, delay: float = 4.0) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = httpx.get(url, timeout=15.0, follow_redirects=True)
            if resp.status_code < 500:
                return resp
        except Exception as exc:
            last_exc = exc
        if attempt < retries - 1:
            time.sleep(delay)
    if last_exc:
        raise last_exc
    return resp


@pytest.mark.prod
def test_ca_5_3_production_deployment() -> None:
    assert DEPLOY_JSON.exists(), "CA-5.3: Falta deploy.json en la raíz del repo."
    data = json.loads(DEPLOY_JSON.read_text(encoding="utf-8"))
    app_url = (data.get("app_url") or "").strip().rstrip("/")
    assert app_url.startswith("https://"), (
        'CA-5.3: Agrega tu URL pública de Vercel en deploy.json ({"app_url": "https://tu-app.vercel.app"}).'
    )

    health = _get_with_retries(f"{app_url}/api/health")
    assert health.status_code == 200, f"CA-5.3: /api/health devolvió {health.status_code}."

    products = _get_with_retries(f"{app_url}/api/products")
    assert products.status_code == 200 and len(products.json()) >= 1, (
        f"CA-5.3: /api/products debe devolver productos desde Neon (status={products.status_code})."
    )

    protected = _get_with_retries(f"{app_url}/api/orders/mine")
    assert protected.status_code == 401, (
        f"CA-5.3: /api/orders/mine sin token debe devolver 401, devolvió {protected.status_code}."
    )

    front = _get_with_retries(f"{app_url}/")
    assert front.status_code == 200 and "<html" in front.text.lower(), (
        f"CA-5.3: El frontend en / no cargó correctamente (status={front.status_code})."
    )
