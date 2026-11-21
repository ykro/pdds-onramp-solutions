# Registro de Decisión Arquitectónica (ADR)

Un ADR documenta una decisión técnica relevante en el momento en que se toma. Sirve para que cualquier persona del equipo entienda meses después qué opciones se evaluaron, qué restricciones pesaron y qué trade-offs se aceptaron.

## Versión buena

> # ADR-0002. Representar precios en centavos enteros
>
> ## Contexto
> Tiendita calcula subtotales, cupones porcentuales e impuestos en Python, guarda montos en PostgreSQL y los muestra en React con TypeScript. Usar `float` en Python o `DOUBLE PRECISION` en SQL introduce errores binarios de redondeo como `0.1 + 0.2 = 0.30000000000000004`, provocando diferencias entre el total mostrado y el cobrado.
>
> ## Decisión
> Almacenamos y transportamos todos los montos monetarios como enteros en centavos (`int` en Python, `INTEGER` o `BIGINT` en PostgreSQL, `number` entero en JSON y TypeScript) con el sufijo explícito `_cents` en cada campo. La conversión a formato decimal ocurre únicamente en la capa de presentación del frontend.
>
> Se descartó usar `Decimal` serializado como texto en todo el stack porque exige librerías extra en TypeScript y complica las agregaciones rápidas en consultas analíticas cuando todas las ventas usan una sola moneda.
>
> ## Consecuencias
> - **Ventajas** — Cero errores de redondeo binario en sumas, comparación exacta en pruebas y tipos nativos en Python, PostgreSQL y JSON.
> - **Trade-offs aceptados** — Si Tiendita soporta monedas sin subdivisión decimal (como JPY) o divisas múltiples en el futuro, habrá que agregar una columna `currency` y migrar el formateo.
> - **Mitigación** — El sufijo `_cents` evita confundir unidades monetarias al leer cualquier contrato o tabla.

## Versión mala

> # Decisión de dinero
>
> Vamos a usar enteros para los precios porque los flotantes son malos y en la industria todos recomiendan enteros. Es mucho más fácil y rápido.

Esta versión falla porque omite el contexto concreto del sistema, ignora alternativas consideradas y esconde las limitaciones o consecuencias que el equipo deberá vigilar después.

## Rúbrica de 5 puntos

| # | Criterio | Cumple cuando |
| --- | --- | --- |
| 1 | Estructura completa | Contiene claramente las secciones `Contexto`, `Decisión` y `Consecuencias`. |
| 2 | Contexto verificable | Explica el problema técnico, las restricciones reales del proyecto y por qué urge decidir. |
| 3 | Alternativas evaluadas | Menciona al menos una alternativa descartada y la razón concreta para descartarla. |
| 4 | Decisión sin ambigüedad | Deja claro qué se adopta y dónde aplica dentro de la arquitectura. |
| 5 | Consecuencias y trade-offs | Reconoce tanto beneficios como costos, riesgos o límites que asume el equipo. |
