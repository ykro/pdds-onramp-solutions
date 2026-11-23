# De Python a TypeScript antes de entrar a React

Si hiciste los pasos 2 a 4, ya escribiste Python con type hints y Pydantic. TypeScript aplica la misma disciplina sobre JavaScript, verificando los tipos antes de ejecutar el código en el navegador. Esta tabla compara las piezas que usarás todos los días en Tiendita.

## 1. Modelos de datos y tipos

En Python defines `dataclass` o `BaseModel` de Pydantic. En TypeScript usas `interface` o `type`.

```python
# Python
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price_cents: int
    stock: int
```

```typescript
// TypeScript
export interface Product {
  readonly id: number;
  readonly name: string;
  readonly price_cents: number;
  readonly stock: number;
}
```

Un detalle clave en JavaScript y TypeScript es que solo existe el tipo numérico `number` (coma flotante IEEE 754 con enteros exactos hasta `2^53 - 1`). Por eso conservamos `price_cents` en centavos enteros y solo dividimos entre `100` al formatear el texto para pantalla.

## 2. Funciones y valores opcionales

```python
# Python
def format_quetzales(price_cents: int, prefix: str = "Q") -> str:
    return f"{prefix} {price_cents / 100:.2f}"
```

```typescript
// TypeScript
export function formatQuetzales(priceCents: number, prefix = "Q"): string {
  return `${prefix} ${(priceCents / 100).toFixed(2)}`;
}
```

Para valores que pueden faltar, Python usa `str | None` y TypeScript usa `string | null` o propiedades opcionales con `?`. El modo estricto (`"strict": true` en `tsconfig.json`) te obliga a comprobar si un valor es `null` antes de leer sus campos.

## 3. Listas y transformaciones inmutables

React necesita arreglos nuevos cuando actualizas el estado. En vez de mutar con `.push()`, usa `.map()`, `.filter()` y el operador spread `[...items]`.

```python
# Python
in_stock = [p.name for p in products if p.stock > 0]
```

```typescript
// TypeScript
const inStock = products
  .filter((product) => product.stock > 0)
  .map((product) => product.name);
```

## 4. Llamadas HTTP con `async` y `fetch`

A diferencia de `httpx` o `requests` cuando usas `raise_for_status()`, la función nativa `fetch` del navegador solo rechaza la promesa ante un fallo de red. Si el servidor responde `401` o `500`, `response.ok` es `false` y debes comprobarlo explícitamente.

```typescript
export async function fetchProducts(apiUrl: string): Promise<Product[]> {
  const response = await fetch(`${apiUrl}/products`);
  if (!response.ok) {
    throw new Error(`Error HTTP ${response.status} al cargar el catálogo`);
  }
  return (await response.json()) as Product[];
}
```

## 5. Uniones discriminadas para estados de interfaz

En lugar de tres booleanos independientes (`loading`, `error`, `data`) que pueden contradecirse, modela el estado de pantalla como una unión discriminada.

```typescript
type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: T };
```

Cuando compruebas `state.status === "ready"`, TypeScript sabe automáticamente que `state.data` existe y está tipado.
