-- Products with low stock (stock <= 5), ordered by stock ascending then sku
-- Columns: sku, name, stock

-- SOLUTION_START
SELECT sku, name, stock
FROM products
WHERE stock <= 5
ORDER BY stock ASC, sku ASC;
-- SOLUTION_REPLACE
-- SELECT '' AS sku, '' AS name, 0 AS stock WHERE FALSE;
-- SOLUTION_END
