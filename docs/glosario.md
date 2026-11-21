# Glosario de ingeniería de software

Este glosario reúne términos frecuentes en equipos de ingeniería que aparecen a lo largo de los 5 pasos de Tiendita. Cada definición va directo a cómo se usa en el día a día.

## CI/CD

Integración continua (CI) y entrega o deploy continuo (CD). En CI, un servidor como [GitHub Actions](https://docs.github.com/en/actions) ejecuta pruebas y verificaciones cada vez que subes cambios a una rama. En CD, los cambios que pasan esas verificaciones se publican automáticamente hacia un entorno de pruebas o producción.

## CORS (Cross-Origin Resource Sharing)

Mecanismo de seguridad aplicado por los navegadores web, documentado en [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS). Cuando tu frontend en un dominio (por ejemplo `https://tiendita.vercel.app`) llama a un backend en otro origen, el navegador exige que el backend autorice explícitamente ese origen mediante encabezados HTTP como `Access-Control-Allow-Origin`.

## Deuda técnica

Costo adicional de mantenimiento que acumula un equipo cuando elige un atajo rápido en lugar de un diseño limpio. Al igual que una deuda financiera, puede ser una decisión consciente para aprender o salir antes, siempre que el equipo registre qué quedó pendiente y lo pague antes de que frene cada cambio futuro.

## Estimación

Pronóstico aproximado del esfuerzo o complejidad necesaria para completar una historia o tarea técnica. Una estimación sirve para priorizar y coordinar dependencias entre personas, nunca como una promesa exacta grabada en piedra.

## Hotfix

Cambio pequeño y urgente que se aplica directamente para corregir un fallo crítico en producción sin esperar al ciclo normal de lanzamientos. Después de hacer deploy del hotfix, el equipo integra ese cambio de vuelta a la rama principal y agrega una prueba que impida la regresión.

## Idempotencia

Propiedad de una operación que produce exactamente el mismo efecto aunque el cliente la ejecute varias veces con la misma entrada o llave (`Idempotency-Key`), como explica [Stripe Idempotency](https://stripe.com/blog/idempotency). En pagos y creación de órdenes evita cobros duplicados cuando el usuario reintenta ante una caída de red.

## Incidente

Evento no planificado que degrada o interrumpe un servicio para los usuarios, o que corrompe datos del negocio (por ejemplo, vender más unidades de las disponibles en inventario). Todo incidente serio se atiende primero restaurando el servicio y después analizando causas en un postmortem sin culpas.

## JWKS (JSON Web Key Set)

Documento JSON público expuesto por un proveedor de identidad (como Neon Auth) que contiene las llaves criptográficas públicas usadas para verificar la firma de los tokens JWT, según [RFC 7517](https://datatracker.ietf.org/doc/html/rfc7517). El backend consulta este endpoint y guarda las llaves en caché local para validar firmas sin llamar al proveedor en cada request.

## JWT (JSON Web Token)

Formato estándar ([RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)) para transmitir afirmaciones firmadas entre dos sistemas en formato compacto (`header.payload.signature`). El payload suele estar codificado en Base64URL y cualquier persona puede leerlo, por eso la confianza depende siempre de verificar su firma criptográfica, emisor (`iss`), audiencia (`aud`) y expiración (`exp`) en el servidor.

## Race condition

Defecto de concurrencia donde el resultado final de un programa cambia según el orden exacto en que se intercalan dos o más operaciones simultáneas. En Tiendita ocurre cuando dos compradores consultan `stock = 1` en paralelo y ambos logran confirmar la compra si falta un bloqueo de fila (`SELECT ... FOR UPDATE`).

## Rollback

Acción de revertir un deploy, una migración o una transacción de base de datos al último estado estable conocido cuando aparece un fallo grave. Diseñar cambios pequeños y compatibles hacia atrás hace que un rollback sea rápido y seguro.
