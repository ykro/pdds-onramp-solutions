"""PostgreSQL repository for products and orders."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from tiendita.pricing import OutOfStockError


@dataclass(frozen=True)
class OrderSummary:
    id: int
    user_id: str
    status: str
    total_cents: int


def get_connection(dsn: str | None = None) -> psycopg.Connection[Any]:
    """Open a Postgres connection compatible with Neon's transaction pooler."""
    url = dsn or os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tiendita"
    )
    return psycopg.connect(url, row_factory=dict_row, prepare_threshold=None)


def find_orders_by_sku(conn: psycopg.Connection[Any], sku: str) -> list[dict[str, Any]]:
    """Return active (non-cancelled) orders containing sku using a parameterized query."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT o.id, o.user_id, o.status, o.total_cents
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN products p ON p.id = oi.product_id
            WHERE p.sku = %s AND o.status <> 'cancelled'
            ORDER BY o.id ASC
            """,
            (sku,),
        )
        return list(cur.fetchall())


class PostgresStoreRepository:
    """Concrete repository backed by PostgreSQL."""

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn

    def list_products(self) -> list[dict[str, Any]]:
        with get_connection(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, price_cents, stock FROM products ORDER BY sku ASC"
            )
            return list(cur.fetchall())

    def get_product_by_sku(self, sku: str) -> dict[str, Any] | None:
        with get_connection(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, price_cents, stock FROM products WHERE sku = %s",
                (sku,),
            )
            row = cur.fetchone()
            return dict(row) if row is not None else None

    def create_order(self, user_id: str, sku: str, quantity: int) -> OrderSummary:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        with get_connection(self._dsn) as conn:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute(
                    "SELECT id, price_cents, stock FROM products WHERE sku = %s FOR UPDATE",
                    (sku,),
                )
                product = cur.fetchone()
                if product is None:
                    raise KeyError(f"Unknown SKU: {sku}")
                if int(product["stock"]) < quantity:
                    raise OutOfStockError(
                        f"SKU {sku}: requested {quantity}, available {product['stock']}"
                    )

                total_cents = int(product["price_cents"]) * quantity
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (quantity, product["id"]),
                )
                cur.execute(
                    """
                    INSERT INTO orders (user_id, status, total_cents)
                    VALUES (%s, 'pending', %s)
                    RETURNING id, user_id, status, total_cents
                    """,
                    (user_id, total_cents),
                )
                order_row = cur.fetchone()
                assert order_row is not None
                order_id = int(order_row["id"])
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product["id"], quantity, int(product["price_cents"])),
                )
                return OrderSummary(
                    id=order_id,
                    user_id=str(order_row["user_id"]),
                    status=str(order_row["status"]),
                    total_cents=int(order_row["total_cents"]),
                )

    def list_orders_for_user(self, user_id: str) -> list[dict[str, Any]]:
        with get_connection(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, status, total_cents, created_at
                FROM orders
                WHERE user_id = %s
                ORDER BY id DESC
                """,
                (user_id,),
            )
            return list(cur.fetchall())
