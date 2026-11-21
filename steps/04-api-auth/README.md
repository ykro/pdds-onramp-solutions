# Paso 4. API REST, capas y autenticación

![Dónde estás](diagrams/where.svg)

## Por qué importa

El backend expone las reglas de negocio sobre HTTP sin mezclar rutas, lógica y SQL en un mismo archivo. Separar capas como propone [Cosmic Python](https://www.cosmicpython.com/book/preface.html) y *Fundamentals of Software Architecture* (Richards y Ford), respetar [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) y validar tokens con [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) protege los pedidos y simplifica las pruebas. Todo corre al 100% en local con un servidor JWKS de prueba, sin crear una cuenta de Neon todavía.

## Qué se construye

**Núcleo**
- La migración `db/migrations/002_roles_and_idempotency.sql` con `admins` e `idempotency_keys` sin alterar datos existentes.
- Las rutas `/api/health`, `/api/products`, `/api/orders` y `/api/orders/mine` en [FastAPI](https://fastapi.tiangolo.com/) separadas en tres capas (`api/app.py`, `services/store_service.py`, `repositories/orders_repo.py`).
- `verify_jwt_token` en `api/auth.py` con `PyJWT[crypto]`, configuración por variables de entorno según [The Twelve-Factor App](https://12factor.net/) y el ADR en `docs/decisions/0001-auth.md`.

**Extendido**
- `PATCH /api/products/{sku}/stock` con `403` para usuarios sin rol admin, `Idempotency-Key` concurrente siguiendo [Stripe Idempotency](https://stripe.com/blog/idempotency), contrato en `/api/openapi.json` y `Dockerfile` con `compose.yaml`.

![Capas del backend](diagrams/layers.svg)

![Flujo de verificación JWT](diagrams/jwt-flow.svg)

## Criterios de aceptación

- `CA-4.1` [auto, núcleo] `db/migrations/002_roles_and_idempotency.sql` crea `admins` e `idempotency_keys` preservando las filas existentes en `orders`.
- `CA-4.2` [auto, núcleo] `/api/health`, `/api/products`, `/api/orders` y `/api/orders/mine` separan `api/app.py`, `services/store_service.py` y `repositories/orders_repo.py` para probarse en aislamiento.
- `CA-4.3` [auto, núcleo] `verify_jwt_token` en `api/auth.py` valida JWT con `PyJWT[crypto]` contra el servidor JWKS local y rechaza tokens ausentes, expirados o mal firmados con `401`.
- `CA-4.4` [auto, núcleo] `GET /api/orders/mine` devuelve únicamente los pedidos del usuario autenticado sin filtrar órdenes ajenas.
- `CA-4.5` [auto, núcleo] `docs/decisions/0001-auth.md` completa Contexto, Decisión y Consecuencias sin `TODO`, siguiendo `examples/adr.md`.
- `CA-4.6` [auto, extendido] `PATCH /api/products/{sku}/stock` exige rol en `admins` y responde `403` a clientes regulares.
- `CA-4.7` [auto, extendido] Dos envíos concurrentes de `POST /api/orders` con la misma `Idempotency-Key` crean una sola orden y devuelven el mismo `order_id`.
- `CA-4.8` [auto, extendido] `/api/openapi.json` publica las cinco rutas del contrato y el repo incluye `Dockerfile` y `compose.yaml`.

## Cómo verificar

Corre `make check STEP=4` para validar el núcleo y `make check STEP=4 EXTRA=1` para el alcance extendido. Ejecuta `make self-check STEP=4` para la autoevaluación formativa. Revisa el patrón completo en [example/layered_endpoint_example.py](example/layered_endpoint_example.py) o abre la [primera pista](hints/1.md).
