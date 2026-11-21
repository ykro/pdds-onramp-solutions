"""Step 3 automated checks against PostgreSQL (CA-3.1, CA-3.2, CA-3.3)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg
import pytest

from tiendita.repositories import orders_repo

ROOT = Path(__file__).resolve().parents[3]
QUERIES_DIR = ROOT / "db" / "queries"
DB_URL = os.environ.get("DATABASE_URL", "")


def _pg_available() -> bool:
    if not DB_URL:
        return False
    try:
        with psycopg.connect(DB_URL, connect_timeout=2):
            return True
    except Exception:
        return False


pytestmark = [
    pytest.mark.db,
    pytest.mark.skipif(not _pg_available(), reason="PostgreSQL DATABASE_URL not available"),
]


def test_ca_3_1_monthly_sales_query(seeded_db: psycopg.Connection[Any]) -> None:
    sql = (QUERIES_DIR / "monthly_sales.sql").read_text(encoding="utf-8")
    with seeded_db.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    assert len(rows) >= 8, (
        "CA-3.1: db/queries/monthly_sales.sql debe devolver las ventas agrupadas por mes (YYYY-MM)."
    )
    assert all(row["revenue_cents"] > 0 and row["order_count"] > 0 for row in rows)


def test_ca_3_2_top_products_query(seeded_db: psycopg.Connection[Any]) -> None:
    sql = (QUERIES_DIR / "top_products.sql").read_text(encoding="utf-8")
    with seeded_db.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    assert len(rows) == 5, (
        f"CA-3.2: db/queries/top_products.sql debe devolver los 5 productos más vendidos (obtenidos={len(rows)})."
    )
    assert rows[0]["units_sold"] >= rows[4]["units_sold"]


def test_ca_3_3_find_orders_blocks_sql_injection_and_cancelled(seeded_db: psycopg.Connection[Any]) -> None:
    active_rows = orders_repo.find_orders_by_sku(seeded_db, "SKU-001")
    assert len(active_rows) > 0, "CA-3.3: find_orders_by_sku debe devolver pedidos activos para SKU-001."
    assert all(r["status"] != "cancelled" for r in active_rows), (
        "CA-3.3: find_orders_by_sku devolvió pedidos cancelados; agrega AND o.status <> 'cancelled'."
    )
    injected = orders_repo.find_orders_by_sku(seeded_db, "' OR '1'='1")
    assert injected == [], (
        "CA-3.3: find_orders_by_sku es vulnerable a inyección SQL. Usa parámetros (%s) en lugar de f-strings."
    )
