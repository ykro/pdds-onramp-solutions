"""Recursive category tree traversal (Step 2 extended)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CategoryNode:
    name: str
    direct_product_count: int = 0
    children: list[CategoryNode] = field(default_factory=list)


def count_products_in_tree(node: CategoryNode) -> int:
    """Recursively return total products in this category and all subcategories."""
    # SOLUTION_START
    total = node.direct_product_count
    for child in node.children:
        total += count_products_in_tree(child)
    return total
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa count_products_in_tree en categories.py")
    # SOLUTION_END
