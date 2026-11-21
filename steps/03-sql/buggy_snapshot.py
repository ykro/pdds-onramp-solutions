"""Immutable buggy snapshot used by Step 3 tests (CA-3.4).

This file intentionally contains two bugs from the PR under review:
1. SQL injection via string concatenation.
2. Does not exclude cancelled orders.
"""

from __future__ import annotations

from typing import Any

import psycopg


def find_orders_by_sku(conn: psycopg.Connection[Any], sku: str) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT o.id, o.user_id, o.status, o.total_cents FROM orders o "
            f"JOIN order_items oi ON oi.order_id = o.id "
            f"JOIN products p ON p.id = oi.product_id WHERE p.sku = '{sku}'"
        )
        return list(cur.fetchall())
