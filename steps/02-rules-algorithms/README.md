# Paso 2. Reglas de negocio y algoritmos

![Dónde estás](diagrams/where.svg)

Este paso toma unos 75 minutos.

## Antes de empezar

1. ¿Por qué calcular precios con números de punto flotante (`float`) genera errores silenciosos en una tienda en línea?
2. ¿Cómo cambia el tiempo de respuesta de una búsqueda lineal frente a un diccionario cuando el catálogo crece de 1,000 a 100,000 productos?
3. ¿Qué ventaja da escribir pruebas automatizadas sobre edge cases de negocio antes de tocar una base de datos o un servidor web?

## Por qué importa

En el posgrado revisarás reglas de negocio escritas por otros y por asistentes de IA, y decidirás qué estructura de datos aguanta el tamaño real del sistema. Si no sabes escribir un test que exponga un bug, apruebas código que cobra mal.

## Lo mínimo que necesitas saber

- **Dinero en centavos enteros.** Un `float` no puede guardar exactamente valores como `0.1`; prueba `0.1 + 0.2` en `uv run python`. Por eso Tiendita guarda los montos como `int` en centavos (`Q 12.50` es `1250`) y redondea con una regla explícita.
- **Half-up.** La regla del negocio dice que `.5` siempre sube: 10.5 centavos se cobran como 11. La función `round()` de Python no sigue esa regla (prueba `round(10.5)` y `round(11.5)`), así que no sirve para este caso.
- **Complejidad.** Buscar en una lista revisa los elementos uno por uno; con el doble de productos tarda el doble, y se escribe `O(n)`. Un diccionario encuentra la llave casi en el mismo tiempo con mil o con un millón de productos, `O(1)` en promedio. `make bench` te lo muestra con números.
- **Un test.** Una función `test_*` que prepara datos, llama al código y revisa el resultado con `assert` (preparar, actuar, comprobar). `pytest.raises(Error)` comprueba que el código lance un error esperado.

## Qué vas a hacer

- **Leer**. Corre `make bench` y lee `scripts/bench_search.py` junto con `backend/tiendita/search.py` para observar cómo escala una búsqueda lineal frente a un diccionario al pasar de 1,000 a 100,000 productos.
- **Debuguear**. Un asistente de IA escribió `pricing.py` y pasó una revisión apurada. Corre `make check STEP=2` y lee los síntomas. Un descuento de 10 % sobre 105 centavos devuelve 10 y el negocio espera 11. Un cupón con tope descuenta más que su tope. Y `search_by_name` no encuentra `"  pantalón   chino "` aunque el producto existe. Encuentra la causa de cada uno en `backend/tiendita/pricing.py` y `backend/tiendita/catalog.py` antes de cambiar código.
- **Escribir**. Agrega al menos tres pruebas reales en `backend/tests/step2/test_student_pricing.py` para cubrir redondeo half-up, tope de cupón y `OutOfStockError` (esta excepción ya existe en `pricing.py`; solo hay que probarla).

## Criterios de aceptación

- `CA-2.1` `backend/tiendita/pricing.py` calcula centavos exactos con `int`, aplica redondeo half-up, respeta `max_discount_cents` y lanza `OutOfStockError` cuando falta inventario.
- `CA-2.2` `backend/tiendita/catalog.py` carga `data/products.csv` y encuentra `"  pantalón   chino "` mediante `search_by_name`.
- `CA-2.3` `backend/tests/step2/test_student_pricing.py` contiene al menos tres tests que pasan con tu código, y cada una de las tres versiones con un bug (redondeo con `float`, cupón sin tope y venta sin revisar inventario) pone al menos uno de ellos en rojo.

## Al terminar

1. Un cupón de 50 % se aplica a un producto de 5 centavos. ¿Cuánto descuento da tu `round_half_up_percent` y cuánto daba la versión con `float` y `round()`?
2. Escribe el comentario bloqueante que le dejarías al asistente que escribió `pricing.py` por el bug del tope del cupón. Revísalo con la rúbrica de [code-review.md](../../examples/code-review.md).
3. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

Ejecuta `make check STEP=2` para validar los tres criterios y corre `make bench` para medir las búsquedas. Si necesitas una referencia rápida, revisa [example/discount_example.py](example/discount_example.py) o abre la [primera pista](hints/1.md).

## Respuestas de autoevaluación

### Antes de empezar

1. Fracciones decimales como `0.1` no tienen representación binaria exacta en `float`, por lo que al sumar o aplicar porcentajes acumulan diferencias de centavos sin lanzar errores.
2. La búsqueda lineal (`O(n)`) multiplica su tiempo unas cien veces al pasar de 1,000 a 100,000 productos; el diccionario (`O(1)` promedio) tarda casi lo mismo.
3. Las pruebas sobre funciones puras corren en milisegundos sin levantar servidores ni bases de datos, y aíslan de inmediato si el fallo vive en la regla de negocio.

### Al terminar

1. Tu versión devuelve 3 centavos (`(5 * 50 + 50) // 100`). La versión con `round()` devolvía 2, porque `round(2.5)` redondea al par más cercano.
2. Un ejemplo: «**Bloqueante, corrección.** En `backend/tiendita/pricing.py`, el descuento del cupón no se limita a `max_discount_cents`, así que un cupón de 50 % con tope de Q 10 descuenta Q 25 en un producto de Q 50. El negocio pierde dinero en cada venta grande. Propongo `min(descuento, tope)` y un test con ese caso. El redondeo en centavos enteros quedó bien resuelto». Cumple la rúbrica si dice dónde, qué tan grave es, qué impacto tiene, qué hacer y con qué tono.
3. Respuesta personal. Debe mencionar los centavos enteros, el redondeo half-up, el tope del cupón y la normalización de texto en la búsqueda.
