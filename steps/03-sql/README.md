# Paso 3. SQL, modelado y seguridad de consultas

![Dónde estás](diagrams/where.svg)

Este paso toma unos 75 minutos.

## Antes de empezar

1. Si guardas pedidos y productos en dos hojas de cálculo, ¿qué impide que un pedido apunte a un producto que ya no existe?
2. Un buscador arma su consulta pegando lo que escribe la persona. ¿Qué pasa si esa persona escribe un pedazo de SQL?
3. ¿Por qué conviene excluir pedidos cancelados dentro de las consultas de reportes en lugar de filtrar en memoria después?

## Por qué importa

En el posgrado revisarás consultas escritas por otros y por asistentes de IA. Si no distingues un parámetro de un texto pegado, apruebas una inyección SQL.

## Lo mínimo que necesitas saber

- **Tabla, fila y llave.** Una tabla es como una hoja de cálculo con columnas de tipo fijo. La llave primaria identifica cada fila (`orders.id`) y una llave foránea apunta a la fila de otra tabla (`order_items.order_id` hacia `orders.id`).
- **Leer datos.** `SELECT columnas FROM tabla WHERE condición ORDER BY columna` trae filas. `JOIN ... ON` une filas de dos tablas que coinciden en una columna, por ejemplo cada línea de pedido con su producto.
- **Agrupar.** `GROUP BY columna` junta las filas que comparten un valor y te deja calcular `SUM`, `COUNT` o `AVG` por grupo, como las ventas de cada mes. `WHERE` filtra filas antes de agrupar.
- **Inyección SQL.** Si armas la consulta pegando el texto que escribió alguien (`f"... WHERE sku = '{sku}'"`), ese texto puede cambiar la consulta. Con parámetros (`WHERE sku = %s` y el valor aparte), la base de datos lo trata siempre como dato.
- **Índice.** Una estructura aparte que permite encontrar filas sin leer toda la tabla, como el índice de un libro. `EXPLAIN` muestra si PostgreSQL lo usa (`Index Scan`) o lee todo (`Seq Scan`).

Si nunca escribiste SQL, abre primero [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql) y corre cada consulta.

## Qué vas a hacer

- **Leer**. Levanta PostgreSQL local con `make db-up` (en local necesitas Docker Desktop abierto; `make doctor` te dice si responde) y revisa el esquema ya listo en `db/migrations/001_init.sql`, el diagrama `diagrams/db-schema.svg` y los ejemplos de joins y agrupaciones en [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql).
- **Debuguear**. Abre `psql` con la primera línea (si no conecta, revisa usuario y base en `.env.example`). En otra terminal, abre Python con la segunda y escribe las otras tres:

  ```bash
  docker compose exec db psql -U postgres tiendita
  PYTHONPATH=backend uv run python
  >>> import psycopg
  >>> from tiendita.repositories.orders_repo import find_orders_by_sku
  >>> conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/tiendita")
  ```

  Después llama a `find_orders_by_sku(conn, ...)` de `backend/tiendita/repositories/orders_repo.py` con `SKU-001` y con el texto `' OR '1'='1`. En el primer caso aparecen pedidos que el negocio ya no cuenta; en el segundo, pedidos de todos los productos. Explica por qué pasa cada cosa antes de corregirla.
- **Escribir**. Completa las consultas analíticas en `db/queries/monthly_sales.sql` y `db/queries/top_products.sql` sobre las tablas reales del esquema.

![Esquema de base de datos](diagrams/db-schema.svg)

## Criterios de aceptación

- `CA-3.1` `db/queries/monthly_sales.sql` agrupa las ventas activas por mes (`YYYY-MM`) devolviendo conteo de órdenes e ingresos en centavos.
- `CA-3.2` `db/queries/top_products.sql` devuelve los cinco productos más vendidos ordenados por unidades totales.
- `CA-3.3` `find_orders_by_sku()` pasa el SKU como parámetro y nunca dentro del texto SQL, bloquea el payload `' OR '1'='1` y excluye pedidos cancelados.

## Al terminar

1. Un pedido de marzo pasa de `paid` a `cancelled`. ¿Qué número cambia en tu reporte mensual y por qué conviene que el filtro viva en el SQL?
2. Un compañero propone quitar las comillas de la entrada en Python en lugar de usar `%s`. ¿Qué le responderías?
3. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

Levanta la base de datos local con `make db-up` y ejecuta `make check STEP=3`. Antes de escribir tus consultas, revisa [example/guided_joins_and_groupby.sql](example/guided_joins_and_groupby.sql) o consulta la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. Bajan `order_count` y `revenue_cents` de marzo. Con el filtro en el SQL, cualquier persona o reporte que corra la consulta obtiene la misma cifra, sin depender de que alguien recuerde filtrar después en Python.
2. Que limpiar a mano siempre deja casos fuera (otras comillas, codificaciones, comentarios SQL). Con `%s`, psycopg manda el valor separado del texto de la consulta y PostgreSQL nunca lo interpreta como SQL.
3. Respuesta personal. Debe mencionar el filtro de cancelados, los parámetros `%s` y el `GROUP BY` de cada reporte.
