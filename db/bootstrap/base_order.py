"""Bootstrap base order creation so Step 4 extended (CA-4.7) runs independently of Step 3."""

from __future__ import annotations

from typing import Any

import psycopg

from tiendita.pricing import OutOfStockError
from tiendita.repositories.orders_repo import OrderSummary


def create_order_for_step4(
    conn: psycopg.Connection[Any],
    user_id: str,
    sku: str,
    quantity: int,
    idempotency_key: str | None = None,
) -> OrderSummary:
    """Atomic order insert used only if Step 3's place_order has not been implemented yet."""
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
                raise OutOfStockError(f"Out of stock: {sku}")

            total_cents = int(product["price_cents"]) * quantity
            cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product["id"]))
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
                if cur.fetchone() is None:
                    raise psycopg.errors.UniqueViolation("concurrent idempotency key")

            return OrderSummary(
                id=order_id,
                user_id=str(order_row["user_id"]),
                status=str(order_row["status"]),
                total_cents=int(order_row["total_cents"]),
            )
