"""Step 2 automated checks (CA-2.1, CA-2.2, CA-2.3)."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest
from tiendita import catalog, pricing

ROOT = Path(__file__).resolve().parents[3]
PRODUCTS_CSV = ROOT / "data" / "products.csv"
STUDENT_TESTS = ROOT / "backend" / "tests" / "step2" / "test_student_pricing.py"

_MUTATION_HARNESS = """
import sys
import pytest
from tiendita import pricing

test_file, mutant = sys.argv[1], sys.argv[2]
original_total = pricing.calculate_order_total

if mutant == "truncate_rounding":
    def truncate_rounding(amount_cents: int, percent: int) -> int:
        return (amount_cents * percent) // 100
    pricing.round_half_up_percent = truncate_rounding
elif mutant == "no_coupon_cap":
    def total_without_cap(items, coupon=None):
        if coupon is not None:
            coupon = pricing.Coupon(coupon.code, coupon.percent_off, None)
        return original_total(items, coupon=coupon)
    pricing.calculate_order_total = total_without_cap
elif mutant == "no_stock_check":
    def total_without_stock_check(items, coupon=None):
        relaxed = [
            pricing.CartItem(
                i.sku, i.unit_price_cents, i.quantity, max(i.quantity, i.available_stock)
            )
            for i in items
        ]
        return original_total(relaxed, coupon=coupon)
    pricing.calculate_order_total = total_without_stock_check

sys.exit(pytest.main(["-q", "--no-header", test_file]))
"""


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
    found_skus = {p.sku for p in matches}
    assert found_skus == {"SKU-003", "SKU-023"}, (
        "CA-2.2: search_by_name('  pantalón   chino ') debe devolver exactamente "
        f"{{'SKU-003', 'SKU-023'}} (obtenido={sorted(found_skus)}). "
        "Revisa backend/tiendita/catalog.py y usa _normalize_text."
    )
    empty = catalog.search_by_name(loaded.products, "producto-inexistente-xyz")
    assert empty == [], (
        "CA-2.2: search_by_name debe devolver [] cuando ningún producto coincide "
        f"(obtenido={len(empty)} resultados)."
    )


def _has_assertion(node: ast.AST) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assert):
            return True
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Attribute) and sub.func.attr == "raises":
                return True
            if isinstance(sub.func, ast.Name) and sub.func.id == "raises":
                return True
    return False


def _validate_student_test_file() -> list[str]:
    raw = STUDENT_TESTS.read_text(encoding="utf-8")
    assert "TODO" not in raw, (
        "CA-2.3: Completa tus 3 tests en backend/tests/step2/test_student_pricing.py "
        "y quita los TODO."
    )
    tree = ast.parse(raw, filename=str(STUDENT_TESTS))
    test_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]
    assert len(test_nodes) >= 3, (
        "CA-2.3: Escribe al menos 3 funciones test_* en test_student_pricing.py "
        f"(actuales={len(test_nodes)})."
    )
    without_assert = [node.name for node in test_nodes if not _has_assertion(node)]
    assert not without_assert, (
        "CA-2.3: Cada función test_* en test_student_pricing.py debe contener un assert "
        f"o pytest.raises (sin verificación: {without_assert})."
    )
    return [node.name for node in test_nodes]


def _run_student_suite(mutant: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", _MUTATION_HARNESS, str(STUDENT_TESTS), mutant],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_ca_2_3_student_pricing_tests_exist_and_pass() -> None:
    _validate_student_test_file()
    res = _run_student_suite()
    assert res.returncode == 0, (
        "CA-2.3: Tus pruebas en test_student_pricing.py fallan con tu pricing.py actual:\n"
        f"{(res.stdout + res.stderr).strip()}"
    )


def test_ca_2_3_student_tests_fail_on_buggy_versions() -> None:
    """Cada prueba útil debe ponerse en rojo cuando reaparece uno de los tres bugs del paso."""
    _validate_student_test_file()
    mutants = {
        "truncamiento en lugar de half-up en round_half_up_percent": "truncate_rounding",
        "cupón sin tope max_discount_cents": "no_coupon_cap",
        "venta sin revisar inventario (sin OutOfStockError)": "no_stock_check",
    }
    missed = []
    for label, mutant in mutants.items():
        res = _run_student_suite(mutant)
        if res.returncode == 0:
            missed.append(label)
    assert not missed, (
        "CA-2.3: Tus pruebas siguen en verde cuando reaparece este bug: "
        + "; ".join(missed)
        + ". Escribe una prueba con un caso que lo exponga."
    )
