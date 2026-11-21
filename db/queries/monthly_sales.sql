-- Monthly sales excluding cancelled orders, ordered chronologically
-- Columns: month (YYYY-MM), order_count, revenue_cents

-- SOLUTION_START
SELECT
    TO_CHAR(created_at AT TIME ZONE 'UTC', 'YYYY-MM') AS month,
    COUNT(*) AS order_count,
    SUM(total_cents) AS revenue_cents
FROM orders
WHERE status <> 'cancelled'
GROUP BY 1
ORDER BY 1;
-- SOLUTION_REPLACE
-- SELECT '' AS month, 0 AS order_count, 0 AS revenue_cents WHERE FALSE;
-- SOLUTION_END
