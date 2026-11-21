#!/usr/bin/env python3
"""Preguntas de autoevaluación formativa para el Paso 5 (React, TypeScript y deploy)."""

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
        id="P5-Q1",
        prompt=(
            "En un componente React escribes `cartItems.push(newItem); setCartItems(cartItems);`.\n"
            "¿Qué ocurre en pantalla?"
        ),
        options=(
            "A) React detecta el nuevo elemento y vuelve a renderizar el carrito al instante.",
            "B) React compara referencias con `Object.is`, ve el mismo arreglo y omite el re-render.",
            "C) TypeScript rechaza el código porque `push` no existe en arreglos.",
        ),
        answer_index=1,
        explanation=(
            "React necesita una referencia nueva para detectar cambios de estado. "
            "Usa `setCartItems((prev) => [...prev, newItem])` para actualizar de forma inmutable."
        ),
    ),
    Question(
        id="P5-Q2",
        prompt=(
            "Ejecutas `const res = await fetch('/api/orders');` y el servidor responde `401 Unauthorized`.\n"
            "¿Qué pasa si no compruebas `res.ok`?"
        ),
        options=(
            "A) `fetch` lanza una excepción automática y salta al bloque `catch`.",
            "B) La promesa se resuelve normalmente con `res.ok === false` y el código intenta leer el JSON como si fuera exitoso.",
            "C) El navegador recarga la página para pedir credenciales.",
        ),
        answer_index=1,
        explanation=(
            "`fetch` solo rechaza la promesa cuando falla la red o DNS. "
            "Siempre debes revisar `if (!res.ok)` para manejar códigos 4xx y 5xx explícitamente."
        ),
    ),
    Question(
        id="P5-Q3",
        prompt=(
            "Reemplazas un `<button type=\"button\">Agregar</button>` por `<div onClick={handleAdd}>Agregar</div>` "
            "sin atributos adicionales.\n"
            "¿Qué pierde un usuario que navega solo con teclado o lector de pantalla?"
        ),
        options=(
            "A) Nada, `div` y `button` tienen el mismo comportamiento nativo en el navegador.",
            "B) Pierde el foco con Tab, la activación con Enter o Espacio y el rol semántico de botón.",
            "C) Solo pierde el cursor de mano al pasar el ratón.",
        ),
        answer_index=1,
        explanation=(
            "Los elementos HTML semánticos como `<button>` traen foco por teclado, soporte de Enter/Espacio "
            "y anuncios correctos en tecnologías de asistencia sin código extra."
        ),
    ),
    Question(
        id="P5-Q4",
        prompt=(
            "Haces deploy del frontend en `https://tiendita.vercel.app` y del backend en `https://api-tiendita.vercel.app`. "
            "En producción el navegador bloquea `GET /products` con un error de CORS, aunque `curl` funciona.\n"
            "¿Por qué sucede eso?"
        ),
        options=(
            "A) Porque CORS es una política que aplica el navegador cuando el backend no autoriza el origen del frontend en `Access-Control-Allow-Origin`.",
            "B) Porque Neon bloquea conexiones que vienen desde navegadores Chrome.",
            "C) Porque `curl` envía automáticamente cookies de sesión.",
        ),
        answer_index=0,
        explanation=(
            "`curl` ignora CORS porque esa restricción protege a usuarios dentro del navegador. "
            "Debes configurar en FastAPI el origen exacto de tu frontend en producción."
        ),
    ),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoevaluación formativa del Paso 5 (React, TypeScript y deploy)."
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
    print("Autoevaluación formativa — Paso 5. React, TypeScript y deploy\n")
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
        print(f"Paso 5 — {len(QUESTIONS)} preguntas de autoevaluación formativa")
        for q in QUESTIONS:
            expected = chr(ord("A") + q.answer_index)
            print(f"- {q.id} (respuesta {expected}) {q.prompt.splitlines()[0]}")
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
