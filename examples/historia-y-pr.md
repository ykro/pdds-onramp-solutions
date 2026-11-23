# Historia de usuario y Pull Request

Una historia clara acuerda qué problema resuelve el cambio antes de escribir código. Un Pull Request bien descrito permite que otro ingeniero revise el porqué y verifique el resultado sin adivinar.

## Versión buena

### Historia

> **Título** — Consultar pedidos propios en Tiendita
>
> **Historia de usuario** — Como cliente autenticado de Tiendita, quiero consultar mis pedidos en `GET /api/orders/mine` para revisar su estado y el total pagado en quetzales sin escribirle a soporte.
>
> **Criterios de aceptación**
> 1. Dado un cliente autenticado con pedidos propios y pedidos de otras cuentas en la base, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `200 OK` únicamente con sus pedidos ordenados del más reciente al más antiguo.
> 2. Dado un cliente autenticado que todavía no ha comprado, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `200 OK` con una lista vacía `[]`.
> 3. Dado un visitante sin token JWT o con un token vencido, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `401 Unauthorized`.
>
> **Fuera de alcance** — Descarga de factura en PDF y cancelación de pedidos confirmados.

### Descripción del Pull Request

> **Qué cambia** — Refuerza el filtro por `user_id` en `StoreService.get_my_orders` para `GET /api/orders/mine` en `backend/tiendita/api/app.py` y agrega pruebas de aislamiento por cuenta.
>
> **Por qué** — Implementa la historia `docs/stories/001-order-history.md` y cierra la fuga de pedidos entre usuarios.
>
> **Cómo probarlo**
> 1. Ejecuta `make check STEP=4`.
> 2. Verifica que `test_ca_4_1_authorization_isolates_user_orders` pasa en verde.
>
> **Riesgos y rollback** — Cambio acotado a la capa de servicio sin migraciones de base de datos. Revertir el commit de merge restaura el comportamiento anterior sin tocar pedidos existentes.

## Versión mala

### Historia

> Hacer pantalla de historial de órdenes para que funcione bien y sea rápida. Debe verse bonita y traer los datos de la base de datos.

### Descripción del Pull Request

> Arreglé cosas del backend y agregué historial. Ya corre en mi máquina. Cambié también unos espacios en otros archivos.

Esta versión falla porque omite criterios verificables, deja abierto qué pasa con errores o permisos, mezcla archivos sin relación y obliga al revisor a leer cada línea para deducir el alcance.

## Rúbrica de 5 puntos

| # | Criterio | Cumple cuando |
| --- | --- | --- |
| 1 | Problema y usuario claros | Identifica quién usa la funcionalidad y qué necesidad concreta resuelve. |
| 2 | Criterios verificables | Cada criterio describe una entrada y una salida comprobables con una prueba o comando. |
| 3 | Edge cases y alcance | Incluye qué ocurre con listas vacías, errores o permisos, y declara qué queda fuera. |
| 4 | PR enfocado y trazable | El Pull Request enlaza la historia, explica el porqué y evita cambios ajenos al objetivo. |
| 5 | Pasos de verificación | Indica exactamente qué comando o flujo ejecutar para comprobar el cambio. |
