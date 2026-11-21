-- Top 5 products by total units sold (excluding cancelled orders)
-- Columns: sku, name, units_sold

-- SOLUTION_START
SELECT
    p.sku,
    p.name,
    SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o ON o.id = oi.order_id
WHERE o.status <> 'cancelled'
GROUP BY p.id, p.sku, p.name
ORDER BY units_sold DESC, p.sku ASC
LIMIT 5;
-- SOLUTION_REPLACE
-- SELECT '' AS sku, '' AS name, 0 AS units_sold WHERE FALSE;
-- SOLUTION_END
