# Paso 5. React, TypeScript y deploy en producción

![Dónde estás](diagrams/where.svg)

## Por qué importa

El software entrega valor cuando un usuario real abre la tienda en su navegador y completa una compra sin fricciones. Construir componentes declarativos siguiendo [Thinking in React](https://react.dev/learn/thinking-in-react) y [Full Stack Open](https://fullstackopen.com/en/), con tipos estrictos del [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) y *Effective TypeScript* (Vanderkam), cierra el ciclo desde el código local hasta la nube.

## Qué se construye

**Núcleo**
- La interfaz de Tiendita en React y TypeScript con catálogo, carrito, checkout e historial conectados al API real.
- Estados explícitos de carga, error y vacío, más controles accesibles con teclado y etiquetas semánticas según [web.dev Learn Accessibility](https://web.dev/learn/accessibility).
- Integración de sesión con [Neon Auth](https://neon.com/docs/guides/neon-auth) y configuración lista para deploy de frontend y backend en [Vercel Python](https://vercel.com/docs/functions/runtimes/python).

**Extendido**
- Deploy público funcional en Vercel y Neon con smoke tests automatizados corriendo sobre la URL en producción.

![Arquitectura de deploy](diagrams/deployment.svg)

## Criterios de aceptación

- `CA-5.1` [auto, núcleo] El proyecto compila con `tsc --noEmit` en modo estricto sin `any` implícitos y supera las pruebas de componentes.
- `CA-5.2` [auto, núcleo] El usuario navega el catálogo, agrega productos al carrito, aplica cupones y completa una orden reflejada en el historial.
- `CA-5.3` [auto, núcleo] Todos los formularios, botones y alertas manejan estados de carga y error con roles ARIA y navegación completa por teclado.
- `CA-5.4` [auto, extendido] El deploy en vivo en Vercel conectado a Neon responde `200` en `/health`, autentica usuarios y pasa el smoke test de compra.

## Cómo verificar

Ejecuta `make check STEP=5` para el núcleo y `make check STEP=5 EXTRA=1` para el smoke test en producción. Corre `make self-check STEP=5` para responder las preguntas de autoevaluación formativa. Si vienes de Python y es tu primer contacto con TypeScript, lee [example/python_vs_typescript.md](example/python_vs_typescript.md) o consulta la [primera pista](hints/1.md).
