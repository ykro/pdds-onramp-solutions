# Tiendita — PDDS Onramp (Soluciones de referencia)

[![Paso 1](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-1.yml/badge.svg)](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-1.yml)
[![Paso 2](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-2.yml/badge.svg)](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-2.yml)
[![Paso 3](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-3.yml/badge.svg)](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-3.yml)
[![Paso 4](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-4.yml/badge.svg)](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-4.yml)
[![Paso 5](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-5.yml/badge.svg)](https://github.com/ykro/pdds-onramp-solutions/actions/workflows/step-5.yml)

Este repositorio contiene las soluciones completas, limpias y verificadas de [ykro/pdds-onramp](https://github.com/ykro/pdds-onramp), el onramp práctico del Postgrado en Diseño y Desarrollo de Software (PDDS) de Universidad Galileo. Cada uno de los cinco pasos se puede revisar de forma independiente y combina lectura de código ajeno, debugging y un cambio pequeño.

![Mapa de Tiendita](docs/diagrams/tiendita-overview.svg)

## Los 5 pasos (independientes)

| Paso | Enfoque | Guía y respuestas |
| --- | --- | --- |
| Paso 1 | Flujo de trabajo, logs, Pull Requests y code review | [steps/01-terminal-git/README.md](steps/01-terminal-git/README.md) |
| Paso 2 | Reglas de negocio, estructuras de datos, debugging y testing | [steps/02-rules-algorithms/README.md](steps/02-rules-algorithms/README.md) |
| Paso 3 | Modelo relacional, consultas SQL y prevención de inyección SQL | [steps/03-sql/README.md](steps/03-sql/README.md) |
| Paso 4 | Arquitectura por capas, cliente-servidor, API REST y autorización | [steps/04-api-auth/README.md](steps/04-api-auth/README.md) |
| Paso 5 | Frontend en React conectado al API y deploy en Vercel y Neon | [steps/05-react-deploy/README.md](steps/05-react-deploy/README.md) |

## Dónde ver la solución de cada problema

| Paso | Problema y criterio | Archivo de solución |
| --- | --- | --- |
| Paso 1 | Corrección de `log_report.sh` (archivo faltante y códigos 5xx, `CA-1.1`, `CA-1.2`) | [scripts/log_report.sh](scripts/log_report.sh) |
| Paso 1 | Historia de usuario completa (`CA-1.3`) | [docs/stories/001-order-history.md](docs/stories/001-order-history.md) |
| Paso 2 | Dinero en centavos con redondeo half-up y tope de cupón (`CA-2.1`) | [backend/tiendita/pricing.py](backend/tiendita/pricing.py) |
| Paso 2 | Corrección de búsqueda por nombre con tildes y espacios (`CA-2.2`) | [backend/tiendita/catalog.py](backend/tiendita/catalog.py) |
| Paso 2 | Tres tests con `pytest` sobre reglas de negocio (`CA-2.3`) | [backend/tests/step2/test_student_pricing.py](backend/tests/step2/test_student_pricing.py) |
| Paso 3 | Consultas de ventas por mes y top 5 de productos (`CA-3.1`, `CA-3.2`) | [db/queries/monthly_sales.sql](db/queries/monthly_sales.sql) y [db/queries/top_products.sql](db/queries/top_products.sql) |
| Paso 3 | Consulta parametrizada contra inyección SQL y pedidos cancelados (`CA-3.3`) | [backend/tiendita/repositories/orders_repo.py](backend/tiendita/repositories/orders_repo.py) |
| Paso 4 | Corrección de fuga de autorización en pedidos (`CA-4.1`) | [backend/tiendita/services/store_service.py](backend/tiendita/services/store_service.py) |
| Paso 4 | Endpoint `GET /api/products/{sku}` a través de las 3 capas (`CA-4.2`, `CA-4.3`) | [backend/tiendita/api/app.py](backend/tiendita/api/app.py), [backend/tiendita/services/store_service.py](backend/tiendita/services/store_service.py) y [backend/tiendita/repositories/orders_repo.py](backend/tiendita/repositories/orders_repo.py) |
| Paso 5 | Corrección de `totalCents` en el carrito y deploy en producción (`CA-5.1` a `CA-5.3`) | [frontend/src/hooks/useCart.ts](frontend/src/hooks/useCart.ts), [vercel.json](vercel.json) y [deploy.json](deploy.json) |

Las respuestas a las tres preguntas de autoevaluación de cada paso viven al final de su `README.md` correspondiente.

## Cómo debería verse Tiendita

Demo en vivo en [https://pdds-onramp.vercel.app](https://pdds-onramp.vercel.app).

Inicio de sesión

![Vista de inicio de sesión](docs/screenshots/01-login.png)

Catálogo y carrito

![Vista de catálogo y carrito](docs/screenshots/02-catalog.png)

Mis pedidos

![Vista de mis pedidos](docs/screenshots/03-orders.png)

## Licencia

Publicado bajo licencia [MIT](LICENSE).
