"""Student tests for order_status.py (CA-2.3).

Your tests must pass against tiendita.order_status and fail with AssertionError
against three versions with planted bugs.
"""

from __future__ import annotations

import pytest

from tiendita import order_status as os_mod


def test_example_pending_to_paid_is_allowed() -> None:
    """Example test that already passes once can_transition is implemented."""
    assert os_mod.can_transition("pending", "paid") is True


# SOLUTION_START
def test_cannot_cancel_after_shipped_or_delivered() -> None:
    assert os_mod.can_transition("shipped", "cancelled") is False
    assert os_mod.can_transition("delivered", "cancelled") is False
    with pytest.raises(os_mod.InvalidTransitionError):
        os_mod.transition_status("shipped", "cancelled")


def test_cannot_skip_paid_state() -> None:
    assert os_mod.can_transition("pending", "shipped") is False
    assert os_mod.can_transition("pending", "delivered") is False
    with pytest.raises(os_mod.InvalidTransitionError):
        os_mod.transition_status("pending", "shipped")


def test_delivered_and_cancelled_are_terminal() -> None:
    assert os_mod.can_transition("delivered", "paid") is False
    assert os_mod.can_transition("cancelled", "pending") is False
    assert os_mod.can_transition("paid", "cancelled") is True
    assert os_mod.transition_status("paid", "shipped") == "shipped"
# SOLUTION_REPLACE
# # TODO (CA-2.3): escribe tests que detecten:
# # 1. Cancelar un pedido que ya fue enviado o entregado.
# # 2. Saltar de pending directo a shipped o delivered.
# # 3. Salir de un estado terminal (delivered o cancelled).
# SOLUTION_END
