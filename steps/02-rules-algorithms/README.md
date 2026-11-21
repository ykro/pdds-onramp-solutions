# Paso 2. Reglas de negocio y algoritmos

![Dónde estás](diagrams/where.svg)

## Por qué importa

El dinero calculado con punto flotante acumula errores de redondeo que arruinan facturas y cierres de caja. Modelar precios en centavos enteros, elegir estructuras eficientes como explica [Runestone Python DS](https://runestone.academy/ns/books/published/pythonds3/index.html) y *Grokking Algorithms* (Bhargava), y blindar cada regla con pruebas automatizadas garantiza resultados exactos antes de tocar una base de datos.

## Qué se construye

**Núcleo**
- Un motor de carrito y checkout en Python puro que opera con enteros en centavos y diseña interfaces simples siguiendo *A Philosophy of Software Design* (Ousterhout).
- Reglas de cupones, impuestos y validación de stock probadas con [pytest](https://docs.pytest.org/) bajo el ciclo de [Test-Driven Development with Python](https://www.obeythetestinggoat.com/).
- Pruebas unitarias capaces de detectar versiones con bugs plantados en la lógica de precios.

**Extendido**
- Búsqueda eficiente de productos por prefijo y rango de precio usando índices en memoria y búsqueda binaria.
- Pruebas basadas en propiedades que verifican invariantes del total del carrito ante entradas aleatorias.

## Criterios de aceptación

- `CA-2.1` [auto, núcleo] Todos los cálculos monetarios usan centavos en `int` y producen totales, impuestos y descuentos exactos sin `float`.
- `CA-2.2` [auto, núcleo] El motor valida cantidades positivas, existencia en catálogo y límites de stock disponibles antes de confirmar.
- `CA-2.3` [auto, núcleo] Los cupones porcentuales y de monto fijo respetan fechas de vigencia, mínimo de compra y nunca producen totales negativos.
- `CA-2.4` [auto, núcleo] Las funciones del dominio permanecen puras y desacopladas de entrada, salida y base de datos.
- `CA-2.5` [auto, núcleo] Tu suite de `pytest` falla cuando se ejecuta contra las versiones con bugs plantados del verificador y pasa con la implementación correcta.
- `CA-2.6` [auto, extendido] La búsqueda por rango de precios y prefijo responde con complejidad sublineal sobre catálogos grandes.
- `CA-2.7` [auto, extendido] Las pruebas de propiedades verifican que el total siempre permanece no negativo y coherente al reordenar ítems.

## Cómo verificar

Corre las verificaciones del núcleo con `make check STEP=2` y las extendidas con `make check STEP=2 EXTRA=1`. Ejecuta las preguntas de autoevaluación formativa con `make self-check STEP=2`. Consulta el ejemplo resuelto en [example/discount_example.py](example/discount_example.py) o empieza por la [primera pista](hints/1.md).
