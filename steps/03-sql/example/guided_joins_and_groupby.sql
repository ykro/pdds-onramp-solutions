-- Ejemplo guiado para el Paso 3.
-- Practica JOIN, GROUP BY, HAVING y agregaciones antes de implementar transacciones.
-- Asume las tablas de Tiendita: products, orders y order_items.

-- 1. INNER JOIN básico
-- Une cada línea de pedido con el nombre del producto y calcula el subtotal por línea.
-- Todas las cifras monetarias viven en centavos enteros (INTEGER o BIGINT).
SELECT
    oi.order_id,
    p.name AS product_name,
    oi.quantity,
    oi.unit_price_cents,
    (oi.quantity * oi.unit_price_cents) AS line_total_cents
FROM order_items AS oi
INNER JOIN products AS p
    ON p.id = oi.product_id
ORDER BY oi.order_id, p.name;

-- 2. LEFT JOIN para encontrar productos sin ventas
-- LEFT JOIN conserva todas las filas de products aunque no existan en order_items.
-- COALESCE reemplaza NULL por 0 cuando un producto todavía no se ha vendido.
SELECT
    p.id,
    p.name,
    COALESCE(SUM(oi.quantity), 0) AS units_sold
FROM products AS p
LEFT JOIN order_items AS oi
    ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY units_sold DESC, p.name ASC;

-- 3. GROUP BY + HAVING
-- Filtra primero las filas individuales con WHERE (por ejemplo, órdenes confirmadas)
-- y filtra después los grupos agregados con HAVING (categorías con al menos 2 unidades).
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id) AS orders_count,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price_cents) AS gross_revenue_cents
FROM order_items AS oi
INNER JOIN orders AS o
    ON o.id = oi.order_id
INNER JOIN products AS p
    ON p.id = oi.product_id
WHERE o.status = 'confirmed'
GROUP BY p.category
HAVING SUM(oi.quantity) >= 2
ORDER BY gross_revenue_cents DESC, p.category ASC;

-- 4. Verificación mental antes de pasar a transacciones
-- Observa que SUM(...) nunca debe devolverse como FLOAT; usa BIGINT o INTEGER
-- y valida el plan de ejecución con EXPLAIN ANALYZE sobre datos reales.
