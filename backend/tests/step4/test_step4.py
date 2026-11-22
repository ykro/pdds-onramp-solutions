"""Step 4 automated checks (CA-4.1 to CA-4.4): authz bugfix, new endpoint, service layer and ADR."""

from __future__ import annotations

import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt.algorithms import RSAAlgorithm

from tiendita.api.app import create_app, get_store_service
from tiendita.api.auth import get_jwk_client
from tiendita.repositories.orders_repo import OrderSummary
from tiendita.services.store_service import StoreService


class _FakeRepo:
    def __init__(self) -> None:
        self.products = [
            {
                "id": 1,
                "sku": "SKU-001",
                "name": "Camisa Oxford",
                "category": "ropa/hombre/camisas",
                "price_cents": 18500,
                "stock": 5,
            }
        ]
        self.orders = [
            {"id": 1, "user_id": "usr_alice", "status": "paid", "total_cents": 18500},
            {"id": 2, "user_id": "usr_bob", "status": "pending", "total_cents": 18500},
        ]

    def list_products(self) -> list[dict[str, Any]]:
        return list(self.products)

    def get_product_by_sku(self, sku: str) -> dict[str, Any] | None:
        for p in self.products:
            if p["sku"] == sku:
                return dict(p)
        return None

    def create_order(self, user_id: str, sku: str, quantity: int) -> OrderSummary:
        order = OrderSummary(
            id=len(self.orders) + 1,
            user_id=user_id,
            status="pending",
            total_cents=18500 * quantity,
        )
        self.orders.append(
            {"id": order.id, "user_id": order.user_id, "status": order.status, "total_cents": order.total_cents}
        )
        return order

    def list_orders_for_user(self, user_id: str) -> list[dict[str, Any]]:
        # Intentionally returns all orders to verify StoreService enforces authorization
        return list(self.orders)


@pytest.fixture(scope="module")
def local_jwks() -> Any:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk["kid"] = "tiendita-test-key"
    public_jwk["use"] = "sig"
    public_jwk["alg"] = "RS256"
    jwks_payload = json.dumps({"keys": [public_jwk]}).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(jwks_payload)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def sign(sub: str, *, exp_offset: int = 300) -> str:
        now = int(time.time())
        return jwt.encode(
            {
                "sub": sub,
                "iss": "https://tiendita.local",
                "aud": "tiendita-api",
                "iat": now,
                "exp": now + exp_offset,
            },
            private_key,
            algorithm="RS256",
            headers={"kid": "tiendita-test-key"},
        )

    yield {"jwks_url": f"http://127.0.0.1:{port}/.well-known/jwks.json", "sign": sign}
    server.shutdown()


def test_ca_4_1_authorization_isolates_user_orders(
    local_jwks: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NEON_AUTH_JWKS_URL", local_jwks["jwks_url"])
    monkeypatch.setenv("JWT_ISSUER", "https://tiendita.local")
    monkeypatch.setenv("JWT_AUDIENCE", "tiendita-api")
    get_jwk_client.cache_clear()

    app = create_app()
    app.dependency_overrides[get_store_service] = lambda: StoreService(_FakeRepo())
    client = TestClient(app)

    assert client.get("/api/orders/mine").status_code == 401
    alice_token = local_jwks["sign"]("usr_alice")
    resp = client.get("/api/orders/mine", headers={"Authorization": f"Bearer {alice_token}"})
    assert resp.status_code == 200
    orders = resp.json()
    assert len(orders) == 1 and orders[0]["user_id"] == "usr_alice", (
        "CA-4.1: GET /api/orders/mine devolvió pedidos de otro usuario. "
        "Revisa el filtro por user_id en backend/tiendita/services/store_service.py."
    )


def test_ca_4_2_get_product_by_sku_across_layers() -> None:
    app = create_app()
    app.dependency_overrides[get_store_service] = lambda: StoreService(_FakeRepo())
    client = TestClient(app)

    ok = client.get("/api/products/SKU-001")
    assert ok.status_code == 200 and ok.json()["sku"] == "SKU-001", (
        f"CA-4.2: GET /api/products/SKU-001 debe devolver 200 con el producto (obtenido={ok.status_code})."
    )

    missing = client.get("/api/products/SKU-NO-EXISTE")
    assert missing.status_code == 404, (
        f"CA-4.2: GET /api/products/SKU-NO-EXISTE debe devolver 404 (obtenido={missing.status_code})."
    )


def test_ca_4_3_service_raises_key_error_without_http() -> None:
    service = StoreService(_FakeRepo())
    assert service.get_product("SKU-001")["sku"] == "SKU-001", (
        "CA-4.3: StoreService.get_product('SKU-001') debe devolver el producto."
    )
    with pytest.raises(KeyError):
        service.get_product("SKU-NO-EXISTE")


ADR_DIR = Path(__file__).resolve().parents[3] / "docs" / "adr"
ADR_SECTIONS = ("contexto", "decisi[oó]n", "alternativas descartadas", "consecuencias")


def test_ca_4_4_adr_has_four_sections() -> None:
    adrs = sorted(ADR_DIR.glob("0001-*.md"))
    assert adrs, "CA-4.4: Falta tu ADR en docs/adr/0001-<tema>.md (modelo en examples/adr.md)."
    text = adrs[0].read_text(encoding="utf-8").lower()
    for section in ADR_SECTIONS:
        assert re.search(rf"^(#+\s*|[-*]\s*\*\*){section}", text, re.MULTILINE), (
            f"CA-4.4: {adrs[0].name} necesita un encabezado '{section}' "
            "(contexto, decisión, alternativas descartadas y consecuencias)."
        )
