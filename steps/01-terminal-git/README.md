# Paso 1. Terminal, Git y flujo de trabajo

![Dónde estás](diagrams/where.svg)

## Por qué importa

Todo equipo de ingeniería colabora sobre un historial compartido y reproduce su entorno desde la línea de comandos. Dominar el shell como plantea [MIT Missing Semester](https://missing.csail.mit.edu/) y controlar ramas con [Pro Git](https://git-scm.com/book/en/v2) evita pérdida de código y hace cada cambio auditable. Si necesitas repasar rutas, variables de entorno y JSON antes de empezar, revisa la [guía opcional de terminal](example/intro-terminal.md) y el [glosario](../../docs/glosario.md).

## Qué se construye

**Núcleo**
- Un script de diagnóstico en shell que inspecciona `data/products.json` y genera un reporte limpio, siguiendo hábitos de automatización descritos en *The Pragmatic Programmer* (Hunt y Thomas).
- Una historia de usuario en `docs/stories/001-order-history.md` y un flujo completo de rama, commits atómicos y Pull Request en [GitHub Docs](https://docs.github.com/en/pull-requests).
- La resolución controlada de un conflicto de merge en Git sin perder cambios válidos.

**Extendido**
- Una revisión de código documentada sobre un Pull Request ajeno o propio, aplicando la rúbrica de `examples/code-review.md`.

## Criterios de aceptación

- `CA-1.1` [auto, núcleo] El script de reporte corre sin errores sobre `data/products.json`, devuelve código de salida `0` y produce el conteo y formato esperados.
- `CA-1.2` [auto, núcleo] El historial de Git contiene una rama de feature integrada con commits atómicos y mensajes descriptivos en formato consistente.
- `CA-1.3` [auto, núcleo] El conflicto de merge preparado queda resuelto sin marcadores residuales (`<<<<<<<`, `=======`, `>>>>>>>`) y conserva ambas líneas de negocio.
- `CA-1.4` [rubric, núcleo] La historia en `docs/stories/001-order-history.md` y el Pull Request cumplen los 5 criterios de `examples/historia-y-pr.md`.
- `CA-1.5` [rubric, extendido] El comentario de revisión en el Pull Request cumple la rúbrica de `examples/code-review.md` con observaciones accionables y tono constructivo.

## Cómo verificar

Ejecuta las pruebas del núcleo con `make check STEP=1` y agrega los criterios extendidos con `make check STEP=1 EXTRA=1`. Responde las preguntas de autoevaluación formativa con `make self-check STEP=1` (usa `--skip-intro` si ya dominas la terminal). Si buscas una referencia resuelta, revisa [example/sample_report.sh](example/sample_report.sh), la [guía opcional de terminal](example/intro-terminal.md) o la [primera pista](hints/1.md).
