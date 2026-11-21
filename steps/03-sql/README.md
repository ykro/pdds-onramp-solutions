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

1. ¿Qué integridad garantiza una llave foránea junto con un constraint `CHECK` en PostgreSQL frente a validar solo en Python? (Pista, revisa `db/migrations/001_init.sql` y `diagrams/db-schema.svg`.)
2. ¿Por qué concatenar entrada del usuario en un f-string de SQL abre una vulnerabilidad de inyección SQL y cómo la bloquean los parámetros `%s`? (Pista, revisa `find_orders_by_sku()` en `backend/tiendita/repositories/orders_repo.py`.)
3. ¿Por qué conviene excluir pedidos cancelados dentro de las consultas de reportes en lugar de filtrar en memoria después? (Pista, revisa `example/guided_joins_and_groupby.sql`.)

## Cómo verificar

Levanta la base de datos local con `make db-up` y ejecuta `make check STEP=3`. Antes de escribir tus consultas, revisa [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql) o consulta la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. PostgreSQL aplica las llaves foráneas y los constraints `CHECK` en cada escritura sin importar qué servicio, script o migración toque la tabla. Así impide registros huérfanos o stock negativo incluso cuando falla una validación en la capa de aplicación.
2. Un f-string mezcla datos con instrucciones SQL, permitiendo que un texto como `' OR '1'='1` altere la cláusula `WHERE` y exponga filas ajenas. Al pasar parámetros `%s`, el driver envía la plantilla SQL y los valores por separado, de modo que PostgreSQL trata la entrada únicamente como texto literal.
3. Filtrar en el `WHERE` antes de agrupar reduce las filas que la base de datos lee, une y transfiere por red, y evita que un olvido en el código consumidor infle ingresos o unidades vendidas con pedidos cancelados.
