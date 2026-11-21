"""SKU search strategies for Big-O comparison (linear, binary, hash table)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductRecord:
    sku: str
    name: str
    category: str
    price_cents: int
    stock: int


@dataclass
class SearchResult:
    product: ProductRecord | None
    operations: int


def linear_search(products: list[ProductRecord], target_sku: str) -> SearchResult:
    """Scan products one by one and count comparisons."""
    # SOLUTION_START
    ops = 0
    for product in products:
        ops += 1
        if product.sku == target_sku:
            return SearchResult(product=product, operations=ops)
    return SearchResult(product=None, operations=ops)
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa linear_search en search.py")
    # SOLUTION_END


def binary_search(sorted_products: list[ProductRecord], target_sku: str) -> SearchResult:
    """Binary search over products sorted ascending by sku, counting comparisons."""
    # SOLUTION_START
    low = 0
    high = len(sorted_products) - 1
    ops = 0
    while low <= high:
        mid = (low + high) // 2
        ops += 1
        mid_sku = sorted_products[mid].sku
        if mid_sku == target_sku:
            return SearchResult(product=sorted_products[mid], operations=ops)
        if mid_sku < target_sku:
            low = mid + 1
        else:
            high = mid - 1
    return SearchResult(product=None, operations=ops)
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa binary_search en search.py")
    # SOLUTION_END


def build_sku_index(products: list[ProductRecord]) -> dict[str, ProductRecord]:
    """Build a dictionary keyed by SKU for O(1) lookup."""
    # SOLUTION_START
    return {product.sku: product for product in products}
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa build_sku_index en search.py")
    # SOLUTION_END


def dict_search(index: dict[str, ProductRecord], target_sku: str) -> SearchResult:
    """Lookup a SKU in the dictionary index in O(1)."""
    # SOLUTION_START
    return SearchResult(product=index.get(target_sku), operations=1)
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa dict_search en search.py")
    # SOLUTION_END
