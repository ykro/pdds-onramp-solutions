#!/usr/bin/env python3
"""Preguntas de autoevaluación formativa para el Paso 2 (Reglas de negocio y algoritmos)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    options: tuple[str, ...]
    answer_index: int
    explanation: str


QUESTIONS: tuple[Question, ...] = (
    Question(
        id="P2-Q1",
        prompt=(
            "En Python ejecutas `(0.1 + 0.2) == 0.3` y luego `(10 + 20) == 30`.\n"
            "¿Qué imprime cada comparación?"
        ),
        options=(
            "A) True y True.",
            "B) False y True.",
            "C) True y False.",
        ),
        answer_index=1,
        explanation=(
            "En binario IEEE 754, 0.1 + 0.2 produce 0.30000000000000004. "
            "Operar dinero en centavos enteros evita desviaciones al sumar precios e impuestos."
        ),
    ),
    Question(
        id="P2-Q2",
        prompt=(
            "Un carrito tiene subtotal de 2500 centavos y el cliente aplica un cupón fijo de 4000 centavos "
            "con impuesto del 12%. ¿Cuál debe ser el total final?"
        ),
        options=(
            "A) -1500 centavos (saldo a favor negativo).",
            "B) 0 centavos.",
            "C) 300 centavos (12% sobre los 2500 originales).",
        ),
        answer_index=1,
        explanation=(
            "El descuento queda acotado al subtotal para que la base imponible nunca sea negativa. "
            "Con base imponible 0, el impuesto y el total final son 0."
        ),
    ),
    Question(
        id="P2-Q3",
        prompt=(
            "El verificador corre tu suite de `pytest` contra una versión con bug plantado donde "
            "el mínimo del cupón cambió de `subtotal < min_subtotal` a `subtotal <= min_subtotal`. "
            "Si tu suite pasa en verde contra esa versión, ¿qué significa?"
        ),
        options=(
            "A) Que tu implementación principal es excelente.",
            "B) Que te falta al menos un test en el valor exacto del límite (`subtotal == min_subtotal`).",
            "C) Que `pytest` tiene un caché viejo y debes reinstalar Python.",
        ),
        answer_index=1,
        explanation=(
            "Una buena suite falla cuando se planta un bug en el límite. Probar exactamente en el "
            "borde (`min_subtotal - 1` y `min_subtotal`) atrapa cambios entre `<` y `<=`."
        ),
    ),
    Question(
        id="P2-Q4",
        prompt=(
            "Tienes 100,000 productos ordenados por `price_cents` en una lista y necesitas encontrar "
            "todos los productos entre 1000 y 2500 centavos.\n"
            "¿Qué ventaja da usar `bisect_left` y `bisect_right` frente a un ciclo `for` completo?"
        ),
        options=(
            "A) Localiza ambos extremos en O(log n) en vez de inspeccionar los 100,000 elementos.",
            "B) Reduce el uso de memoria a O(1) porque elimina la lista.",
            "C) Permite buscar aunque la lista esté desordenada.",
        ),
        answer_index=0,
        explanation=(
            "La búsqueda binaria exige que la lista esté ordenada y encuentra las posiciones inicial "
            "y final en tiempo logarítmico, recorriendo únicamente los elementos dentro del rango."
        ),
    ),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoevaluación formativa del Paso 2 (Reglas de negocio y algoritmos)."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Muestra las preguntas y respuestas esperadas sin pedir entrada.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Ejecuta una verificación sin entrada interactiva y devuelve código 0.",
    )
    return parser.parse_args(argv)


def run_interactive() -> int:
    print("Autoevaluación formativa — Paso 2. Reglas de negocio y algoritmos\n")
    correct = 0
    for idx, q in enumerate(QUESTIONS, start=1):
        print(f"[{idx}/{len(QUESTIONS)}] ({q.id}) {q.prompt}\n")
        for opt in q.options:
            print(f"  {opt}")
        valid_letters = [chr(ord("A") + i) for i in range(len(q.options))]
        while True:
            raw = input(f"\nTu respuesta ({'/'.join(valid_letters)}): ").strip().upper()
            if raw in valid_letters:
                break
            print(f"Escribe una opción válida ({', '.join(valid_letters)}).")

        chosen = ord(raw) - ord("A")
        if chosen == q.answer_index:
            correct += 1
            print("Correcto.")
        else:
            print(f"Respuesta esperada = {valid_letters[q.answer_index]}.")
        print(f"Explicación: {q.explanation}\n")
        print("-" * 60)

    print(f"Resultado = {correct}/{len(QUESTIONS)} respuestas acertadas.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.list or args.non_interactive:
        print(f"Paso 2 — {len(QUESTIONS)} preguntas de autoevaluación formativa")
        for q in QUESTIONS:
            expected = chr(ord("A") + q.answer_index)
            print(f"- {q.id} (respuesta {expected}) {q.prompt.splitlines()[0]}")
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
