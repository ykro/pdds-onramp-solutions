# Reto opcional: deploy en Neon y Vercel

Neon ofrece dos URLs: usa la directa (sin `-pooler`) para correr migraciones desde tu terminal y la pooled en Vercel.

1. Crea tu proyecto en **Neon Console** y aplica las migraciones con la URL directa:
   `DIRECT_DATABASE_URL="<tu-url-directa>" make migrate`
2. En el mismo proyecto de Neon, activa **Neon Auth**, crea un usuario de prueba en la consola y copia el **Auth URL** junto con el **JWKS URL** (`.../.well-known/jwks.json`).
3. Importa tu repositorio en **Vercel** dejando **Root Directory** en `.`. En **Project Settings -> Environment Variables** (entorno Production), agrega únicamente:
   - `DATABASE_URL` (la URL pooled de Neon)
   - `NEON_AUTH_JWKS_URL` (el JWKS URL de Neon Auth)
   - `VITE_NEON_AUTH_URL` (el Auth URL base de Neon Auth)
   No copies `JWT_ISSUER` ni `JWT_AUDIENCE` de `.env.example`, porque esos valores corresponden al entorno local. Haz el primer deploy y copia el dominio `https://<tu-app>.vercel.app` que asigna Vercel.
4. Vuelve a **Neon Auth** en Neon Console y agrega `https://<tu-app>.vercel.app` en **Trusted Domains**.
5. Si agregaste o modificaste `VITE_NEON_AUTH_URL` después del primer deploy, lanza un **Redeploy** en Vercel para que el build de Vite tome la variable.
6. Registra tu URL pública en `deploy.json` (`{"app_url": "https://tu-app.vercel.app"}`) y corre `make check-prod`.
