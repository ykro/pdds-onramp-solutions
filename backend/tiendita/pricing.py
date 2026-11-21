"""Money and pricing rules in integer cents (GTQ, 12% IVA included)."""

from __future__ import annotations

from dataclasses import dataclass


class OutOfStockError(ValueError):
    """Raised when requested quantity exceeds available stock."""


@dataclass(frozen=True)
class CartItem:
    sku: str
    unit_price_cents: int
    quantity: int
    available_stock: int


@dataclass(frozen=True)
class Coupon:
    code: str
    percent_off: int
    max_discount_cents: int | None = None


def format_gtq(cents: int) -> str:
    """Format integer cents as Quetzales, e.g. 18550 -> 'Q 185.50'."""
    sign = "-" if cents < 0 else ""
    abs_cents = abs(cents)
    return f"{sign}Q {abs_cents // 100}.{abs_cents % 100:02d}"


def round_half_up_percent(amount_cents: int, percent: int) -> int:
    """Compute round_half_up(amount_cents * percent / 100) using integer arithmetic only."""
    if amount_cents < 0 or percent < 0:
        raise ValueError("amount_cents and percent must be non-negative")
    # SOLUTION_START
    return (amount_cents * percent + 50) // 100
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa round_half_up_percent en pricing.py")
    # SOLUTION_END


def calculate_order_total(items: list[CartItem], coupon: Coupon | None = None) -> int:
    """Validate stock and return total in integer cents after optional coupon."""
    # SOLUTION_START
    subtotal = 0
    for item in items:
        if item.quantity <= 0:
            raise ValueError(f"Invalid quantity for {item.sku}: {item.quantity}")
        if item.unit_price_cents < 0:
            raise ValueError(f"Invalid price for {item.sku}: {item.unit_price_cents}")
        if item.quantity > item.available_stock:
            raise OutOfStockError(
                f"SKU {item.sku}: requested {item.quantity}, available {item.available_stock}"
            )
        subtotal += item.unit_price_cents * item.quantity

    discount = 0
    if coupon is not None:
        if not 0 <= coupon.percent_off <= 100:
            raise ValueError(f"Invalid coupon percent: {coupon.percent_off}")
        discount = round_half_up_percent(subtotal, coupon.percent_off)
        if coupon.max_discount_cents is not None:
            discount = min(discount, coupon.max_discount_cents)

    return max(0, subtotal - discount)
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa calculate_order_total en pricing.py")
    # SOLUTION_END
