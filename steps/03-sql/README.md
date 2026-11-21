# Paso 3. SQL, modelado y concurrencia

![Dónde estás](diagrams/where.svg)

## Por qué importa

Una tienda real guarda pedidos en disco y atiende a varios compradores al mismo tiempo. Entender esquemas relacionales e índices como enseña [CMU 15-445](https://15445.courses.cs.cmu.edu/) junto con [Use The Index, Luke](https://use-the-index-luke.com/), y controlar transacciones como explica el capítulo 7 de *Designing Data-Intensive Applications* (Kleppmann), impide vender dos veces el último producto en stock.

## Qué se construye

**Núcleo**
- Migraciones SQL en PostgreSQL para usuarios, productos, órdenes e ítems con llaves foráneas, `CHECK` constraints y precios en centavos.
- Consultas analíticas con `JOIN`, `GROUP BY` y agregaciones para ventas por categoría e historial de cliente.
- Una función transaccional de checkout que usa `SELECT ... FOR UPDATE` según la [documentación de PostgreSQL](https://www.postgresql.org/docs/current/explicit-locking.html) para eliminar race conditions de inventario.

**Extendido**
- Índices compuestos validados con `EXPLAIN ANALYZE` para acelerar consultas de historial y catálogo.
- Un postmortem breve que documenta una race condition reproducida y su corrección.

![Esquema de base de datos](diagrams/db-schema.svg)

![Race condition en inventario](diagrams/race-condition.svg)

## Criterios de aceptación

- `CA-3.1` [auto, núcleo] Las migraciones crean todas las tablas con restricciones `NOT NULL`, `CHECK` y llaves foráneas que rechazan datos inválidos.
- `CA-3.2` [auto, núcleo] Las consultas de reporte devuelven ventas por categoría, productos más vendidos e historial de órdenes con totales exactos.
- `CA-3.3` [auto, núcleo] El checkout transaccional descuenta stock y registra la orden de forma atómica, revertiendo todo ante un error intermedio.
- `CA-3.4` [auto, núcleo] Bajo solicitudes concurrentes sobre la última unidad disponible, exactamente una orden tiene éxito y el stock nunca baja de cero.
- `CA-3.5` [rubric, núcleo] El diseño del esquema y las consultas muestran nombres claros, tipos exactos y cero redundancia injustificada.
- `CA-3.6` [auto, extendido] Los planes de `EXPLAIN ANALYZE` confirman el uso de índices en las consultas principales sin `Seq Scan` sobre tablas grandes.
- `CA-3.7` [rubric, extendido] El postmortem del incidente de concurrencia cumple los 5 criterios de `examples/postmortem.md`.

## Cómo verificar

Ejecuta `make check STEP=3` para el núcleo y `make check STEP=3 EXTRA=1` para los criterios extendidos. Practica con `make self-check STEP=3`. Antes de entrar a transacciones, revisa las consultas comentadas en [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql) o consulta la [primera pista](hints/1.md).
