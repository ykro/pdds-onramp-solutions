"""Shared PostgreSQL fixtures for Step 3 tests."""

from __future__ import annotations

import os
from typing import Any

import psycopg
import pytest
from psycopg.rows import dict_row

from db.load import apply_migrations, load_csv_data

DB_URL = os.environ.get("DATABASE_URL", "")


@pytest.fixture()
def seeded_db() -> Any:
    if not DB_URL:
        pytest.fail(
            "Paso 3: falta DATABASE_URL. Corre `make db-up` y luego `make check STEP=3` "
            "(el Makefile ya apunta al PostgreSQL local)."
        )
    try:
        admin = psycopg.connect(DB_URL, row_factory=dict_row, autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as exc:
        pytest.fail(
            f"Paso 3: no hay conexión a PostgreSQL en {DB_URL}. "
            f"¿Corriste `make db-up` y Docker está abierto? Detalle: {exc}"
        )
    with admin as admin_conn:
        with admin_conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS order_items, orders, products CASCADE")

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        apply_migrations(conn)
        load_csv_data(conn)
        yield conn
