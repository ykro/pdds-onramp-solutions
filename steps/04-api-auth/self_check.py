#!/usr/bin/env python3
"""Preguntas de autoevaluación formativa para el Paso 4 (API REST, capas y JWT)."""

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
        id="P4-Q1",
        prompt=(
            "La usuaria Ana envía un JWT válido y vigente al endpoint `GET /orders/99`, "
            "pero la orden `99` pertenece al usuario Luis.\n"
            "¿Qué código HTTP debe responder el API?"
        ),
        options=(
            "A) 401 Unauthorized.",
            "B) 403 Forbidden.",
            "C) 200 OK con el cuerpo vacío.",
        ),
        answer_index=1,
        explanation=(
            "401 indica que falta autenticación válida. Aquí Ana sí está autenticada, "
            "pero carece de permiso sobre un recurso ajeno, por eso corresponde 403 Forbidden."
        ),
    ),
    Question(
        id="P4-Q2",
        prompt=(
            "Un servidor verifica JWT leyendo el campo `alg` directamente del header del token "
            "sin fijar una lista blanca en el código del backend.\n"
            "¿Qué riesgo descrito en RFC 8725 abre esa decisión?"
        ),
        options=(
            "A) Permite ataques de confusión de algoritmo como `alg: none` o firmar con HS256 usando una llave pública.",
            "B) Hace que el token expire antes de tiempo.",
            "C) Impide almacenar el JWKS en caché local.",
        ),
        answer_index=0,
        explanation=(
            "El verificador debe fijar los algoritmos aceptados desde configuración del servidor "
            "y rechazar cualquier token que declare un algoritmo distinto."
        ),
    ),
    Question(
        id="P4-Q3",
        prompt=(
            "El cliente envía `POST /orders` con `Idempotency-Key: req-42`, el servidor crea la orden, "
            "pero la red se corta antes de que llegue la respuesta al navegador. El cliente reintenta "
            "el mismo request con `Idempotency-Key: req-42`.\n"
            "¿Qué debe suceder?"
        ),
        options=(
            "A) El servidor crea una segunda orden idéntica y descuenta stock otra vez.",
            "B) El servidor devuelve la orden ya creada sin volver a descontar stock.",
            "C) El servidor responde 500 Internal Server Error.",
        ),
        answer_index=1,
        explanation=(
            "Guardar la llave de idempotencia junto con el resultado de la orden permite responder "
            "de forma segura ante reintentos de red sin duplicar cobros ni reducir inventario dos veces."
        ),
    ),
    Question(
        id="P4-Q4",
        prompt=(
            "En una prueba unitaria de `OrderService` reemplazas `PostgresOrderRepository` por un "
            "`InMemoryOrderRepository` mediante inyección de dependencias.\n"
            "¿Qué ganas con ese diseño?"
        ),
        options=(
            "A) Pruebas las reglas del servicio en milisegundos sin depender de una base de datos encendida.",
            "B) Eliminas por completo la necesidad de probar SQL en el Paso 3.",
            "C) Haces que FastAPI omita la validación de esquemas Pydantic.",
        ),
        answer_index=0,
        explanation=(
            "Separar rutas, servicios y repositorios te permite probar la lógica de negocio rápido "
            "en memoria, reservando las pruebas contra PostgreSQL real para los repositorios e integración."
        ),
    ),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoevaluación formativa del Paso 4 (API REST, capas y JWT)."
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
    print("Autoevaluación formativa — Paso 4. API REST, capas y autenticación\n")
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
        print(f"Paso 4 — {len(QUESTIONS)} preguntas de autoevaluación formativa")
        for q in QUESTIONS:
            expected = chr(ord("A") + q.answer_index)
            print(f"- {q.id} (respuesta {expected}) {q.prompt.splitlines()[0]}")
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
