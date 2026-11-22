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
    assert pricing.round_half_up_percent(10**17 + 5, 10) == 10**16 + 1, (
        "CA-2.1: usa solo int; con float se pierden centavos en montos grandes."
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


def _student_test_functions() -> list:
    student_file = ROOT / "backend" / "tests" / "step2" / "test_student_pricing.py"
    raw = student_file.read_text(encoding="utf-8")
    assert "TODO" not in raw, (
        "CA-2.3: Completa tus 3 tests en backend/tests/step2/test_student_pricing.py "
        "y quita los TODO."
    )
    from backend.tests.step2 import test_student_pricing as student_mod

    return [
        fn
        for name, fn in inspect.getmembers(student_mod, inspect.isfunction)
        if name.startswith("test_")
    ]


def _failures(test_fns: list) -> list[str]:
    failed = []
    for fn in test_fns:
        try:
            fn()
        except KeyboardInterrupt:
            raise
        except BaseException:  # noqa: BLE001 - pytest.fail y pytest.raises lanzan BaseException
            failed.append(fn.__name__)
    return failed


def test_ca_2_3_student_pricing_tests_exist_and_pass() -> None:
    test_fns = _student_test_functions()
    assert len(test_fns) >= 3, (
        "CA-2.3: Escribe al menos 3 funciones test_* en test_student_pricing.py "
        f"(actuales={len(test_fns)})."
    )
    failed = _failures(test_fns)
    assert not failed, f"CA-2.3: Estas pruebas tuyas fallan con tu pricing.py actual: {failed}."


def test_ca_2_3_student_tests_fail_on_buggy_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cada prueba útil debe ponerse en rojo cuando reaparece uno de los tres bugs del paso."""
    test_fns = _student_test_functions()
    original_total = pricing.calculate_order_total

    def banker_rounding(amount_cents: int, percent: int) -> int:
        return int(round(amount_cents * (percent / 100.0)))

    def total_without_cap(items, coupon=None):  # type: ignore[no-untyped-def]
        if coupon is not None:
            coupon = pricing.Coupon(coupon.code, coupon.percent_off, None)
        return original_total(items, coupon=coupon)

    def total_without_stock_check(items, coupon=None):  # type: ignore[no-untyped-def]
        relaxed = [
            pricing.CartItem(
                i.sku, i.unit_price_cents, i.quantity, max(i.quantity, i.available_stock)
            )
            for i in items
        ]
        return original_total(relaxed, coupon=coupon)

    buggy_versions = {
        "redondeo bancario con float en round_half_up_percent": (
            "round_half_up_percent",
            banker_rounding,
        ),
        "cupón sin tope max_discount_cents": ("calculate_order_total", total_without_cap),
        "venta sin revisar inventario (sin OutOfStockError)": (
            "calculate_order_total",
            total_without_stock_check,
        ),
    }
    missed = []
    for label, (attr, fake) in buggy_versions.items():
        with monkeypatch.context() as m:
            m.setattr(pricing, attr, fake)
            if not _failures(test_fns):
                missed.append(label)
    assert not missed, (
        "CA-2.3: Tus pruebas siguen en verde cuando reaparece este bug: "
        + "; ".join(missed)
        + ". Escribe una prueba con un caso que lo exponga."
    )
