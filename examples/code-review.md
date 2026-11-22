# Revisión de código (Code Review)

Una revisión de código busca defectos reales, riesgos de mantenimiento y desalineaciones con los criterios de aceptación antes de hacer merge. Una buena revisión comenta el código con evidencias y respeto, manteniendo la conversación en el diseño y el comportamiento.

## Versión buena

> **Comentario 1 (bloqueante, corrección)** — En `backend/tiendita/services/checkout.py`, línea 42, el descuento porcentual se calcula con `round(subtotal * 0.15)`. Eso convierte el monto a `float` y falla con centavos impares en `CA-2.1`. Sugiero resolverlo con aritmética entera, sin pasar por `float`, y agregar un test con `subtotal = 1055` que documente el redondeo esperado.
>
> **Comentario 2 (bloqueante, concurrencia)** — En `db/queries/checkout.sql`, línea 14, el `SELECT` lee los productos sin `ORDER BY id` antes de `FOR UPDATE`. Si dos carritos traen los mismos productos en orden invertido pueden caer en deadlock. Agregar `ORDER BY id` elimina ese escenario.
>
> **Comentario 3 (sugerencia opcional, legibilidad)** — En `orders.py`, línea 88, el nombre `d` para el diccionario de ítems obliga a leer cinco líneas arriba. Renombrarlo a `items_by_id` mejora la lectura, aunque puedes dejarlo para después si prefieres.
>
> **Resumen** — La separación entre servicio y repositorio quedó limpia y las pruebas de autorización cubren `401` y `403`. Resueltos los dos puntos bloqueantes, queda listo para merge.

## Versión mala

> Esto está mal hecho, ¿por qué usaste `float`? Además los nombres de variables son horribles y todo el archivo parece desordenado. Cámbialo por completo.

Esta versión falla porque ataca el tono personal, omite archivo y línea, mezcla preferencias de estilo con bugs reales y deja al autor sin una acción concreta para avanzar.

## Rúbrica de 5 puntos

| # | Criterio | Cumple cuando |
| --- | --- | --- |
| 1 | Ubicación precisa | Cada observación señala archivo, función o línea específica. |
| 2 | Severidad explícita | Distingue entre bloqueantes (bugs, seguridad, contrato) y sugerencias menores de estilo. |
| 3 | Explicación del impacto | Explica qué falla o qué riesgo aparece en producción si el código queda igual. |
| 4 | Propuesta accionable | Ofrece una alternativa concreta o un caso de prueba que reproduce el problema. |
| 5 | Tono constructivo y balance | Critica el código con respeto y reconoce también lo que está bien resuelto. |
