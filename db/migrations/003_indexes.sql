-- Migration 003 (extended): performance index for order_items lookups

-- SOLUTION_START
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id_created_at ON orders (user_id, created_at DESC);
-- SOLUTION_REPLACE
-- -- TODO (extendido): crea un índice que acelere las consultas sobre order_items
-- SELECT 1 WHERE FALSE;
-- SOLUTION_END
