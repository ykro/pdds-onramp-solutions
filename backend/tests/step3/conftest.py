"""Shared PostgreSQL fixtures for Step 3 tests."""

from __future__ import annotations

import os
from urllib.parse import urlparse
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
    host = (urlparse(DB_URL).hostname or "").lower()
    if host not in {"localhost", "127.0.0.1", "::1", "db", "postgres"} and not os.environ.get("CI"):
        pytest.fail(
            f"Paso 3: DATABASE_URL apunta a {host}. Este test borra y recrea las tablas, así que solo "
            "corre contra el PostgreSQL local de `make db-up`. Quita la variable o usa la URL local."
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
