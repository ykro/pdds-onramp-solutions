# Historia de usuario y Pull Request

Una historia clara acuerda qué problema resuelve el cambio antes de escribir código. Un Pull Request bien descrito permite que otro ingeniero revise el porqué y verifique el resultado sin adivinar.

## Versión buena

### Historia

> **Título** — Consultar historial de órdenes propias en Tiendita
>
> **Problema** — Quien compra en Tiendita necesita revisar sus pedidos anteriores con fecha, estado y total en quetzales sin escribirle a soporte.
>
> **Criterios de aceptación**
> 1. Un usuario autenticado recibe únicamente sus propias órdenes ordenadas de la más reciente a la más antigua.
> 2. Cada orden muestra fecha, estado, listado de ítems con cantidad y precio unitario en centavos, y total final.
> 3. Una solicitud sin JWT válido responde `401` y un intento de leer una orden ajena responde `403`.
> 4. Cuando el usuario todavía no tiene compras, la respuesta devuelve una lista vacía `[]` con estado `200`.
>
> **Fuera de alcance** — Descarga de factura en PDF y cancelación de pedidos confirmados.

### Descripción del Pull Request

> **Qué cambia** — Agrega el endpoint `GET /orders` en `backend/tiendita/api/orders.py`, la consulta filtrada por `user_id` en el repositorio y pruebas de aislamiento y autorización.
>
> **Por qué** — Implementa la historia `docs/stories/001-order-history.md`.
>
> **Cómo probarlo**
> 1. Ejecuta `make check STEP=4`.
> 2. Verifica que `test_user_cannot_read_foreign_order` pasa con `403`.
>
> **Riesgos y rollback** — Cambio aditivo sin migraciones destructivas. Revertir el commit de merge retira la ruta sin afectar órdenes existentes.

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
