"""Student tests for pricing.py (CA-2.3)."""

from __future__ import annotations

import pytest
from tiendita import pricing


def test_student_half_up_rounding() -> None:
    assert pricing.round_half_up_percent(105, 10) == 11
    assert pricing.round_half_up_percent(104, 10) == 10


def test_student_coupon_respects_max_discount_cap() -> None:
    items = [pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=2, available_stock=5)]
    coupon = pricing.Coupon(code="BIENVENIDA", percent_off=15, max_discount_cents=5000)
    assert pricing.calculate_order_total(items, coupon=coupon) == 32000


def test_student_rejects_quantity_over_stock() -> None:
    items = [pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=6, available_stock=5)]
    with pytest.raises(pricing.OutOfStockError):
        pricing.calculate_order_total(items)
