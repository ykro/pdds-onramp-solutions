"""Deterministic dataset generator for Tiendita (seed=42).

Generates:
- data/access.log (10,000 HTTP access log lines)
- data/products.csv (40 valid products + 5 intentionally invalid rows)
- data/users.csv (300 test users)
- data/orders.csv (2,000 orders)
- data/order_items.csv (order line items)
"""

from __future__ import annotations

import csv
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORIES = [
    ("ropa/hombre/camisas", "Camisa Oxford", 18500),
    ("ropa/hombre/camisas", "Camisa Lino", 22000),
    ("ropa/hombre/pantalones", "Pantalon Chino", 27500),
    ("ropa/hombre/pantalones", "Jean Clasico", 31000),
    ("ropa/mujer/blusas", "Blusa Algodon", 16500),
    ("ropa/mujer/blusas", "Blusa Seda", 24000),
    ("ropa/mujer/vestidos", "Vestido Verano", 34500),
    ("ropa/mujer/vestidos", "Vestido Midi", 39000),
    ("calzado/deportivo", "Tenis Runner", 48000),
    ("calzado/deportivo", "Tenis Trail", 56000),
    ("calzado/casual", "Mocasin Cuero", 42000),
    ("calzado/casual", "Bota Urbana", 51000),
    ("hogar/cocina", "Taza Ceramica", 6500),
    ("hogar/cocina", "Termo Acero", 14500),
    ("hogar/cocina", "Prensa Francesa", 19500),
    ("hogar/oficina", "Lampara Escritorio", 21000),
    ("hogar/oficina", "Libreta Puntos", 5500),
    ("hogar/oficina", "Organizador Bambu", 12000),
    ("electronica/audio", "Audifonos Bluetooth", 32000),
    ("electronica/audio", "Bocina Portatil", 28500),
]

ENDPOINTS = [
    ("/api/products", 0.34),
    ("/api/orders", 0.22),
    ("/api/orders/mine", 0.18),
    ("/api/health", 0.14),
    ("/api/products/SKU-001", 0.08),
    ("/api/products/SKU-999", 0.04),
]

STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled"]


def generate_access_log(rng: random.Random, path: Path) -> None:
    start = datetime(2026, 10, 1, 0, 0, 0)
    endpoints = [e for e, _ in ENDPOINTS]
    weights = [w for _, w in ENDPOINTS]
    lines: list[str] = []
    for i in range(10_000):
        ts = start + timedelta(seconds=i * 8 + rng.randint(0, 5))
        ep = rng.choices(endpoints, weights=weights, k=1)[0]
        method = "POST" if ep == "/api/orders" else "GET"
        r = rng.random()
        if ep == "/api/products/SKU-999":
            code = 404
        elif ts.hour == 22 and r < 0.18:
            code = rng.choice([500, 502, 503])
        elif r < 0.025:
            code = rng.choice([500, 502, 503])
        elif r < 0.06:
            code = rng.choice([400, 401, 404])
        else:
            code = 200
        latency_ms = rng.randint(12, 850 if code >= 500 else 180)
        lines.append(
            f"{ts.strftime('%Y-%m-%dT%H:%M:%SZ')} {method} {ep} {code} {latency_ms}ms\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def generate_products(rng: random.Random, path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    idx = 1
    for variant in ("", " Edicion Especial"):
        for cat, base_name, base_price in CATEGORIES:
            sku = f"SKU-{idx:03d}"
            name = f"{base_name}{variant}"
            price_cents = base_price + (2500 if variant else 0)
            stock = rng.choice([2, 4, 8, 15, 25, 40, 60]) if idx > 5 else idx
            rows.append(
                {
                    "sku": sku,
                    "name": name,
                    "category": cat,
                    "price_cents": str(price_cents),
                    "stock": str(stock),
                }
            )
            idx += 1

    # 5 intentionally invalid rows for Step 2 validation
    invalid_rows = [
        {"sku": "", "name": "Producto sin SKU", "category": "hogar/cocina", "price_cents": "1000", "stock": "5"},
        {"sku": "SKU-BAD-1", "name": "", "category": "hogar/cocina", "price_cents": "1000", "stock": "5"},
        {"sku": "SKU-BAD-2", "name": "Precio Negativo", "category": "hogar/cocina", "price_cents": "-500", "stock": "5"},
        {"sku": "SKU-BAD-3", "name": "Stock Negativo", "category": "hogar/cocina", "price_cents": "1500", "stock": "-3"},
        {"sku": "SKU-BAD-4", "name": "Precio Texto", "category": "hogar/cocina", "price_cents": "gratis", "stock": "2"},
    ]

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["sku", "name", "category", "price_cents", "stock"])
        writer.writeheader()
        for row in rows + invalid_rows:
            writer.writerow(row)
    return rows


def generate_users(rng: random.Random, path: Path) -> list[str]:
    user_ids: list[str] = []
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user_id", "email", "role"])
        writer.writeheader()
        for i in range(1, 301):
            uid = f"usr_{i:04d}"
            role = "admin" if i <= 3 else "customer"
            writer.writerow({"user_id": uid, "email": f"user{i:04d}@tiendita.example", "role": role})
            user_ids.append(uid)
    return user_ids


def generate_orders(
    rng: random.Random,
    products: list[dict[str, str]],
    user_ids: list[str],
    orders_path: Path,
    items_path: Path,
) -> None:
    start = datetime(2026, 1, 1, 8, 0, 0)
    orders_rows: list[dict[str, str]] = []
    items_rows: list[dict[str, str]] = []
    item_id = 1

    for order_id in range(1, 2001):
        uid = rng.choice(user_ids)
        created = start + timedelta(hours=rng.randint(0, 24 * 270))
        status = rng.choices(STATUSES, weights=[0.10, 0.20, 0.25, 0.35, 0.10], k=1)[0]
        chosen = rng.sample(products, k=rng.randint(1, 3))
        total_cents = 0
        for prod in chosen:
            qty = rng.randint(1, 4)
            unit_price = int(prod["price_cents"])
            total_cents += unit_price * qty
            items_rows.append(
                {
                    "id": str(item_id),
                    "order_id": str(order_id),
                    "sku": prod["sku"],
                    "quantity": str(qty),
                    "unit_price_cents": str(unit_price),
                }
            )
            item_id += 1
        orders_rows.append(
            {
                "id": str(order_id),
                "user_id": uid,
                "status": status,
                "total_cents": str(total_cents),
                "created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )

    with orders_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "user_id", "status", "total_cents", "created_at"])
        writer.writeheader()
        writer.writerows(orders_rows)

    with items_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "order_id", "sku", "quantity", "unit_price_cents"])
        writer.writeheader()
        writer.writerows(items_rows)


def compute_manifest_hash() -> str:
    h = hashlib.sha256()
    for name in ("access.log", "products.csv", "users.csv", "orders.csv", "order_items.csv"):
        h.update((DATA_DIR / name).read_bytes())
    return h.hexdigest()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    generate_access_log(rng, DATA_DIR / "access.log")
    products = generate_products(rng, DATA_DIR / "products.csv")
    user_ids = generate_users(rng, DATA_DIR / "users.csv")
    generate_orders(rng, products, user_ids, DATA_DIR / "orders.csv", DATA_DIR / "order_items.csv")
    print(f"Generated datasets in {DATA_DIR} (sha256={compute_manifest_hash()[:16]})")


if __name__ == "__main__":
    main()
