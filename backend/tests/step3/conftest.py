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
        pytest.skip("PostgreSQL DATABASE_URL not available")
    with psycopg.connect(DB_URL, row_factory=dict_row, autocommit=True) as admin_conn:
        with admin_conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS order_items, orders, products CASCADE")

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        apply_migrations(conn)
        load_csv_data(conn)
        yield conn
