"""Ejemplo resuelto para el Paso 2.

Muestra cómo modelar reglas de precios usando enteros en centavos (`int`),
mantener funciones puras sin efectos secundarios y escribir pruebas con `pytest`
capaces de atrapar errores comunes de redondeo y límites.

Ejecuta este archivo directamente con:
    pytest steps/02-rules-algorithms/example/discount_example.py
"""

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class Coupon:
    code: str
    percent_off: int = 0
    fixed_off_cents: int = 0
    min_subtotal_cents: int = 0


def calculate_discount_cents(subtotal_cents: int, coupon: Coupon | None) -> int:
    """Calcula el descuento en centavos enteros sin dejar que supere el subtotal."""
    if subtotal_cents < 0:
        raise ValueError("El subtotal no puede ser negativo")
    if coupon is None or subtotal_cents < coupon.min_subtotal_cents:
        return 0
    if not (0 <= coupon.percent_off <= 100):
        raise ValueError("El porcentaje debe estar entre 0 y 100")
    if coupon.fixed_off_cents < 0:
        raise ValueError("El descuento fijo no puede ser negativo")

    percent_discount = (subtotal_cents * coupon.percent_off + 50) // 100
    raw_discount = percent_discount + coupon.fixed_off_cents
    return min(raw_discount, subtotal_cents)


def calculate_total_cents(
    subtotal_cents: int,
    coupon: Coupon | None = None,
    tax_percent: int = 12,
) -> int:
    """Aplica primero el cupón y luego calcula el impuesto sobre la base descontada."""
    if tax_percent < 0:
        raise ValueError("El impuesto no puede ser negativo")
    discount = calculate_discount_cents(subtotal_cents, coupon)
    taxable_base = subtotal_cents - discount
    tax = (taxable_base * tax_percent + 50) // 100
    return taxable_base + tax


def test_percent_coupon_rounds_half_up_without_float() -> None:
    coupon = Coupon(code="DIEZ", percent_off=10)
    # 10% de 1055 centavos = 105.5 -> redondea a 106 centavos
    assert calculate_discount_cents(1055, coupon) == 106


def test_fixed_coupon_never_produces_negative_total() -> None:
    coupon = Coupon(code="REGALO50", fixed_off_cents=5000)
    assert calculate_total_cents(3200, coupon=coupon, tax_percent=12) == 0


def test_coupon_respects_exact_minimum_threshold() -> None:
    coupon = Coupon(code="MIN1000", fixed_off_cents=200, min_subtotal_cents=1000)
    # Si alguien cambia `<` por `<=`, este test falla de inmediato.
    assert calculate_discount_cents(999, coupon) == 0
    assert calculate_discount_cents(1000, coupon) == 200


def test_negative_subtotal_raises_value_error() -> None:
    with pytest.raises(ValueError):
        calculate_total_cents(-100)
