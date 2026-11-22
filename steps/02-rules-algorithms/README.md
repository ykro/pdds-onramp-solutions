# Paso 2. Reglas de negocio y algoritmos

![Dónde estás](diagrams/where.svg)

Este paso toma unos 75 minutos.

## Antes de empezar

1. ¿Por qué calcular precios con números de punto flotante (`float`) genera errores silenciosos en una tienda en línea? (Pista, revisa `backend/tiendita/pricing.py` y `example/discount_example.py`.)
2. ¿Cómo cambia el tiempo de respuesta de una búsqueda lineal frente a un diccionario cuando el catálogo crece de 1,000 a 100,000 productos? (Pista, ejecuta `make bench` y lee `backend/tiendita/search.py`.)
3. ¿Qué ventaja da escribir pruebas automatizadas sobre edge cases de negocio antes de tocar una base de datos o un servidor web? (Pista, revisa `backend/tests/step2/test_student_pricing.py`.)

## Por qué importa

Los bugs más caros en producción suelen vivir en reglas de negocio pequeñas y en estructuras de datos mal elegidas para el tamaño real del sistema. Comprender complejidad algorítmica como explican [Problem Solving with Algorithms and Data Structures using Python](https://runestone.academy/ns/books/published/pythonds3/index.html) y *Grokking Algorithms* (Bhargava) te ayuda a evaluar decisiones de rendimiento con datos medidos. A la vez, mantener módulos simples como plantea *A Philosophy of Software Design* (Ousterhout) y validarlos con [pytest](https://docs.pytest.org/) permite cambiar reglas sin romper cálculos existentes.

## Qué vas a hacer

- **Leer**. Corre `make bench` y lee `scripts/bench_search.py` junto con `backend/tiendita/search.py` para observar cómo escala una búsqueda lineal frente a un diccionario al pasar de 1,000 a 100,000 productos.
- **Debuguear**. Corre `make check STEP=2` y lee los síntomas. Un descuento de 10 % sobre 105 centavos devuelve 10 y el negocio espera 11. Un cupón con tope descuenta más que su tope. Y `search_by_name` no encuentra `"  pantalón   chino "` aunque el producto existe. Encuentra la causa de cada uno en `backend/tiendita/pricing.py` y `backend/tiendita/catalog.py` antes de cambiar código.
- **Escribir**. Agrega al menos tres pruebas reales en `backend/tests/step2/test_student_pricing.py` para cubrir redondeo half-up, tope de cupón y `OutOfStockError`.

## Criterios de aceptación

- `CA-2.1` `backend/tiendita/pricing.py` calcula centavos exactos con `int`, aplica redondeo half-up, respeta `max_discount_cents` y lanza `OutOfStockError` cuando falta inventario.
- `CA-2.2` `backend/tiendita/catalog.py` carga `data/products.csv` y encuentra `"  pantalón   chino "` mediante `search_by_name`.
- `CA-2.3` `backend/tests/step2/test_student_pricing.py` contiene al menos tres tests que pasan con tu código, y cada una de las tres versiones con un bug (redondeo con `float`, cupón sin tope y venta sin revisar inventario) pone al menos uno de ellos en rojo.

## Al terminar

1. Un cupón de 50 % se aplica a un producto de 5 centavos. ¿Cuánto descuento da tu `round_half_up_percent` y cuánto daba la versión con `float` y `round()`?
2. Si el catálogo llega a un millón de productos, ¿qué esperas de la búsqueda lineal frente al diccionario según lo que mediste con `make bench`? ¿En qué caso la búsqueda lineal sigue siendo necesaria?
3. `make check STEP=2` corre tus tests contra versiones con un bug. Si una de esas versiones queda en verde, ¿qué te dice de tus tests?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

Ejecuta `make check STEP=2` para validar los tres criterios y corre `make bench` para medir las búsquedas. Si necesitas una referencia rápida, revisa [example/discount_example.py](example/discount_example.py) o abre la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. Tu versión devuelve 3 centavos (`(5 * 50 + 50) // 100`). La versión con `round()` devolvía 2, porque `round(2.5)` redondea al par más cercano.
2. El diccionario responde casi igual de rápido con mil o con un millón, y la búsqueda lineal crece en proporción al catálogo. La lineal sigue siendo necesaria cuando buscas por parte del nombre, como en `search_by_name`, porque un diccionario solo encuentra la llave exacta.
3. Que ningún test revisa la regla que esa versión rompe. Hace falta un caso concreto que la exponga, por ejemplo un monto que termine en `.5` o un cupón cuyo descuento pase el tope.
4. Respuesta personal. Debe mencionar los centavos enteros, el redondeo half-up, el tope del cupón y la normalización de texto en la búsqueda.
