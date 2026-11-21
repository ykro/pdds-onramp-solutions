# Tiendita — PDDS Onramp

[![Paso 1](https://github.com/ykro/pdds-onramp/actions/workflows/step-1.yml/badge.svg)](https://github.com/ykro/pdds-onramp/actions/workflows/step-1.yml)
[![Paso 2](https://github.com/ykro/pdds-onramp/actions/workflows/step-2.yml/badge.svg)](https://github.com/ykro/pdds-onramp/actions/workflows/step-2.yml)
[![Paso 3](https://github.com/ykro/pdds-onramp/actions/workflows/step-3.yml/badge.svg)](https://github.com/ykro/pdds-onramp/actions/workflows/step-3.yml)
[![Paso 4](https://github.com/ykro/pdds-onramp/actions/workflows/step-4.yml/badge.svg)](https://github.com/ykro/pdds-onramp/actions/workflows/step-4.yml)
[![Paso 5](https://github.com/ykro/pdds-onramp/actions/workflows/step-5.yml/badge.svg)](https://github.com/ykro/pdds-onramp/actions/workflows/step-5.yml)

Este repositorio es un **onramp** práctico y autoevaluable para preparar tu entrada al Postgrado en Diseño y Desarrollo de Software (PDDS) de Universidad Galileo. Todo gira alrededor de un solo proyecto, **Tiendita**, pero cada uno de los cinco pasos se puede trabajar de forma independiente. Si ya dominas terminal y Git, puedes arrancar directo en el paso 2, el 3 o el que necesites reforzar.

![Mapa de Tiendita](docs/diagrams/tiendita-overview.svg)

## Los 5 pasos (independientes)

| Paso | Enfoque | Guía |
| --- | --- | --- |
| Paso 1 | Terminal, Git, Pull Requests y flujo de trabajo | [steps/01-terminal-git/README.md](steps/01-terminal-git/README.md) |
| Paso 2 | Reglas de negocio, algoritmos, pruebas y debugging | [steps/02-rules-algorithms/README.md](steps/02-rules-algorithms/README.md) |
| Paso 3 | Modelado relacional, SQL, transacciones y code review | [steps/03-sql/README.md](steps/03-sql/README.md) |
| Paso 4 | Arquitectura por capas, API REST en FastAPI y JWT | [steps/04-api-auth/README.md](steps/04-api-auth/README.md) |
| Paso 5 | React, TypeScript, Neon Auth y deploy en Vercel | [steps/05-react-deploy/README.md](steps/05-react-deploy/README.md) |

## Inicio rápido

1. Haz clic en **Use this template** en GitHub para crear tu copia del repositorio.
2. Abre la pestaña **Actions** en tu repositorio nuevo y ejecuta el workflow **Initialize Repo** (crea tus issues, abre el PR del paso 3 y actualiza los badges de arriba).
3. Abre el repositorio en **GitHub Codespaces** o clónalo en local con Python 3.12, `uv` y Node 22.
4. Verifica tu entorno con `make doctor` y elige el paso por donde quieras empezar.
5. Revisa tu avance en cualquier momento con `make progress` o valida un paso con `make check STEP=N`.

Si algún término de ingeniería resulta nuevo, consulta el [glosario](docs/glosario.md) y las rúbricas comentadas en [examples/](examples/). Para dudas o compartir avances, usa la pestaña **Discussions** de este repositorio.

## Licencia

Publicado bajo licencia [MIT](LICENSE).
