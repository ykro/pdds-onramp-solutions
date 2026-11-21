"""FastAPI application mounted under /api for both local dev and Vercel."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tiendita.api.auth import get_current_user_id
from tiendita.pricing import OutOfStockError
from tiendita.repositories.orders_repo import PostgresStoreRepository
from tiendita.services.store_service import ForbiddenError, StoreService


class CreateOrderRequest(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class RestockRequest(BaseModel):
    delta: int = Field(gt=0)


class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: str
    total_cents: int


def get_store_service() -> StoreService:
    return StoreService(PostgresStoreRepository())


router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/products")
def list_products(service: StoreService = Depends(get_store_service)) -> list[dict[str, Any]]:
    return service.get_catalog()


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body: CreateOrderRequest,
    user_id: str = Depends(get_current_user_id),
    service: StoreService = Depends(get_store_service),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> OrderResponse:
    # SOLUTION_START
    try:
        order = service.create_order(
            user_id=user_id,
            sku=body.sku,
            quantity=body.quantity,
            idempotency_key=idempotency_key,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OutOfStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_cents=order.total_cents,
    )
    # SOLUTION_REPLACE
    # raise HTTPException(status_code=501, detail="TODO: implementa POST /api/orders")
    # SOLUTION_END


@router.get("/orders/mine")
def get_my_orders(
    user_id: str = Depends(get_current_user_id),
    service: StoreService = Depends(get_store_service),
) -> list[dict[str, Any]]:
    # SOLUTION_START
    return service.get_my_orders(user_id)
    # SOLUTION_REPLACE
    # raise HTTPException(status_code=501, detail="TODO: implementa GET /api/orders/mine")
    # SOLUTION_END


@router.patch("/products/{sku}/stock")
def restock_product(
    sku: str,
    body: RestockRequest,
    user_id: str = Depends(get_current_user_id),
    service: StoreService = Depends(get_store_service),
) -> dict[str, Any]:
    # SOLUTION_START
    try:
        return service.restock_product(user_id=user_id, sku=sku, delta=body.delta)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # SOLUTION_REPLACE
    # raise HTTPException(status_code=501, detail="TODO: implementa PATCH stock")
    # SOLUTION_END


def create_app() -> FastAPI:
    app = FastAPI(title="Tiendita API", version="0.1.0", openapi_url="/api/openapi.json")
    origins = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
