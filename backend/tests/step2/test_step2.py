"""Step 2 automated checks (CA-2.1 to CA-2.7)."""

from __future__ import annotations

import inspect
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

from tiendita import catalog, categories, fulfillment, order_status, pricing, search

ROOT = Path(__file__).resolve().parents[3]
PRODUCTS_CSV = ROOT / "data" / "products.csv"


def test_ca_2_1_pricing_cents_half_up_and_coupons() -> None:
    assert pricing.round_half_up_percent(105, 10) == 11, (
        "CA-2.1: 10% de 105 centavos es 10.5 y con redondeo half-up debe dar 11."
    )
    assert pricing.round_half_up_percent(104, 10) == 10, (
        "CA-2.1: 10% de 104 centavos es 10.4 y debe dar 10."
    )

    items = [
        pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=2, available_stock=5),
    ]
    coupon = pricing.Coupon(code="BIENVENIDA", percent_off=15, max_discount_cents=5000)
    total = pricing.calculate_order_total(items, coupon=coupon)
    # subtotal = 37000, 15% = 5550 -> capped at 5000 -> total = 32000
    assert total == 32000, (
        f"CA-2.1: Se esperaba total=32000 con tope de cupón de 5000, se obtuvo {total}."
    )

    over_items = [
        pricing.CartItem(sku="SKU-001", unit_price_cents=18500, quantity=10, available_stock=5),
    ]
    with pytest.raises(pricing.OutOfStockError):
        pricing.calculate_order_total(over_items)


def test_ca_2_2_order_status_transitions() -> None:
    assert order_status.can_transition("pending", "paid") is True
    assert order_status.can_transition("paid", "shipped") is True
    assert order_status.can_transition("shipped", "delivered") is True
    assert order_status.can_transition("pending", "cancelled") is True
    assert order_status.can_transition("paid", "cancelled") is True
    assert order_status.can_transition("shipped", "cancelled") is False
    assert order_status.can_transition("pending", "shipped") is False
    assert order_status.transition_status("pending", "paid") == "paid"
    with pytest.raises(order_status.InvalidTransitionError):
        order_status.transition_status("delivered", "pending")


def _run_student_tests_against(fake_module: SimpleNamespace) -> tuple[bool, str]:
    """Run all test_* functions in test_student_order_status against a planted-bug module.

    Requires an AssertionError (or pytest.raises Failed) so ImportError/AttributeError
    never count as a valid bug detection.
    """
    from backend.tests.step2 import test_student_order_status as student_mod

    original = student_mod.os_mod
    student_mod.os_mod = fake_module  # type: ignore[assignment]
    detected = False
    reason = "Ningún test del estudiante falló contra este bug."
    try:
        for name, fn in inspect.getmembers(student_mod, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                fn()
            except AssertionError as exc:
                detected = True
                reason = f"Detectado por {name}: {exc}"
                break
            except Exception as exc:
                reason = f"Error no esperado ({type(exc).__name__}) en {name}: {exc}"
    finally:
        student_mod.os_mod = original
    return detected, reason


def test_ca_2_3_student_tests_catch_planted_bugs() -> None:
    class _BugErr(ValueError):
        pass

    # Bug 1: allows cancelling shipped orders
    def bug1_can(cur: str, tgt: str) -> bool:
        if cur == "shipped" and tgt == "cancelled":
            return True
        return order_status.can_transition(cur, tgt)

    def bug1_trans(cur: str, tgt: str) -> str:
        if not bug1_can(cur, tgt):
            raise _BugErr("invalid")
        return tgt

    # Bug 2: allows skipping paid (pending -> shipped)
    def bug2_can(cur: str, tgt: str) -> bool:
        if cur == "pending" and tgt == "shipped":
            return True
        return order_status.can_transition(cur, tgt)

    def bug2_trans(cur: str, tgt: str) -> str:
        if not bug2_can(cur, tgt):
            raise _BugErr("invalid")
        return tgt

    # Bug 3: allows reviving cancelled orders (cancelled -> pending)
    def bug3_can(cur: str, tgt: str) -> bool:
        if cur == "cancelled" and tgt == "pending":
            return True
        return order_status.can_transition(cur, tgt)

    def bug3_trans(cur: str, tgt: str) -> str:
        if not bug3_can(cur, tgt):
            raise _BugErr("invalid")
        return tgt

    bugs = [
        ("cancelar pedido ya enviado", SimpleNamespace(can_transition=bug1_can, transition_status=bug1_trans, InvalidTransitionError=_BugErr)),
        ("saltar de pending a shipped", SimpleNamespace(can_transition=bug2_can, transition_status=bug2_trans, InvalidTransitionError=_BugErr)),
        ("reabrir pedido cancelado", SimpleNamespace(can_transition=bug3_can, transition_status=bug3_trans, InvalidTransitionError=_BugErr)),
    ]

    for label, fake in bugs:
        detected, detail = _run_student_tests_against(fake)
        assert detected, (
            f"CA-2.3: Tus tests en test_student_order_status.py no detectaron el bug plantado "
            f"'{label}'. {detail}"
        )


def test_ca_2_4_search_big_o_operations() -> None:
    size = 1024
    items = [
        search.ProductRecord(sku=f"SKU-{i:04d}", name=f"P{i}", category="c", price_cents=100, stock=1)
        for i in range(size)
    ]
    target = f"SKU-{size - 1:04d}"

    lin = search.linear_search(items, target)
    assert lin.product is not None and lin.product.sku == target
    assert lin.operations == size, f"CA-2.4: linear_search debe tomar {size} operaciones en el peor caso."

    bin_r = search.binary_search(items, target)
    assert bin_r.product is not None and bin_r.product.sku == target
    max_bin_ops = math.ceil(math.log2(size)) + 1
    assert bin_r.operations <= max_bin_ops, (
        f"CA-2.4: binary_search usó {bin_r.operations} operaciones; máximo O(log n) esperado={max_bin_ops}."
    )

    idx = search.build_sku_index(items)
    dic = search.dict_search(idx, target)
    assert dic.product is not None and dic.product.sku == target
    assert dic.operations == 1, "CA-2.4: dict_search debe tomar 1 operación (O(1))."


def test_ca_2_5_catalog_bug_fixed() -> None:
    loaded = catalog.load_products_csv(PRODUCTS_CSV)
    assert len(loaded.products) == 40
    assert len(loaded.invalid_rows) == 5

    matches = catalog.search_by_name(loaded.products, "  pantalón   chino ")
    assert len(matches) >= 1, (
        "CA-2.5: search_by_name falló al buscar '  pantalón   chino ' (tildes, mayúsculas o espacios). "
        "Revisa backend/tiendita/catalog.py con breakpoint()."
    )


@pytest.mark.extra
def test_ca_2_6_recursive_category_tree() -> None:
    root = categories.CategoryNode(
        name="ropa",
        direct_product_count=0,
        children=[
            categories.CategoryNode(
                name="hombre",
                direct_product_count=1,
                children=[
                    categories.CategoryNode(name="camisas", direct_product_count=4),
                    categories.CategoryNode(name="pantalones", direct_product_count=3),
                ],
            ),
            categories.CategoryNode(name="mujer", direct_product_count=5),
        ],
    )
    assert categories.count_products_in_tree(root) == 13, (
        "CA-2.6 (extendido): El conteo recursivo del árbol debe devolver 13."
    )


@pytest.mark.extra
def test_ca_2_7_fulfillment_fifo_queue() -> None:
    q = fulfillment.FulfillmentQueue()
    q.enqueue(101)
    q.enqueue(102)
    q.enqueue(103)
    assert q.pending_count() == 3
    assert q.dequeue() == 101, "CA-2.7 (extendido): La cola FIFO debe despachar primero el 101."
    assert q.dequeue() == 102
    assert q.dequeue() == 103
    assert q.dequeue() is None
