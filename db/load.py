"""Apply SQL migrations and load Tiendita CSV datasets into PostgreSQL."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import psycopg

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from tiendita.catalog import load_products_csv

MIGRATIONS_DIR = ROOT_DIR / "db" / "migrations"
DATA_DIR = ROOT_DIR / "data"


def get_direct_url() -> str:
    return os.environ.get(
        "DIRECT_DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tiendita"),
    )


def apply_migrations(conn: psycopg.Connection, up_to: int = 2) -> None:
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    for sql_file in files:
        prefix = int(sql_file.name.split("_", 1)[0])
        if prefix <= up_to:
            sql = sql_file.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                cur.execute(sql)
            if prefix == 1 and up_to >= 2:
                with conn.cursor() as cur:
                    cur.execute("SELECT to_regclass('public.products')")
                    row = cur.fetchone()
                    exists = (row["to_regclass"] if isinstance(row, dict) else row[0]) if row else None
                if not exists:
                    base_sql = (ROOT_DIR / "db" / "bootstrap" / "001_base.sql").read_text(encoding="utf-8")
                    with conn.cursor() as cur:
                        cur.execute(base_sql)
    conn.commit()


def load_csv_data(conn: psycopg.Connection) -> None:
    loaded = load_products_csv(DATA_DIR / "products.csv")
    sku_to_id: dict[str, int] = {}

    with conn.cursor() as cur:
        for prod in loaded.products:
            cur.execute(
                """
                INSERT INTO products (sku, name, category, price_cents, stock)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (sku) DO UPDATE
                SET name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    price_cents = EXCLUDED.price_cents,
                    stock = EXCLUDED.stock
                RETURNING id
                """,
                (prod.sku, prod.name, prod.category, prod.price_cents, prod.stock),
            )
            row = cur.fetchone()
            assert row is not None
            sku_to_id[prod.sku] = int(row["id"] if isinstance(row, dict) else row[0])

        with (DATA_DIR / "orders.csv").open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                cur.execute(
                    """
                    INSERT INTO orders (id, user_id, status, total_cents, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        int(row["id"]),
                        row["user_id"],
                        row["status"],
                        int(row["total_cents"]),
                        row["created_at"],
                    ),
                )

        with (DATA_DIR / "order_items.csv").open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                cur.execute(
                    """
                    INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_cents)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        int(row["id"]),
                        int(row["order_id"]),
                        sku_to_id[row["sku"]],
                        int(row["quantity"]),
                        int(row["unit_price_cents"]),
                    ),
                )

        cur.execute("SELECT setval('orders_id_seq', COALESCE((SELECT MAX(id) FROM orders), 1))")
        cur.execute("SELECT setval('order_items_id_seq', COALESCE((SELECT MAX(id) FROM order_items), 1))")

    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate and seed Tiendita PostgreSQL database")
    parser.add_argument("--up-to", type=int, default=2, help="Max migration number to apply")
    parser.add_argument("--seed", action="store_true", help="Load CSV data after migrating")
    args = parser.parse_args()

    with psycopg.connect(get_direct_url()) as conn:
        apply_migrations(conn, up_to=args.up_to)
        if args.seed:
            load_csv_data(conn)
    print(f"Migrations up to {args.up_to:03d} applied (seed={args.seed}).")


if __name__ == "__main__":
    main()
