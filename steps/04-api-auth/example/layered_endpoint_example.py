"""Ejemplo resuelto para el Paso 4.

Demuestra cómo separar una ruta de FastAPI, un servicio con reglas de negocio
y un repositorio intercambiable usando `Depends` y `Protocol`.

Ejecuta las pruebas integradas con:
    pytest steps/04-api-auth/example/layered_endpoint_example.py
"""

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


# 1. Modelos de dominio y contrato HTTP
@dataclass(frozen=True)
class ProductRecord:
    id: str
    name: str
    price_cents: int
    stock: int


class ProductOut(BaseModel):
    id: str
    name: str
    price_cents: int = Field(ge=0)
    stock: int = Field(ge=0)


# 2. Puerto del repositorio (contrato que implementan Postgres y el doble en memoria)
class ProductRepository(Protocol):
    def get_by_id(self, product_id: str) -> ProductRecord | None: ...


class InMemoryProductRepository:
    def __init__(self, items: list[ProductRecord]) -> None:
        self._items = {item.id: item for item in items}

    def get_by_id(self, product_id: str) -> ProductRecord | None:
        return self._items.get(product_id)


# 3. Capa de servicio (conoce reglas de dominio, desconoce HTTP y SQL)
class ProductNotFoundError(Exception):
    pass


class CatalogService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def get_available_product(self, product_id: str) -> ProductRecord:
        product = self._repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product


# 4. Capa de rutas FastAPI (traduce HTTP <-> servicio)
app = FastAPI()


def get_product_repo() -> ProductRepository:
    # En producción esta dependencia devuelve el repositorio conectado a PostgreSQL.
    return InMemoryProductRepository(
        [ProductRecord(id="cafe-gt", name="Café de Huehuetenango", price_cents=6500, stock=8)]
    )


def get_catalog_service(
    repo: ProductRepository = Depends(get_product_repo),
) -> CatalogService:
    return CatalogService(repo)


@app.get("/products/{product_id}", response_model=ProductOut)
def read_product(
    product_id: str,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductOut:
    try:
        product = service.get_available_product(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto '{product_id}' no encontrado",
        ) from exc
    return ProductOut(
        id=product.id,
        name=product.name,
        price_cents=product.price_cents,
        stock=product.stock,
    )


# 5. Prueba aislada sobrescribiendo solo la dependencia del repositorio
def test_read_product_with_fake_repository() -> None:
    fake_repo = InMemoryProductRepository(
        [ProductRecord(id="pan-01", name="Pan artesanal", price_cents=1800, stock=4)]
    )
    app.dependency_overrides[get_product_repo] = lambda: fake_repo
    try:
        client = TestClient(app)
        ok_resp = client.get("/products/pan-01")
        assert ok_resp.status_code == 200
        assert ok_resp.json()["price_cents"] == 1800

        missing_resp = client.get("/products/inexistente")
        assert missing_resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
