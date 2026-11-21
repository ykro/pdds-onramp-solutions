# Tiendita Frontend

Interfaz web en React, TypeScript y Vite para el proyecto Tiendita.

## Comandos locales

```bash
cd frontend
npm install
npx tsc --noEmit
npm test
npm run build
```

En desarrollo local, Vite reenvía `/api` hacia `http://localhost:8000`.

## Despliegue en Vercel

El archivo `vercel.json` en la raíz del repositorio sirve `frontend/dist` en `/` y enruta `/api/(.*)` hacia `api/index.py`.

Después de desplegar el proyecto en Vercel, coloca la URL pública en `deploy.json` en la raíz del repositorio:

```json
{
  "app_url": "https://tu-proyecto.vercel.app"
}
```
