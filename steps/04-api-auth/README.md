# Paso 4. API REST, capas y autorización

![Dónde estás](diagrams/where.svg)

## Antes de empezar

1. ¿Por qué separar un backend en rutas HTTP, capa de servicio y repositorio simplifica probar reglas de negocio y seguridad? (Pista, revisa `diagrams/layers.svg` y `example/layered_endpoint_example.py`.)
2. ¿Qué diferencia existe entre autenticar quién envió un token JWT y autorizar qué recursos puede consultar esa persona? (Pista, revisa `backend/tiendita/api/auth.py` y `backend/tiendita/services/store_service.py`.)
3. ¿Qué debe devolver un endpoint REST cuando el recurso solicitado por identificador no existe y por qué conviene reflejarlo en OpenAPI? (Pista, revisa `backend/tiendita/api/app.py`.)

## Por qué importa

En un sistema en producción, separar transporte HTTP, reglas de negocio y persistencia evita que un cambio pequeño rompa autenticación o exponga datos de otros clientes. Aplicar el diseño por capas de [Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html) y *Fundamentals of Software Architecture* (Richards y Ford) junto con las convenciones de [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) mantiene el código auditable. Además, entender cómo funciona [FastAPI](https://fastapi.tiangolo.com/) y la validación de tokens bajo [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) te prepara para revisar contratos y seguridad de cualquier API.

## Qué vas a hacer

- **Leer**. Recorre las tres capas ya operativas en `backend/tiendita/api/app.py`, `backend/tiendita/services/store_service.py` y `backend/tiendita/repositories/orders_repo.py`, además de la verificación JWT con JWKS ya lista en `backend/tiendita/api/auth.py`.
- **Debuguear**. Corrige la fuga de autorización en `StoreService.get_my_orders()` dentro de `backend/tiendita/services/store_service.py`, donde un usuario autenticado puede leer pedidos que pertenecen a otra cuenta.
- **Escribir**. Agrega el endpoint `GET /api/products/{sku}` atravesando las tres capas (`app.py`, `store_service.py` y `orders_repo.py`) para responder `200` con el producto o `404` cuando el SKU no existe.

![Capas del backend](diagrams/layers.svg)

![Flujo de verificación JWT](diagrams/jwt-flow.svg)

## Criterios de aceptación

- `CA-4.1` `GET /api/orders/mine` exige un token JWT válido (`401` si falta) y devuelve únicamente los pedidos del usuario autenticado.
- `CA-4.2` `GET /api/products/{sku}` atraviesa las tres capas y responde `200` cuando el SKU existe o `404` cuando falta.
- `CA-4.3` El esquema publicado en `/api/openapi.json` expone la ruta `/api/products/{sku}`.

## Al terminar

1. ¿Por qué separar un backend en rutas HTTP, capa de servicio y repositorio simplifica probar reglas de negocio y seguridad? (Pista, revisa `diagrams/layers.svg` y `example/layered_endpoint_example.py`.)
2. ¿Qué diferencia existe entre autenticar quién envió un token JWT y autorizar qué recursos puede consultar esa persona? (Pista, revisa `backend/tiendita/api/auth.py` y `backend/tiendita/services/store_service.py`.)
3. ¿Qué debe devolver un endpoint REST cuando el recurso solicitado por identificador no existe y por qué conviene reflejarlo en OpenAPI? (Pista, revisa `backend/tiendita/api/app.py`.)

## Cómo verificar

Ejecuta `make check STEP=4` para validar los tres criterios en local usando el servidor JWKS de prueba. Si quieres ver el patrón completo antes de editar, revisa [example/layered_endpoint_example.py](example/layered_endpoint_example.py) o abre la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. Al inyectar el repositorio en el servicio, puedes reemplazar PostgreSQL por un repositorio en memoria durante las pruebas y verificar reglas de negocio o autorización en milisegundos, sin levantar red ni base de datos.
2. La autenticación confirma la identidad verificando firma, vigencia, emisor y audiencia del JWT para extraer `sub`. La autorización decide después si esa identidad tiene permiso para leer o modificar un recurso concreto, evitando fugas entre usuarios (IDOR).
3. El servidor debe responder `404 Not Found` cuando el identificador no corresponde a un producto existente. Publicar la ruta y sus códigos en `/api/openapi.json` mantiene alineados al equipo de frontend, a QA y a los consumidores externos del contrato.
