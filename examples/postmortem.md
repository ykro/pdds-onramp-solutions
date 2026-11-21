# Postmortem sin culpas (Blameless Postmortem)

Cuando falla un sistema en producción o aparece un bug grave de concurrencia, el objetivo del postmortem es mejorar el sistema y los procesos. Buscamos causas técnicas y barreras faltantes, sin señalar culpables individuales.

## Versión buena

> # Postmortem. Sobreventa de inventario bajo compras concurrentes
>
> ## Resumen e impacto
> Durante la prueba de carga del checkout, dos compras simultáneas sobre un producto con `stock = 1` completaron con estado `201 Created`. Se registraron dos órdenes confirmadas y el inventario quedó en `-1`, obligando a cancelar manualmente una compra.
>
> ## Línea de tiempo
> 1. `14:02:10.012` — Transacción A lee `stock = 1` con un `SELECT` normal sin bloqueo.
> 2. `14:02:10.015` — Transacción B lee `stock = 1` antes de que A confirme su actualización.
> 3. `14:02:10.021` — Transacción A ejecuta `UPDATE products SET stock = stock - 1` y hace `COMMIT`.
> 4. `14:02:10.025` — Transacción B ejecuta el mismo `UPDATE` y deja `stock = -1`.
>
> ## Causa raíz
> Faltaban dos capas de protección. El checkout leía filas sin `SELECT ... FOR UPDATE`, y la tabla `products` carecía de `CHECK (stock >= 0)`.
>
> ## Qué funcionó y qué falló
> Los logs de PostgreSQL permitieron reconstruir el orden exacto de las transacciones. Sin embargo, la suite de pruebas solo ejecutaba compras secuenciales y nunca simuló concurrencia real.
>
> ## Acciones preventivas
> 1. Agregar `CHECK (stock >= 0)` en la migración de `products` (verificable en `CA-3.1`).
> 2. Bloquear productos con `SELECT ... ORDER BY id FOR UPDATE` dentro de la transacción de checkout (verificable en `CA-3.4`).
> 3. Incorporar una prueba automática con hilos concurrentes en CI que falle si dos órdenes compran la última unidad.

## Versión mala

> El sistema se cayó porque el programador olvidó poner el lock en SQL. Ya lo arreglamos metiendo un `FOR UPDATE` y avisamos al equipo que ponga más atención la próxima vez.

Esta versión falla porque culpa a una persona, omite el impacto medible y la secuencia de hechos, y reemplaza acciones técnicas verificables por un llamado genérico a "poner más atención".

## Rúbrica de 5 puntos

| # | Criterio | Cumple cuando |
| --- | --- | --- |
| 1 | Tono sin culpas | Analiza fallos de diseño, pruebas o procesos sin culpar a individuos. |
| 2 | Impacto concreto | Cuantifica qué falló y cómo afectó al usuario o a los datos. |
| 3 | Secuencia de hechos | Reconstruye el orden técnico de los eventos que dispararon el incidente. |
| 4 | Causa raíz técnica | Identifica los mecanismos y defensas faltantes, más allá del síntoma superficial. |
| 5 | Acciones preventivas verificables | Lista cambios concretos de código, esquema o pruebas automáticas que impiden la repetición. |
