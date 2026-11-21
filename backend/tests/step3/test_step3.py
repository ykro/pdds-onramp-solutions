"""Step 3 automated checks against PostgreSQL (CA-3.1 to CA-3.6)."""

from __future__ import annotations

import importlib.util
import inspect
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import psycopg
import pytest
from psycopg.rows import dict_row

from db.load import apply_migrations, load_csv_data
from tiendita.pricing import OutOfStockError
from tiendita.repositories import orders_repo

ROOT = Path(__file__).resolve().parents[3]
QUERIES_DIR = ROOT / "db" / "queries"
BUGGY_SNAPSHOT = ROOT / "steps" / "03-sql" / "buggy_snapshot.py"

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


@pytest.fixture()
def seeded_db() -> Any:
    with psycopg.connect(DB_URL, row_factory=dict_row, autocommit=True) as admin_conn:
        with admin_conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS idempotency_keys, admins, order_items, orders, products CASCADE")

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        apply_migrations(conn, up_to=1)
        load_csv_data(conn)
        yield conn


def test_ca_3_1_constraints_reject_negative_stock(seeded_db: psycopg.Connection[Any]) -> None:
    with pytest.raises(psycopg.errors.CheckViolation):
        with seeded_db.cursor() as cur:
            cur.execute(
                "INSERT INTO products (sku, name, category, price_cents, stock) "
                "VALUES ('SKU-NEG', 'Bad', 'hogar', 1000, -1)"
            )
    seeded_db.rollback()


def test_ca_3_2_sql_queries_return_expected_results(seeded_db: psycopg.Connection[Any]) -> None:
    monthly_sql = (QUERIES_DIR / "monthly_sales.sql").read_text(encoding="utf-8")
    top_sql = (QUERIES_DIR / "top_products.sql").read_text(encoding="utf-8")
    low_sql = (QUERIES_DIR / "low_stock.sql").read_text(encoding="utf-8")

    with seeded_db.cursor() as cur:
        cur.execute(monthly_sql)
        monthly = cur.fetchall()
        assert len(monthly) >= 8, "CA-3.2: monthly_sales.sql debe devolver al menos 8 meses."
        assert all(row["revenue_cents"] > 0 for row in monthly)

        cur.execute(top_sql)
        top = cur.fetchall()
        assert len(top) == 5, "CA-3.2: top_products.sql debe devolver exactamente 5 productos."
        assert top[0]["units_sold"] >= top[4]["units_sold"]

        cur.execute(low_sql)
        low = cur.fetchall()
        assert len(low) >= 5, "CA-3.2: low_stock.sql debe devolver los productos con stock <= 5."
        assert all(row["stock"] <= 5 for row in low)


def test_ca_3_3_concurrent_purchases_sell_only_once(seeded_db: psycopg.Connection[Any]) -> None:
    with seeded_db.cursor() as cur:
        cur.execute("UPDATE products SET stock = 1 WHERE sku = 'SKU-001'")
    seeded_db.commit()

    def attempt(idx: int) -> str:
        with psycopg.connect(DB_URL, row_factory=dict_row, prepare_threshold=None) as conn:
            try:
                orders_repo.place_order(conn, f"usr_race_{idx}", "SKU-001", 1)
                return "ok"
            except OutOfStockError:
                return "out_of_stock"

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(attempt, range(10)))

    assert results.count("ok") == 1, (
        f"CA-3.3: Con stock=1 y 10 compras simultáneas debe haber exactamente 1 venta, "
        f"se obtuvieron {results.count('ok')}."
    )
    assert results.count("out_of_stock") == 9


def test_ca_3_4_code_review_fix_and_student_tests_against_snapshot(seeded_db: psycopg.Connection[Any]) -> None:
    # Ensure fixed implementation works
    active_rows = orders_repo.find_orders_by_sku(seeded_db, "SKU-001")
    assert all(r["status"] != "cancelled" for r in active_rows)
    assert orders_repo.find_orders_by_sku(seeded_db, "' OR '1'='1") == []

    # Load immutable buggy snapshot and confirm student tests fail with AssertionError
    spec = importlib.util.spec_from_file_location("buggy_snapshot", BUGGY_SNAPSHOT)
    assert spec and spec.loader
    buggy_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(buggy_mod)

    from backend.tests.step3 import test_student_review as student_mod

    orig_fn = student_mod.find_orders_fn
    student_mod.find_orders_fn = buggy_mod.find_orders_by_sku
    caught = 0
    try:
        for name, fn in inspect.getmembers(student_mod, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                fn(seeded_db)
            except AssertionError:
                caught += 1
    finally:
        student_mod.find_orders_fn = orig_fn

    assert caught >= 2, (
        f"CA-3.4: Tus tests en test_student_review.py deben detectar con AssertionError "
        f"las 2 fallas de buggy_snapshot.py (detectadas={caught})."
    )


@pytest.mark.extra
def test_ca_3_6_index_migration_and_explain(seeded_db: psycopg.Connection[Any]) -> None:
    apply_migrations(seeded_db, up_to=3)
    with seeded_db.cursor() as cur:
        cur.execute(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'order_items' "
            "AND indexname = 'idx_order_items_product_id'"
        )
        assert cur.fetchone() is not None, (
            "CA-3.6 (extendido): Falta el índice idx_order_items_product_id en db/migrations/003_indexes.sql."
        )
