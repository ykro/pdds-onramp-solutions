# Cómo se escribe un ADR

Un ADR (*Architecture Decision Record*) es una nota corta que explica por qué el equipo eligió una opción técnica y qué descartó, según la convención de [adr.github.io](https://adr.github.io/). Sirve para que alguien que llega meses después entienda la decisión sin preguntarle a nadie. En el posgrado vas a escribir y defender varios.

Un buen ADR cabe en una pantalla y tiene cuatro partes. Este ejemplo usa una decisión del Paso 2, no la del Paso 4.

## ADR-0000. Guardar los montos como centavos enteros

- **Contexto.** Tiendita calcula precios, descuentos y totales. Con `float`, `0.1 + 0.2` no da `0.3`, y los reportes de ventas no cuadran por centavos.
- **Decisión.** Todo monto se guarda y se calcula como `int` en centavos (`Q 12.50` es `1250`). El redondeo de porcentajes usa half-up con aritmética entera.
- **Alternativas descartadas.** `float` con `round()` en cada cálculo, porque es fácil olvidarlo y `round()` usa otra regla de redondeo. `Decimal`, que también es exacto, pero obliga a convertir en cada frontera con la base de datos y el frontend.
- **Consecuencias.** Los totales cuadran al centavo y los tests comparan enteros exactos. A cambio, cada pantalla debe dividir entre 100 al mostrar, y una persona nueva puede confundir `1250` con mil doscientos cincuenta quetzales.

## Cómo saber si tu ADR está bien

1. Alguien que no estuvo en la discusión entiende el problema solo con el contexto.
2. La decisión es una frase concreta, no una intención.
3. Cada alternativa descartada dice por qué se descartó.
4. Las consecuencias incluyen al menos un costo. Toda decisión tiene uno.
