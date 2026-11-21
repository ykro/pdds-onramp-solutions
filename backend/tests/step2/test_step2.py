"""Step 2 automated checks (CA-2.1, CA-2.2, CA-2.3)."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from tiendita import catalog, pricing

ROOT = Path(__file__).resolve().parents[3]
PRODUCTS_CSV = ROOT / "data" / "products.csv"


def test_ca_2_1_pricing_exact_cents_and_coupon_cap() -> None:
    assert pricing.round_half_up_percent(105, 10) == 11, (
        "CA-2.1: 10% de 105 centavos es 10.5 y con redondeo half-up debe devolver 11 (entero)."
    )
    assert pricing.round_half_up_percent(104, 10) == 10, (
        "CA-2.1: 10% de 104 centavos debe devolver 10."
    )

    items = [
        pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=2, available_stock=5),
    ]
    coupon = pricing.Coupon(code="BIENVENIDA", percent_off=15, max_discount_cents=5000)
    total = pricing.calculate_order_total(items, coupon=coupon)
    assert total == 32000, (
        f"CA-2.1: Con tope de cupón de 5000 centavos el total debe ser 32000, se obtuvo {total}."
    )

    over = [pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=10, available_stock=5)]
    with pytest.raises(pricing.OutOfStockError):
        pricing.calculate_order_total(over)


def test_ca_2_2_catalog_search_handles_accents_case_and_spaces() -> None:
    loaded = catalog.load_products_csv(PRODUCTS_CSV)
    assert len(loaded.products) == 40
    assert len(loaded.invalid_rows) == 5

    matches = catalog.search_by_name(loaded.products, "  pantalón   chino ")
    assert len(matches) >= 1, (
        "CA-2.2: search_by_name falló al buscar '  pantalón   chino '. "
        "Revisa backend/tiendita/catalog.py y usa _normalize_text."
    )


def test_ca_2_3_student_pricing_tests_exist_and_pass() -> None:
    student_file = ROOT / "backend" / "tests" / "step2" / "test_student_pricing.py"
    raw = student_file.read_text(encoding="utf-8")
    assert "TODO" not in raw, (
        "CA-2.3: Completa tus 3 tests en backend/tests/step2/test_student_pricing.py y quita los TODO."
    )
    from backend.tests.step2 import test_student_pricing as student_mod

    test_fns = [fn for name, fn in inspect.getmembers(student_mod, inspect.isfunction) if name.startswith("test_")]
    assert len(test_fns) >= 3, (
        f"CA-2.3: Escribe al menos 3 funciones test_* en test_student_pricing.py (actuales={len(test_fns)})."
    )
    for fn in test_fns:
        fn()
