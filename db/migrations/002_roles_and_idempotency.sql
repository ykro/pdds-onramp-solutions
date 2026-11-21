-- Migration 002: admin roles and idempotency keys (applied on top of live 001 data)

-- SOLUTION_START
CREATE TABLE IF NOT EXISTS admins (
    user_id TEXT PRIMARY KEY,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- SOLUTION_REPLACE
-- -- TODO: crea las tablas admins e idempotency_keys sin modificar 001_init.sql
-- SELECT 1 WHERE FALSE;
-- SOLUTION_END
