#!/usr/bin/env python3
"""Preguntas de autoevaluación formativa para el Paso 1 (Terminal y Git)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    prompt: str
    options: tuple[str, ...]
    answer_index: int
    explanation: str


QUESTIONS: tuple[Question, ...] = (
    Question(
        id="P1-Q1",
        category="terminal",
        prompt=(
            "Ejecutas en Bash el siguiente bloque.\n"
            "  set -euo pipefail\n"
            "  cat archivo_inexistente.json | jq 'length'\n"
            "  echo 'listo'\n"
            "¿Qué ocurre al ejecutar el script?"
        ),
        options=(
            "A) Imprime 0 y luego imprime 'listo'.",
            "B) Falla en la línea del pipe y el script se detiene antes de imprimir 'listo'.",
            "C) Ignora el error de cat porque jq recibe entrada vacía y devuelve código 0.",
        ),
        answer_index=1,
        explanation=(
            "Con 'set -o pipefail', el pipe toma el código de salida del primer comando que falla "
            "('cat'), y 'set -e' detiene el script de inmediato sin llegar a 'echo listo'."
        ),
    ),
    Question(
        id="P1-Q2",
        category="terminal",
        prompt=(
            "Tienes el JSON '[{\"name\":\"Café\",\"stock\":3},{\"name\":\"Pan\",\"stock\":0}]'.\n"
            "¿Qué imprime el comando `jq -r '.[] | select(.stock > 0) | .name'`?"
        ),
        options=(
            "A) \"Café\" (con comillas dobles).",
            "B) Café (sin comillas dobles).",
            "C) Café y Pan en dos líneas.",
        ),
        answer_index=1,
        explanation=(
            "select(.stock > 0) deja pasar solo el objeto con stock mayor a cero y la bandera "
            "-r (raw output) imprime la cadena sin comillas JSON alrededor."
        ),
    ),
    Question(
        id="P1-Q3",
        category="git",
        prompt=(
            "Creas la rama 'feat/reporte', editas 'report.sh' y ejecutas `git add report.sh`, "
            "pero todavía no haces `git commit`. Luego corres `git status`. ¿Dónde aparece el cambio?"
        ),
        options=(
            "A) En 'Changes not staged for commit'.",
            "B) En 'Changes to be committed' (staging area).",
            "C) Ya quedó guardado en el historial de commits de la rama.",
        ),
        answer_index=1,
        explanation=(
            "`git add` mueve el snapshot actual del archivo al área de staging ('Changes to be committed'). "
            "El historial solo cambia cuando ejecutas `git commit`."
        ),
    ),
    Question(
        id="P1-Q4",
        category="git",
        prompt=(
            "Durante un merge aparece un conflicto en `data/config.txt` con marcadores "
            "`<<<<<<< HEAD`, `=======` y `>>>>>>> main`. Editas el archivo para combinar ambos cambios "
            "y borras todos los marcadores. ¿Qué comandos completan el merge?"
        ),
        options=(
            "A) `git add data/config.txt` y después `git commit`.",
            "B) `git merge --abort` y después `git push`.",
            "C) `git checkout -- data/config.txt` y después `git status`.",
        ),
        answer_index=0,
        explanation=(
            "Después de resolver el archivo manualmente, `git add` le indica a Git que el conflicto "
            "quedó resuelto y `git commit` registra el commit de merge. `git merge --abort` desharía todo el intento."
        ),
    ),
    Question(
        id="P1-Q5",
        category="workflow",
        prompt=(
            "Abres un Pull Request que cambia el reporte del Paso 1 y además reformatea 14 archivos "
            "del Paso 4 que nadie tocó. ¿Qué problema principal introduce ese PR?"
        ),
        options=(
            "A) GitHub rechaza Pull Requests con más de 10 archivos.",
            "B) Mezcla cambios sin relación, dificulta la revisión y complica un rollback futuro.",
            "C) Impide que GitHub Actions ejecute los tests del Paso 1.",
        ),
        answer_index=1,
        explanation=(
            "Un Pull Request pequeño y enfocado permite revisar el cambio con criterio y revertirlo "
            "sin romper otras partes del repositorio."
        ),
    ),
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoevaluación formativa del Paso 1 (Terminal y Git)."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Muestra todas las preguntas y respuestas esperadas sin pedir entrada.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Ejecuta una verificación sin entrada interactiva y devuelve código 0.",
    )
    parser.add_argument(
        "--skip-intro",
        action="store_true",
        help="Omite las preguntas básicas de terminal y evalúa solo Git y flujo de trabajo.",
    )
    return parser.parse_args(argv)


def run_interactive(questions: list[Question]) -> int:
    print("Autoevaluación formativa — Paso 1. Terminal, Git y flujo de trabajo\n")
    correct = 0
    terminal_correct = 0
    terminal_total = 0

    for idx, q in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] ({q.id}) {q.prompt}\n")
        for opt in q.options:
            print(f"  {opt}")
        valid_letters = [chr(ord("A") + i) for i in range(len(q.options))]
        while True:
            raw = input(f"\nTu respuesta ({'/'.join(valid_letters)}): ").strip().upper()
            if raw in valid_letters:
                break
            print(f"Escribe una opción válida ({', '.join(valid_letters)}).")

        chosen = ord(raw) - ord("A")
        if q.category == "terminal":
            terminal_total += 1
        if chosen == q.answer_index:
            correct += 1
            if q.category == "terminal":
                terminal_correct += 1
            print("Correcto.")
        else:
            expected = valid_letters[q.answer_index]
            print(f"Respuesta esperada = {expected}.")
        print(f"Explicación: {q.explanation}\n")
        print("-" * 60)

    print(f"Resultado = {correct}/{len(questions)} respuestas acertadas.")
    if terminal_total > 0:
        if terminal_correct == terminal_total:
            print("Diagnóstico de terminal = Puedes saltar example/intro-terminal.md e ir directo al Paso 1.")
        else:
            print("Diagnóstico de terminal = Conviene revisar example/intro-terminal.md antes de empezar.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    selected = [
        q for q in QUESTIONS if not (args.skip_intro and q.category == "terminal")
    ]

    if args.list or args.non_interactive:
        print(f"Paso 1 — {len(selected)} preguntas de autoevaluación formativa")
        for q in selected:
            expected = chr(ord("A") + q.answer_index)
            print(f"- {q.id} [{q.category}] (respuesta {expected}) {q.prompt.splitlines()[0]}")
        return 0

    return run_interactive(selected)


if __name__ == "__main__":
    raise SystemExit(main())
