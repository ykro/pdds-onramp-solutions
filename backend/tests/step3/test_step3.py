"""Step 3 automated checks against PostgreSQL (CA-3.1, CA-3.2, CA-3.3)."""

from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import psycopg
import pytest
from tiendita.repositories import orders_repo

ROOT = Path(__file__).resolve().parents[3]
QUERIES_DIR = ROOT / "db" / "queries"
DB_URL = os.environ.get("DATABASE_URL", "")
DATA_DIR = ROOT / "data"


def _read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _expected_monthly() -> list[tuple[str, int, int]]:
    count: Counter[str] = Counter()
    revenue: defaultdict[str, int] = defaultdict(int)
    for order in _read_csv("orders.csv"):
        if order["status"] == "cancelled":
            continue
        month = order["created_at"][:7]
        count[month] += 1
        revenue[month] += int(order["total_cents"])
    return [(m, count[m], revenue[m]) for m in sorted(count)]


def _expected_top5() -> list[tuple[str, int]]:
    active = {o["id"] for o in _read_csv("orders.csv") if o["status"] != "cancelled"}
    units: Counter[str] = Counter()
    for item in _read_csv("order_items.csv"):
        if item["order_id"] in active:
            units[item["sku"]] += int(item["quantity"])
    return sorted(units.items(), key=lambda kv: (-kv[1], kv[0]))[:5]


pytestmark = [pytest.mark.db]


def test_ca_3_1_monthly_sales_query(seeded_db: psycopg.Connection[Any]) -> None:
    sql = (QUERIES_DIR / "monthly_sales.sql").read_text(encoding="utf-8")
    with seeded_db.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    got = [(r["month"], int(r["order_count"]), int(r["revenue_cents"])) for r in rows]
    expected = _expected_monthly()
    assert got == expected, (
        "CA-3.1: db/queries/monthly_sales.sql no coincide con las ventas activas por mes. "
        f"Primeras filas esperadas: {expected[:2]}; obtenidas: {got[:2]}. "
        "Si tus números son más altos, revisa qué pedidos estás contando."
    )


def test_ca_3_2_top_products_query(seeded_db: psycopg.Connection[Any]) -> None:
    sql = (QUERIES_DIR / "top_products.sql").read_text(encoding="utf-8")
    with seeded_db.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    got = [(r["sku"], int(r["units_sold"])) for r in rows]
    expected = _expected_top5()
    assert got == expected, (
        "CA-3.2: db/queries/top_products.sql debe devolver los 5 productos con más unidades "
        f"vendidas en pedidos activos. Esperado: {expected}; obtenido: {got}."
    )


class _SpyConnection:
    """Wrap the real connection and record the SQL text each execute() receives."""

    def __init__(self, conn: psycopg.Connection[Any]) -> None:
        self._conn = conn
        self.sql: list[str] = []

    def cursor(self, *args: Any, **kwargs: Any) -> Any:
        spy = self
        real = self._conn.cursor(*args, **kwargs)

        class _Cursor:
            def __enter__(self) -> Any:
                real.__enter__()
                return self

            def __exit__(self, *exc: Any) -> Any:
                return real.__exit__(*exc)

            def execute(self, query: Any, params: Any = None, **kw: Any) -> Any:
                spy.sql.append(str(query))
                return real.execute(query, params, **kw)

            def __getattr__(self, name: str) -> Any:
                return getattr(real, name)

        return _Cursor()


def test_ca_3_3_find_orders_blocks_sql_injection_and_cancelled(
    seeded_db: psycopg.Connection[Any],
) -> None:
    spy = _SpyConnection(seeded_db)
    active_rows = orders_repo.find_orders_by_sku(spy, "SKU-001")  # type: ignore[arg-type]
    assert len(active_rows) > 0, (
        "CA-3.3: find_orders_by_sku debe devolver pedidos activos para SKU-001."
    )
    assert all(r["status"] != "cancelled" for r in active_rows), (
        "CA-3.3: find_orders_by_sku devolvió pedidos que el negocio ya no cuenta. Revisa su estado."
    )
    assert spy.sql and all("SKU-001" not in sql for sql in spy.sql), (
        "CA-3.3: el SKU aparece pegado dentro del texto SQL. Pásalo aparte como parámetro (%s); "
        "escapar comillas no basta."
    )
    injected = orders_repo.find_orders_by_sku(spy, "' OR '1'='1")  # type: ignore[arg-type]
    assert injected == [], (
        "CA-3.3: find_orders_by_sku es vulnerable a inyección SQL. Usa parámetros (%s) en lugar de f-strings."
    )
