-- Monthly sales excluding cancelled orders, ordered chronologically
-- Columns: month (YYYY-MM), order_count, revenue_cents

SELECT
    TO_CHAR(created_at AT TIME ZONE 'UTC', 'YYYY-MM') AS month,
    COUNT(*) AS order_count,
    SUM(total_cents) AS revenue_cents
FROM orders
WHERE status <> 'cancelled'
GROUP BY 1
ORDER BY 1;
