# Reto opcional: deploy en Neon y Vercel

Neon ofrece dos URLs: usa la directa (sin `-pooler`) para las migraciones desde tu terminal y la pooled en Vercel.

1. En Neon Console abre tu proyecto, activa **Neon Auth**, agrega tu dominio `https://<tu-app>.vercel.app` en **Trusted Domains** y copia el **Auth URL** junto con el **JWKS URL** (`.../.well-known/jwks.json`).
2. Aplica las migraciones con la URL directa: `DIRECT_DATABASE_URL="<tu-url-directa>" make migrate`.
3. En Vercel, dentro de **Project Settings -> Environment Variables**, agrega para Production `DATABASE_URL` (la URL pooled), `NEON_AUTH_JWKS_URL` (el JWKS URL) y `VITE_NEON_AUTH_URL` (el Auth URL base).
4. Haz deploy, registra tu URL pública en `deploy.json` (`{"app_url": "https://tu-app.vercel.app"}`) y corre `make check-prod`.
