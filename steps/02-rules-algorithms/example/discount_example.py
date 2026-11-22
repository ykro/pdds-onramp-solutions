"""Ejemplo de una regla de negocio pura y sus tests con pytest.

La regla: el envío cuesta Q25.00 hasta 1 kg, Q40.00 hasta 5 kg y Q40.00 más Q5.00 por cada
kilo extra (o fracción) arriba de 5 kg. Todo en centavos enteros, sin float.

Corre los tests con `uv run pytest steps/02-rules-algorithms/example/discount_example.py`.
"""

import pytest


def shipping_cost_cents(weight_grams: int) -> int:
    """Devuelve el costo de envío en centavos para un paquete de weight_grams."""
    if weight_grams <= 0:
        raise ValueError("weight_grams must be positive")
    if weight_grams <= 1_000:
        return 2_500
    if weight_grams <= 5_000:
        return 4_000
    extra_grams = weight_grams - 5_000
    extra_kilos = -(-extra_grams // 1_000)  # división entera hacia arriba
    return 4_000 + extra_kilos * 500


def test_hasta_un_kilo_cuesta_la_tarifa_base() -> None:
    assert shipping_cost_cents(1_000) == 2_500


def test_un_gramo_arriba_del_limite_cambia_de_tarifa() -> None:
    assert shipping_cost_cents(1_001) == 4_000


def test_cada_kilo_extra_o_fraccion_suma_cinco_quetzales() -> None:
    assert shipping_cost_cents(5_001) == 4_500
    assert shipping_cost_cents(7_000) == 5_000


def test_peso_invalido_lanza_error() -> None:
    with pytest.raises(ValueError):
        shipping_cost_cents(0)
