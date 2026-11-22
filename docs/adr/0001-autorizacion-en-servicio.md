# ADR-0001. La autorización de pedidos vive en el servicio

## Contexto

`GET /api/orders/mine` devolvía pedidos de otras cuentas. El repositorio filtra por `user_id` en el SQL, pero el repositorio puede cambiar, y un test con un repositorio falso mostró que nada más protegía la regla.

## Decisión

`StoreService.get_my_orders` vuelve a filtrar por el `user_id` del token, aunque el repositorio ya lo haga.

## Alternativas descartadas

- Confiar solo en el `WHERE user_id = %s` del SQL, porque un cambio en el repositorio rompe la regla sin que falle ningún test.
- Filtrar en la ruta de `app.py`, porque mezcla HTTP con reglas del negocio y obliga a repetir el filtro en cada ruta nueva.

## Consecuencias

La regla se prueba sin base de datos y sigue en pie si alguien cambia el repositorio. A cambio, el filtro se hace dos veces y alguien nuevo puede pensar que sobra.
