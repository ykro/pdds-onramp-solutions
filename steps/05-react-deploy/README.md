# Paso 5. React, TypeScript y deploy en producción

![Dónde estás](diagrams/where.svg)

## Por qué importa

El software entrega valor cuando un usuario real abre la tienda en su navegador y completa una compra sin fricciones. Construir componentes declarativos siguiendo [Thinking in React](https://react.dev/learn/thinking-in-react) y [Full Stack Open](https://fullstackopen.com/en/), con tipos estrictos del [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) y *Effective TypeScript* (Vanderkam), cierra el ciclo desde el código local hasta la nube. Si vienes de Python, lee primero [example/python_vs_typescript.md](example/python_vs_typescript.md).

## Qué se construye

**Núcleo**
- El hook `frontend/src/hooks/useCart.ts` y las vistas `LoginView`, `CatalogView` y `OrdersView` verificadas con `vitest` y React Testing Library, siguiendo [web.dev Learn Accessibility](https://web.dev/learn/accessibility).
- La conexión con [Neon](https://neon.com/docs/guides/neon-auth) y Neon Auth más el deploy de un solo proyecto en [Vercel Python](https://vercel.com/docs/functions/runtimes/python), registrando `app_url` en `deploy.json`.

**Extendido**
- Pruebas E2E con Playwright y `axe-core` en `frontend/e2e/checkout.spec.ts` junto con una auditoría informativa mediante `npm audit`.

![Arquitectura de deploy](diagrams/deployment.svg)

## Criterios de aceptación

- `CA-5.1` [auto, núcleo] `frontend/` pasa `npm run typecheck` y `npm run build`.
- `CA-5.2` [auto, núcleo] `useCart` y las 3 vistas pasan `vitest` y React Testing Library.
- `CA-5.3` [auto, núcleo] `deploy.json` contiene `app_url` y `make check-prod` confirma `/api/health` (`200`), `/api/orders/mine` (`401`) y `/`.
- `CA-5.4` [auto, extendido] `frontend/e2e/checkout.spec.ts` recorre catálogo, carrito y pago con `axe-core` sin violaciones críticas ni serias.

## Cómo verificar

Ejecuta `make check STEP=5` para validar el núcleo en local, `make check-prod` para comprobar tu deploy en Vercel y `make check STEP=5 EXTRA=1` para correr Playwright con `axe-core`. Corre `make self-check STEP=5` para la autoevaluación formativa, o abre la [primera pista](hints/1.md).
