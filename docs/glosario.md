# Glosario de ingeniería de software

Este glosario reúne términos frecuentes en equipos de ingeniería que aparecen a lo largo de los 5 pasos de Tiendita. Cada definición va directo a cómo se usa en el día a día.

## ADR

Architecture Decision Record (registro de decisión de arquitectura). Es un documento corto que explica qué decisión técnica tomó el equipo, en qué contexto, qué alternativas descartó y qué consecuencias acepta. En el Paso 4 escribes uno en `docs/adr/0001-<tema>.md` (hay un modelo en `examples/adr.md`).

## API y endpoint

Un API es la puerta por la que un programa le pide datos o acciones a otro ([MDN: API](https://developer.mozilla.org/es/docs/Glossary/API)). Cada endpoint es una combinación de método y ruta, como `GET /api/products`, que responde algo concreto.

## CI/CD

Integración continua (CI) y entrega o deploy continuo (CD). En CI, un servidor como [GitHub Actions](https://docs.github.com/en/actions) ejecuta pruebas y verificaciones cada vez que subes cambios a una rama. En CD, los cambios que pasan esas verificaciones se publican automáticamente hacia un entorno de pruebas o producción.

## Códigos HTTP (2xx, 4xx, 5xx)

Números de tres dígitos con los que un servidor indica qué ocurrió con un request ([MDN HTTP status](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)). Los `2xx` confirman éxito (`200 OK`, `201 Created`); los `4xx` señalan un problema del cliente (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`); y los `5xx` indican un fallo interno del servidor (`500`, `502`, `503`), justo lo que cuentas en el Paso 1.

## Commit, rama y Pull Request

Un commit guarda una foto del proyecto con un mensaje. Una rama es una línea de trabajo aparte de `main`. Un Pull Request propone llevar los commits de una rama a otra y es donde ocurre el code review ([Pro Git](https://git-scm.com/book/es/v2)).

## CORS (Cross-Origin Resource Sharing)

Mecanismo de seguridad aplicado por los navegadores web, documentado en [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS). Cuando tu frontend en un dominio (por ejemplo `https://tiendita.vercel.app`) llama a un backend en otro origen, el navegador exige que el backend autorice explícitamente ese origen mediante encabezados HTTP como `Access-Control-Allow-Origin`.

## Deploy

Publicar tu aplicación en un servidor para que otras personas la usen desde internet. En el Paso 5 el deploy es opcional y se hace en Vercel.

## Deuda técnica

Costo adicional de mantenimiento que acumula un equipo cuando elige un atajo rápido en lugar de un diseño limpio. Al igual que una deuda financiera, puede ser una decisión consciente para aprender o salir antes, siempre que el equipo registre qué quedó pendiente y lo pague antes de que frene cada cambio futuro.

## Estimación

Pronóstico aproximado del esfuerzo o complejidad necesaria para completar una historia o tarea técnica. Una estimación sirve para priorizar y coordinar dependencias entre personas, nunca como una promesa exacta grabada en piedra.

## Hotfix

Cambio pequeño y urgente que se aplica directamente para corregir un fallo crítico en producción sin esperar al ciclo normal de lanzamientos. Después de hacer deploy del hotfix, el equipo integra ese cambio de vuelta a la rama principal y agrega una prueba que impida la regresión.

## Idempotencia

Propiedad de una operación que produce exactamente el mismo efecto aunque el cliente la ejecute varias veces con la misma entrada o llave (`Idempotency-Key`), como explica [Stripe Idempotency](https://stripe.com/blog/idempotency). En pagos y creación de órdenes evita cobros duplicados cuando el usuario reintenta ante una caída de red.

## Incidente

Evento no planificado que degrada o interrumpe un servicio para los usuarios, o que corrompe datos del negocio (por ejemplo, vender más unidades de las disponibles en inventario). Todo incidente serio se atiende primero restaurando el servicio y después analizando causas en un postmortem sin culpas.

## Inyección de dependencias

Patrón donde una función o clase recibe las piezas que necesita desde afuera en lugar de crearlas dentro. En FastAPI lo ves con `Depends(get_store_service)`: en producción inyecta `PostgresStoreRepository` y en los tests del Paso 4 se reemplaza por un repositorio en memoria sin levantar PostgreSQL.

## JWKS (JSON Web Key Set)

Documento JSON público expuesto por un proveedor de identidad (como Neon Auth) que contiene las llaves criptográficas públicas usadas para verificar la firma de los tokens JWT, según [RFC 7517](https://datatracker.ietf.org/doc/html/rfc7517). El backend consulta este endpoint y guarda las llaves en caché local para validar firmas sin llamar al proveedor en cada request.

## JWT (JSON Web Token)

Formato estándar ([RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)) para transmitir afirmaciones firmadas entre dos sistemas en formato compacto (`header.payload.signature`). El payload suele estar codificado en Base64URL y cualquier persona puede leerlo, por eso la confianza depende siempre de verificar su firma criptográfica, emisor (`iss`), audiencia (`aud`) y expiración (`exp`) en el servidor.

## Linter (ruff)

Herramienta que revisa el código sin ejecutarlo para detectar errores comunes, imports sin usar y problemas de estilo. Tiendita usa `ruff` (`uv run ruff check ...`) en el Paso 2 y en CI para mantener el código Python limpio y consistente.

## Migración y seed

Una migración es un script versionado (como `db/migrations/001_init.sql`) que crea o modifica tablas e índices de forma repetible. Un seed carga datos iniciales de prueba (productos y pedidos de ejemplo) para poder desarrollar y probar. En Tiendita `make migrate` ejecuta ambos pasos con `db/load.py --seed`.

## ORM

Una librería que convierte filas de la base de datos en objetos del lenguaje y genera el SQL por ti, como SQLAlchemy en Python. Tiendita usa SQL directo con `psycopg` para que veas cada consulta.

## Race condition

Defecto de concurrencia donde el resultado final de un programa cambia según el orden exacto en que se intercalan dos o más operaciones simultáneas. En Tiendita ocurre cuando dos compradores consultan `stock = 1` en paralelo y ambos logran confirmar la compra si falta un bloqueo de fila (`SELECT ... FOR UPDATE`).

## Rollback

Acción de revertir un deploy, una migración o una transacción de base de datos al último estado estable conocido cuando aparece un fallo grave. Diseñar cambios pequeños y compatibles hacia atrás hace que un rollback sea rápido y seguro.

## SQL

El lenguaje para consultar y modificar bases de datos relacionales ([PostgreSQL: tutorial](https://www.postgresql.org/docs/current/tutorial-sql.html)). `SELECT` lee filas, `JOIN` combina tablas y `GROUP BY` agrupa para sumar o contar.

## Test automatizado

Código que ejecuta otra parte del código y comprueba el resultado. Pasa en verde cuando el comportamiento es el esperado y se pone en rojo cuando algo se rompe. En Tiendita los tests de Python corren con `pytest` y los de React con `vitest`.

## Para leer más

- Paso 1: [MIT The Missing Semester](https://missing.csail.mit.edu/) y [Pro Git](https://git-scm.com/book/es/v2).
- Paso 2: [Problem Solving with Algorithms and Data Structures using Python](https://runestone.academy/ns/books/published/pythonds3/index.html) y [pytest](https://docs.pytest.org/).
- Paso 3: [documentación de PostgreSQL](https://www.postgresql.org/docs/current/), [Use The Index, Luke](https://use-the-index-luke.com/) y [CMU 15-445](https://15445.courses.cs.cmu.edu/).
- Paso 4: [Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html), [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP), [FastAPI](https://fastapi.tiangolo.com/) y [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) sobre JWT.
- Paso 5: [Thinking in React](https://react.dev/learn/thinking-in-react), [Full Stack Open](https://fullstackopen.com/en/) y el [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html).
