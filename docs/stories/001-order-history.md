# Historia 001. Consultar historial de pedidos propios

## Historia de usuario

Como cliente de Tiendita, quiero consultar el historial de mis pedidos desde la aplicación para verificar su estado y el total pagado sin pedir ayuda manual.

## Criterios de aceptación

1. Dado un cliente autenticado con pedidos previos, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `200 OK` solo con sus propios pedidos ordenados del más reciente al más antiguo.
2. Dado un cliente autenticado sin compras registradas, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `200 OK` con una lista vacía `[]`.
3. Dado un visitante sin token o con un token vencido, cuando solicita `GET /api/orders/mine`, entonces el sistema responde `401 Unauthorized`.

## Fuera de alcance

- Cancelación o reembolso de pedidos confirmados.
- Descarga de facturas en PDF.
