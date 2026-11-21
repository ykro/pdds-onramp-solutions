#!/usr/bin/env python3
"""Preguntas de autoevaluación formativa para el Paso 3 (SQL y concurrencia)."""

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
        id="P3-Q1",
        prompt=(
            "Dos transacciones concurrentes en `READ COMMITTED` ejecutan un `SELECT stock FROM products WHERE id = 7` "
            "sin `FOR UPDATE` cuando queda 1 unidad. Ambas leen `stock = 1`, deciden en Python que hay inventario "
            "y ejecutan `UPDATE products SET stock = stock - 1 WHERE id = 7`.\n"
            "Si la columna NO tiene `CHECK (stock >= 0)`, ¿qué pasa al terminar ambas transacciones?"
        ),
        options=(
            "A) PostgreSQL aborta automáticamente la segunda transacción.",
            "B) Ambas órdenes se confirman y el stock termina en -1.",
            "C) La segunda transacción queda esperando indefinidamente.",
        ),
        answer_index=1,
        explanation=(
            "Sin bloqueo de fila (`FOR UPDATE`) ni restricción `CHECK`, ambas transacciones leen 1 y "
            "restan 1 sobre la fila actualizada, provocando sobreventa y stock negativo."
        ),
    ),
    Question(
        id="P3-Q2",
        prompt=(
            "Dentro de una transacción compras los productos `[5, 2]` mientras otro cliente compra `[2, 5]`. "
            "Ambos usan `SELECT ... FOR UPDATE` en el orden exacto en que llegaron los IDs.\n"
            "¿Qué fallo puede suceder?"
        ),
        options=(
            "A) Un deadlock porque la transacción A espera la fila 2 y la transacción B espera la fila 5.",
            "B) Un error de sintaxis porque `FOR UPDATE` solo bloquea una fila.",
            "C) Una duplicación de las llaves primarias en `order_items`.",
        ),
        answer_index=0,
        explanation=(
            "Bloquear filas en órdenes distintos crea ciclos de espera (deadlocks). "
            "Agregar `ORDER BY id` antes de `FOR UPDATE` impone un orden global y evita el ciclo."
        ),
    ),
    Question(
        id="P3-Q3",
        prompt=(
            "Quieres listar todos los productos del catálogo junto con sus unidades vendidas, "
            "incluyendo los productos que nunca se han vendido (con `0` en vez de omitirlos).\n"
            "¿Qué combinación necesitas?"
        ),
        options=(
            "A) `INNER JOIN order_items` y `COUNT(*)`.",
            "B) `LEFT JOIN order_items` y `COALESCE(SUM(oi.quantity), 0)`.",
            "C) `RIGHT JOIN products` y `WHERE oi.quantity IS NOT NULL`.",
        ),
        answer_index=1,
        explanation=(
            "`LEFT JOIN` preserva los productos sin filas en `order_items` y `COALESCE` convierte "
            "el resultado `NULL` de `SUM` en `0`."
        ),
    ),
    Question(
        id="P3-Q4",
        prompt=(
            "Ejecutas `EXPLAIN ANALYZE` sobre tu consulta de historial de órdenes filtrada por `user_id` "
            "y ordenada por `created_at DESC`, y el plan muestra `Seq Scan on orders` en una tabla grande.\n"
            "¿Cuál índice compuesto atiende mejor ese patrón?"
        ),
        options=(
            "A) `CREATE INDEX ON orders (created_at, status)`.",
            "B) `CREATE INDEX ON orders (user_id, created_at DESC)`.",
            "C) `CREATE INDEX ON orders (total_cents)`.",
        ),
        answer_index=1,
        explanation=(
            "Colocar primero la columna de igualdad (`user_id`) y luego la de ordenamiento (`created_at DESC`) "
            "permite a PostgreSQL localizar las filas del usuario ya ordenadas con un `Index Scan`."
        ),
    ),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoevaluación formativa del Paso 3 (SQL y concurrencia)."
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
    print("Autoevaluación formativa — Paso 3. SQL, modelado y concurrencia\n")
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
        print(f"Paso 3 — {len(QUESTIONS)} preguntas de autoevaluación formativa")
        for q in QUESTIONS:
            expected = chr(ord("A") + q.answer_index)
            print(f"- {q.id} (respuesta {expected}) {q.prompt.splitlines()[0]}")
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
