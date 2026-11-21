"""Step 4 automated checks (CA-4.1 to CA-4.8): layered API, local JWKS, authz, roles, idempotency."""

from __future__ import annotations

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import jwt
import psycopg
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt.algorithms import RSAAlgorithm
from psycopg.rows import dict_row

from db.load import apply_migrations, load_csv_data
from tiendita.api.app import create_app, get_store_service
from tiendita.api.auth import get_jwk_client
from tiendita.repositories.orders_repo import OrderSummary, PostgresStoreRepository
from tiendita.services.store_service import ForbiddenError, StoreService

ROOT = Path(__file__).resolve().parents[3]
ADR_FILE = ROOT / "docs" / "decisions" / "0001-auth.md"
DB_URL = os.environ.get("DATABASE_URL", "")


def _pg_available() -> bool:
    if not DB_URL:
        return False
    try:
        with psycopg.connect(DB_URL, connect_timeout=2):
            return True
    except Exception:
        return False


class _FakeRepo:
    def __init__(self) -> None:
        self.products = [
            {"sku": "SKU-001", "name": "Camisa Oxford", "category": "ropa", "price_cents": 18500, "stock": 5}
        ]
        self.orders = [
            {"id": 1, "user_id": "usr_alice", "status": "paid", "total_cents": 18500},
            {"id": 2, "user_id": "usr_bob", "status": "pending", "total_cents": 18500},
        ]
        self.admins = {"usr_admin"}

    def list_products(self) -> list[dict[str, Any]]:
        return list(self.products)

    def create_order(
        self,
        user_id: str,
        sku: str,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> OrderSummary:
        order = OrderSummary(id=len(self.orders) + 1, user_id=user_id, status="pending", total_cents=18500 * quantity)
        self.orders.append(
            {"id": order.id, "user_id": order.user_id, "status": order.status, "total_cents": order.total_cents}
        )
        return order

    def list_orders_for_user(self, user_id: str) -> list[dict[str, Any]]:
        # Intentionally returns all orders to verify the service enforces authorization
        return list(self.orders)

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins

    def restock_product(self, sku: str, delta: int) -> dict[str, Any]:
        for p in self.products:
            if p["sku"] == sku:
                p["stock"] += delta
                return dict(p)
        raise KeyError(sku)


@pytest.fixture(scope="module")
def local_jwks() -> Any:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
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

    def sign(sub: str, *, exp_offset: int = 300, key: Any = private_key, kid: str = "tiendita-test-key") -> str:
        now = int(time.time())
        return jwt.encode(
            {
                "sub": sub,
                "iss": "https://tiendita.local",
                "aud": "tiendita-api",
                "iat": now,
                "exp": now + exp_offset,
            },
            key,
            algorithm="RS256",
            headers={"kid": kid},
        )

    yield {
        "jwks_url": f"http://127.0.0.1:{port}/.well-known/jwks.json",
        "sign": sign,
        "other_key": other_private_key,
    }
    server.shutdown()


def test_ca_4_2_and_4_3_and_4_4_api_layers_jwt_and_authz(
    local_jwks: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NEON_AUTH_JWKS_URL", local_jwks["jwks_url"])
    monkeypatch.setenv("JWT_ISSUER", "https://tiendita.local")
    monkeypatch.setenv("JWT_AUDIENCE", "tiendita-api")
    get_jwk_client.cache_clear()

    fake_repo = _FakeRepo()
    app = create_app()
    app.dependency_overrides[get_store_service] = lambda: StoreService(fake_repo)
    client = TestClient(app)

    # Health & products
    assert client.get("/api/health").status_code == 200
    assert len(client.get("/api/products").json()) == 1

    # CA-4.3: missing, expired, tampered, wrong-key tokens -> 401
    assert client.get("/api/orders/mine").status_code == 401
    expired = local_jwks["sign"]("usr_alice", exp_offset=-60)
    assert client.get("/api/orders/mine", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    wrong_key = local_jwks["sign"]("usr_alice", key=local_jwks["other_key"])
    assert client.get("/api/orders/mine", headers={"Authorization": f"Bearer {wrong_key}"}).status_code == 401

    # CA-4.4: Alice only sees Alice's orders
    alice_token = local_jwks["sign"]("usr_alice")
    resp = client.get("/api/orders/mine", headers={"Authorization": f"Bearer {alice_token}"})
    assert resp.status_code == 200
    orders = resp.json()
    assert len(orders) == 1 and orders[0]["user_id"] == "usr_alice", (
        "CA-4.4: GET /api/orders/mine devolvió pedidos de otro usuario."
    )

    # Create order
    created = client.post(
        "/api/orders",
        json={"sku": "SKU-001", "quantity": 1},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert created.status_code == 201


def test_ca_4_5_adr_has_required_sections() -> None:
    assert ADR_FILE.exists(), "CA-4.5: Falta docs/decisions/0001-auth.md."
    text = ADR_FILE.read_text(encoding="utf-8")
    for heading in ("Contexto", "Decisión", "Consecuencias"):
        assert heading in text, f"CA-4.5: El ADR necesita la sección '{heading}'."
    assert len(text.strip()) >= 200, "CA-4.5: El ADR está demasiado corto; explica el porqué."


@pytest.mark.extra
def test_ca_4_6_admin_role_required_for_restock(
    local_jwks: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NEON_AUTH_JWKS_URL", local_jwks["jwks_url"])
    monkeypatch.setenv("JWT_ISSUER", "https://tiendita.local")
    monkeypatch.setenv("JWT_AUDIENCE", "tiendita-api")
    get_jwk_client.cache_clear()

    fake_repo = _FakeRepo()
    app = create_app()
    app.dependency_overrides[get_store_service] = lambda: StoreService(fake_repo)
    client = TestClient(app)

    alice_token = local_jwks["sign"]("usr_alice")
    admin_token = local_jwks["sign"]("usr_admin")

    denied = client.patch(
        "/api/products/SKU-001/stock",
        json={"delta": 5},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert denied.status_code == 403, "CA-4.6 (extendido): Un cliente sin rol admin debe recibir 403."

    ok = client.patch(
        "/api/products/SKU-001/stock",
        json={"delta": 5},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert ok.status_code == 200 and ok.json()["stock"] == 10

    with pytest.raises(ForbiddenError):
        StoreService(fake_repo).restock_product("usr_alice", "SKU-001", 5)


@pytest.mark.extra
def test_ca_4_8_openapi_contract_matches_frontend() -> None:
    app = create_app()
    schema = app.openapi()
    paths = set(schema["paths"].keys())
    required = {"/api/health", "/api/products", "/api/orders", "/api/orders/mine", "/api/products/{sku}/stock"}
    missing = required - paths
    assert not missing, f"CA-4.8 (extendido): Faltan rutas en /api/openapi.json: {missing}"


def _ensure_base_schema(conn: psycopg.Connection[Any]) -> None:
    """Allow Step 4 to run independently even if the student has not completed Step 3."""
    apply_migrations(conn, up_to=1)
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.products') AS p")
        row = cur.fetchone()
    if row is None or row["p"] is None:
        base_sql = (ROOT / "db" / "bootstrap" / "001_base.sql").read_text(encoding="utf-8")
        with conn.cursor() as cur:
            cur.execute(base_sql)
        conn.commit()


@pytest.mark.db
@pytest.mark.skipif(not _pg_available(), reason="PostgreSQL DATABASE_URL not available")
def test_ca_4_1_migration_002_preserves_live_data() -> None:
    with psycopg.connect(DB_URL, row_factory=dict_row, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS idempotency_keys, admins, order_items, orders, products CASCADE")

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        _ensure_base_schema(conn)
        load_csv_data(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM orders")
            before = cur.fetchone()["n"]

        apply_migrations(conn, up_to=2)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM orders")
            after = cur.fetchone()["n"]
            cur.execute("SELECT to_regclass('public.admins') AS a, to_regclass('public.idempotency_keys') AS i")
            tables = cur.fetchone()

    assert before == after == 2000, "CA-4.1: La migración 002 perdió filas existentes de orders."
    assert tables["a"] == "admins" and tables["i"] == "idempotency_keys"


@pytest.mark.db
@pytest.mark.extra
@pytest.mark.skipif(not _pg_available(), reason="PostgreSQL DATABASE_URL not available")
def test_ca_4_7_concurrent_idempotency_creates_single_order() -> None:
    with psycopg.connect(DB_URL, row_factory=dict_row, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS idempotency_keys, admins, order_items, orders, products CASCADE")

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        _ensure_base_schema(conn)
        apply_migrations(conn, up_to=2)
        load_csv_data(conn)
        with conn.cursor() as cur:
            cur.execute("UPDATE products SET stock = 10 WHERE sku = 'SKU-001'")
        conn.commit()

    repo = PostgresStoreRepository(DB_URL)

    def send_order(_: int) -> int:
        return repo.create_order("usr_idem", "SKU-001", 1, idempotency_key="idem-key-123").id

    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(send_order, range(2)))

    assert ids[0] == ids[1], (
        f"CA-4.7 (extendido): Dos POST simultáneos con la misma Idempotency-Key deben devolver el mismo order_id ({ids})."
    )
