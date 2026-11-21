"""Catalog CSV loader and product name search."""

from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from tiendita.search import ProductRecord


@dataclass(frozen=True)
class InvalidRow:
    line_number: int
    reason: str
    raw: dict[str, str]


@dataclass(frozen=True)
class LoadResult:
    products: list[ProductRecord]
    invalid_rows: list[InvalidRow]


def load_products_csv(path: Path) -> LoadResult:
    """Parse products.csv, rejecting invalid rows with an explicit reason."""
    products: list[ProductRecord] = []
    invalid: list[InvalidRow] = []

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_number, row in enumerate(reader, start=2):
            sku = (row.get("sku") or "").strip()
            name = (row.get("name") or "").strip()
            category = (row.get("category") or "").strip()
            if not sku:
                invalid.append(InvalidRow(line_number, "missing sku", row))
                continue
            if not name:
                invalid.append(InvalidRow(line_number, "missing name", row))
                continue
            try:
                price_cents = int(row.get("price_cents", ""))
            except ValueError:
                invalid.append(InvalidRow(line_number, "price_cents is not an integer", row))
                continue
            if price_cents < 0:
                invalid.append(InvalidRow(line_number, "negative price_cents", row))
                continue
            try:
                stock = int(row.get("stock", ""))
            except ValueError:
                invalid.append(InvalidRow(line_number, "stock is not an integer", row))
                continue
            if stock < 0:
                invalid.append(InvalidRow(line_number, "negative stock", row))
                continue
            products.append(
                ProductRecord(
                    sku=sku,
                    name=name,
                    category=category,
                    price_cents=price_cents,
                    stock=stock,
                )
            )
    return LoadResult(products=products, invalid_rows=invalid)


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(without_accents.lower().split())


def search_by_name(products: list[ProductRecord], query: str) -> list[ProductRecord]:
    """Find products matching query ignoring case, accents, and extra whitespace."""
    needle = _normalize_text(query)
    if not needle:
        return []
    return [p for p in products if needle in _normalize_text(p.name)]
