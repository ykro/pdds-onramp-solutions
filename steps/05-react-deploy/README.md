# Paso 5. React, TypeScript y deploy en producción

![Dónde estás](diagrams/where.svg)

## Antes de empezar

1. ¿Qué ventajas da tipar las respuestas del backend en TypeScript antes de renderizarlas en una vista de React? (Pista, revisa `example/python_vs_typescript.md` y `frontend/src/lib/api.ts`.)
2. ¿Por qué conviene derivar totales como `totalCents` desde la lista de ítems del carrito en lugar de guardar un segundo estado manual? (Pista, revisa `frontend/src/hooks/useCart.ts`.)
3. ¿Qué valida un smoke test sobre producción que las pruebas unitarias locales dejan fuera? (Pista, revisa `diagrams/deployment.svg` y `backend/tests/step5/test_prod_deploy.py`.)

## Por qué importa

El valor técnico se comprueba cuando el frontend tipado conversa con el API real, autentica usuarios y responde estable en producción. Comprender el flujo de datos declarativo de [Thinking in React](https://react.dev/learn/thinking-in-react) y [Full Stack Open](https://fullstackopen.com/en/), apoyado en el [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) y *Effective TypeScript* (Vanderkam), te da criterio para diagnosticar fallas de punta a punta desde el navegador hasta la nube.

## Qué vas a hacer

- **Leer**. Revisa [example/python_vs_typescript.md](example/python_vs_typescript.md) si vienes de Python, y luego inspecciona `frontend/src/lib/api.ts`, `frontend/src/lib/auth.ts` y `frontend/src/views/CatalogView.tsx` para seguir cómo el navegador autentica sesiones y llama al backend.
- **Debuguear**. Corrige el bug en `totalCents` dentro de `frontend/src/hooks/useCart.ts`, donde el cálculo suma el precio unitario de cada producto sin multiplicarlo por `quantity`.
- **Escribir**. Conecta tu copia a Neon y [Neon Auth](https://neon.com/docs/guides/neon-auth), haz deploy del proyecto completo en [Vercel](https://vercel.com/docs/functions/runtimes/python) y registra tu URL pública en `app_url` dentro de `deploy.json`.

![Arquitectura de deploy](diagrams/deployment.svg)

## Referencia visual

Así se ven las tres vistas cuando la aplicación está lista.

![Vista de inicio de sesión](../../docs/screenshots/01-login.png)

![Vista de catálogo y carrito](../../docs/screenshots/02-catalog.png)

![Vista de mis pedidos](../../docs/screenshots/03-orders.png)

## Criterios de aceptación

- `CA-5.1` `frontend/` pasa `npm run typecheck` y `npm run build` sin errores.
- `CA-5.2` `useCart` y las tres vistas principales pasan la suite de pruebas en `vitest`.
- `CA-5.3` `deploy.json` apunta a tu URL de Vercel y `make check-prod` confirma `/api/health`, `/api/products`, `/api/orders/mine` y `/`.

## Al terminar

1. ¿Qué ventajas da tipar las respuestas del backend en TypeScript antes de renderizarlas en una vista de React? (Pista, revisa `example/python_vs_typescript.md` y `frontend/src/lib/api.ts`.)
2. ¿Por qué conviene derivar totales como `totalCents` desde la lista de ítems del carrito en lugar de guardar un segundo estado manual? (Pista, revisa `frontend/src/hooks/useCart.ts`.)
3. ¿Qué valida un smoke test sobre producción que las pruebas unitarias locales dejan fuera? (Pista, revisa `diagrams/deployment.svg` y `backend/tests/step5/test_prod_deploy.py`.)

## Cómo verificar

Ejecuta `make check STEP=5` para validar el frontend y las pruebas en local, y corre `make check-prod` cuando tu app esté desplegada en Vercel. Revisa [example/python_vs_typescript.md](example/python_vs_typescript.md) o empieza por la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. TypeScript verifica en tiempo de compilación que los campos usados en las vistas coincidan con el contrato del API. Así atrapa nombres mal escritos, tipos incompatibles y valores opcionales antes de que lleguen al navegador del usuario.
2. Calcular `totalCents` con `useMemo` a partir de `items` mantiene una sola fuente de verdad. Cada alta, baja o cambio de cantidad recalcula el monto exacto sin riesgo de desincronizar dos estados separados.
3. Un smoke test contra la URL desplegada comprueba variables de entorno reales, conectividad con Neon, validación JWKS contra Neon Auth, ruteo entre frontend y funciones de Vercel y comportamiento tras un cold start.
