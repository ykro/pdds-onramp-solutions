"""PostgreSQL repository for products, orders, transactions, and idempotency."""

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


def place_order(
    conn: psycopg.Connection[Any],
    user_id: str,
    sku: str,
    quantity: int,
    idempotency_key: str | None = None,
) -> OrderSummary:
    """Atomically lock stock with SELECT ... FOR UPDATE, deduct inventory, and create an order."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    # SOLUTION_START
    with conn.transaction():
        if idempotency_key:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT o.id, o.user_id, o.status, o.total_cents
                    FROM idempotency_keys ik
                    JOIN orders o ON o.id = ik.order_id
                    WHERE ik.key = %s
                    """,
                    (idempotency_key,),
                )
                existing = cur.fetchone()
                if existing is not None:
                    return OrderSummary(
                        id=int(existing["id"]),
                        user_id=str(existing["user_id"]),
                        status=str(existing["status"]),
                        total_cents=int(existing["total_cents"]),
                    )

        with conn.cursor() as cur:
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

            if idempotency_key:
                cur.execute(
                    """
                    INSERT INTO idempotency_keys (key, user_id, order_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (key) DO NOTHING
                    RETURNING order_id
                    """,
                    (idempotency_key, user_id, order_id),
                )
                inserted = cur.fetchone()
                if inserted is None:
                    # Another concurrent request won the race: rollback our insert by raising
                    # and let caller fetch the committed order.
                    raise psycopg.errors.UniqueViolation("concurrent idempotency key")

            return OrderSummary(
                id=order_id,
                user_id=str(order_row["user_id"]),
                status=str(order_row["status"]),
                total_cents=int(order_row["total_cents"]),
            )
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa place_order con SELECT ... FOR UPDATE")
    # SOLUTION_END


def place_order_idempotent(
    conn: psycopg.Connection[Any],
    user_id: str,
    sku: str,
    quantity: int,
    idempotency_key: str | None = None,
) -> OrderSummary:
    """Wrapper that handles concurrent UniqueViolation on idempotency_key cleanly."""
    # SOLUTION_START
    from db.bootstrap.base_order import create_order_for_step4

    try:
        try:
            return place_order(conn, user_id, sku, quantity, idempotency_key=idempotency_key)
        except NotImplementedError:
            # Allow Step 4 extended (CA-4.7) to run independently of Step 3
            return create_order_for_step4(
                conn, user_id, sku, quantity, idempotency_key=idempotency_key
            )
    except psycopg.errors.UniqueViolation:
        if not idempotency_key:
            raise
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.id, o.user_id, o.status, o.total_cents
                FROM idempotency_keys ik
                JOIN orders o ON o.id = ik.order_id
                WHERE ik.key = %s
                """,
                (idempotency_key,),
            )
            existing = cur.fetchone()
            if existing is None:
                raise
            return OrderSummary(
                id=int(existing["id"]),
                user_id=str(existing["user_id"]),
                status=str(existing["status"]),
                total_cents=int(existing["total_cents"]),
            )
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO (extendido): maneja UniqueViolation para idempotencia")
    # SOLUTION_END


def find_orders_by_sku(conn: psycopg.Connection[Any], sku: str) -> list[dict[str, Any]]:
    """Return active (non-cancelled) orders containing sku using a parameterized query."""
    # SOLUTION_START
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
    # SOLUTION_REPLACE
    # # BUG del PR a revisar: concatena SQL y no filtra pedidos cancelados
    # with conn.cursor() as cur:
    #     cur.execute(
    #         f"SELECT o.id, o.user_id, o.status, o.total_cents FROM orders o "
    #         f"JOIN order_items oi ON oi.order_id = o.id "
    #         f"JOIN products p ON p.id = oi.product_id WHERE p.sku = '{sku}'"
    #     )
    #     return list(cur.fetchall())
    # SOLUTION_END


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

    def create_order(
        self,
        user_id: str,
        sku: str,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> OrderSummary:
        with get_connection(self._dsn) as conn:
            return place_order_idempotent(
                conn, user_id, sku, quantity, idempotency_key=idempotency_key
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

    def is_admin(self, user_id: str) -> bool:
        with get_connection(self._dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
            return cur.fetchone() is not None

    def restock_product(self, sku: str, delta: int) -> dict[str, Any]:
        with get_connection(self._dsn) as conn:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE products
                    SET stock = stock + %s
                    WHERE sku = %s
                    RETURNING sku, name, category, price_cents, stock
                    """,
                    (delta, sku),
                )
                row = cur.fetchone()
                if row is None:
                    raise KeyError(f"Unknown SKU: {sku}")
                return dict(row)
