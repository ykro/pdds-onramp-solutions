# Paso 3. SQL, modelado y seguridad de consultas

![Dónde estás](diagrams/where.svg)

## Antes de empezar

1. ¿Qué integridad garantiza una llave foránea junto con un constraint `CHECK` en PostgreSQL frente a validar solo en Python? (Pista, revisa `db/migrations/001_init.sql` y `diagrams/db-schema.svg`.)
2. ¿Por qué concatenar entrada del usuario en un f-string de SQL abre una vulnerabilidad de inyección SQL y cómo la bloquean los parámetros `%s`? (Pista, revisa `find_orders_by_sku()` en `backend/tiendita/repositories/orders_repo.py`.)
3. ¿Por qué conviene excluir pedidos cancelados dentro de las consultas de reportes en lugar de filtrar en memoria después? (Pista, revisa `example/guided_joins_and_groupby.sql`.)

## Por qué importa

Toda aplicación de negocio depende de un esquema relacional sano y de consultas seguras que respondan con datos correctos. Conocer cómo organiza y ejecuta consultas una base de datos según [CMU 15-445](https://15445.courses.cs.cmu.edu/) y la [documentación oficial de PostgreSQL](https://www.postgresql.org/docs/current/) te permite detectar riesgos de seguridad y cuello de botella en revisiones técnicas. Complementar esa base con *Designing Data-Intensive Applications* (Kleppmann) y [Use The Index, Luke](https://use-the-index-luke.com/) da criterio sólido al auditar datos en producción.

## Qué vas a hacer

- **Leer**. Levanta PostgreSQL local con `make db-up` y revisa el esquema ya listo en `db/migrations/001_init.sql`, el diagrama `diagrams/db-schema.svg` y los ejemplos de joins y agrupaciones en [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql).
- **Debuguear**. Corrige `find_orders_by_sku()` en `backend/tiendita/repositories/orders_repo.py` para reemplazar la interpolación directa por parámetros `%s` contra inyección SQL y excluir pedidos con estado `cancelled`.
- **Escribir**. Completa las consultas analíticas en `db/queries/monthly_sales.sql` y `db/queries/top_products.sql` sobre las tablas reales del esquema.

![Esquema de base de datos](diagrams/db-schema.svg)

## Criterios de aceptación

- `CA-3.1` `db/queries/monthly_sales.sql` agrupa las ventas activas por mes (`YYYY-MM`) devolviendo conteo de órdenes e ingresos en centavos.
- `CA-3.2` `db/queries/top_products.sql` devuelve los cinco productos más vendidos ordenados por unidades totales.
- `CA-3.3` `find_orders_by_sku()` bloquea el payload `' OR '1'='1` mediante consultas parametrizadas y excluye pedidos cancelados.

## Al terminar

1. Un pedido de marzo pasa de `paid` a `cancelled`. ¿Qué número cambia en tu reporte mensual y por qué conviene que el filtro viva en el SQL?
2. Un compañero propone quitar las comillas de la entrada en Python en lugar de usar `%s`. ¿Qué le responderías?
3. `top_products` se vuelve lento cuando `order_items` llega a millones de filas. ¿Qué índice probarías y cómo comprobarías que PostgreSQL lo usa?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

Levanta la base de datos local con `make db-up` y ejecuta `make check STEP=3`. Antes de escribir tus consultas, revisa [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql) o consulta la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. Bajan `order_count` y `revenue_cents` de marzo. Con el filtro en el SQL, cualquier persona o reporte que corra la consulta obtiene la misma cifra, sin depender de que alguien recuerde filtrar después en Python.
2. Que limpiar a mano siempre deja casos fuera (otras comillas, codificaciones, comentarios SQL). Con `%s`, psycopg manda el valor separado del texto de la consulta y PostgreSQL nunca lo interpreta como SQL.
3. Un índice sobre `order_items(product_id)` o sobre `order_items(order_id)`, según el plan. Se comprueba con `EXPLAIN ANALYZE` antes y después: el plan debe pasar de `Seq Scan` a un `Index Scan` o `Bitmap Index Scan`.
4. Respuesta personal. Debe mencionar el filtro de cancelados, los parámetros `%s` y el `GROUP BY` de cada reporte.
