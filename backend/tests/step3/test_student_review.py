"""Student review tests for find_orders_by_sku (CA-3.4).

Your tests must pass against tiendita.repositories.orders_repo.find_orders_by_sku
and fail with AssertionError against steps/03-sql/buggy_snapshot.py.
"""

from __future__ import annotations

from typing import Any

import psycopg

from tiendita.repositories import orders_repo

find_orders_fn = orders_repo.find_orders_by_sku


# SOLUTION_START
def test_excludes_cancelled_orders(seeded_db: psycopg.Connection[Any]) -> None:
    rows = find_orders_fn(seeded_db, "SKU-001")
    statuses = {r["status"] for r in rows}
    assert "cancelled" not in statuses, "Los pedidos cancelados no deben aparecer."


def test_blocks_sql_injection(seeded_db: psycopg.Connection[Any]) -> None:
    payload = "' OR '1'='1"
    rows = find_orders_fn(seeded_db, payload)
    assert rows == [], "Una inyección SQL no debe devolver pedidos."
# SOLUTION_REPLACE
# # TODO (CA-3.4): escribe tests que fallen contra buggy_snapshot.py y pasen con tu corrección:
# # 1. Verificar que los pedidos con status='cancelled' no aparezcan.
# # 2. Verificar que un SKU con "' OR '1'='1" no devuelva filas.
# def test_placeholder(seeded_db: psycopg.Connection[Any]) -> None:
#     assert seeded_db is not None
# SOLUTION_END
