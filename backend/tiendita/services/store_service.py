"""Layered business service with dependency injection and authorization rules."""

from __future__ import annotations

from typing import Any, Protocol

from tiendita.repositories.orders_repo import OrderSummary


class ForbiddenError(PermissionError):
    """Raised when an authenticated user lacks permission for an action."""


class StoreRepository(Protocol):
    def list_products(self) -> list[dict[str, Any]]: ...
    def create_order(
        self,
        user_id: str,
        sku: str,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> OrderSummary: ...
    def list_orders_for_user(self, user_id: str) -> list[dict[str, Any]]: ...
    def is_admin(self, user_id: str) -> bool: ...
    def restock_product(self, sku: str, delta: int) -> dict[str, Any]: ...


class StoreService:
    """Coordinates pricing, authorization, and persistence without knowing HTTP or SQL."""

    def __init__(self, repo: StoreRepository) -> None:
        self._repo = repo

    def get_catalog(self) -> list[dict[str, Any]]:
        return self._repo.list_products()

    def create_order(
        self,
        user_id: str,
        sku: str,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> OrderSummary:
        # SOLUTION_START
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        return self._repo.create_order(
            user_id=user_id,
            sku=sku,
            quantity=quantity,
            idempotency_key=idempotency_key,
        )
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO: implementa create_order en StoreService")
        # SOLUTION_END

    def get_my_orders(self, user_id: str) -> list[dict[str, Any]]:
        """Authorization rule: return only orders belonging to user_id."""
        # SOLUTION_START
        orders = self._repo.list_orders_for_user(user_id)
        return [o for o in orders if o["user_id"] == user_id]
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO: implementa get_my_orders en StoreService")
        # SOLUTION_END

    def restock_product(self, user_id: str, sku: str, delta: int) -> dict[str, Any]:
        """Admin-only operation (Step 4 extended)."""
        # SOLUTION_START
        if not self._repo.is_admin(user_id):
            raise ForbiddenError("Admin role required to restock inventory")
        if delta <= 0:
            raise ValueError("delta must be positive")
        return self._repo.restock_product(sku=sku, delta=delta)
        # SOLUTION_REPLACE
        # raise NotImplementedError("TODO (extendido): verifica rol admin y repone inventario")
        # SOLUTION_END
