"""Order lifecycle state machine with a fixed interface for testing."""

from __future__ import annotations

VALID_STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"paid", "cancelled"},
    "paid": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


class InvalidTransitionError(ValueError):
    """Raised when an order status transition is not allowed."""


def can_transition(current: str, target: str) -> bool:
    """Return True if transitioning from current to target is allowed."""
    # SOLUTION_START
    if current not in ALLOWED_TRANSITIONS or target not in ALLOWED_TRANSITIONS:
        return False
    return target in ALLOWED_TRANSITIONS[current]
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa can_transition en order_status.py")
    # SOLUTION_END


def transition_status(current: str, target: str) -> str:
    """Return target status if transition is allowed, else raise InvalidTransitionError."""
    # SOLUTION_START
    if not can_transition(current, target):
        raise InvalidTransitionError(f"Cannot transition order from {current!r} to {target!r}")
    return target
    # SOLUTION_REPLACE
    # raise NotImplementedError("TODO: implementa transition_status en order_status.py")
    # SOLUTION_END
