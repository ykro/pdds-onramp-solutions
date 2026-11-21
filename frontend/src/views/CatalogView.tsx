import { useEffect, useState } from 'react';
import { createOrder, fetchProducts, Order, Product } from '../lib/api';
import { formatQuetzales, UseCartResult } from '../hooks/useCart';

export interface CatalogViewProps {
  cart: UseCartResult;
  onOrderCreated?: (order: Order) => void;
}

export function CatalogView({ cart, onOrderCreated }: CatalogViewProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    fetchProducts()
      .then((list) => {
        if (active) {
          setProducts(list);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : 'Error al cargar productos.');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleCheckout() {
    if (cart.items.length === 0 || paying) {
      return;
    }

    setPaying(true);
    setError(null);
    setStatusMessage(null);

    try {
      const createdOrders: Order[] = [];
      for (const item of cart.items) {
        const order = await createOrder({
          sku: item.product.sku,
          quantity: item.quantity,
        });
        createdOrders.push(order);
      }
      cart.clearCart();
      const lastOrder = createdOrders[createdOrders.length - 1];
      if (createdOrders.length === 1 && lastOrder) {
        setStatusMessage(`Pedido #${lastOrder.id} creado.`);
      } else {
        setStatusMessage(
          `Pedidos ${createdOrders.map((order) => `#${order.id}`).join(', ')} creados.`,
        );
      }
      if (lastOrder) {
        onOrderCreated?.(lastOrder);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al procesar pago.');
    } finally {
      setPaying(false);
    }
  }

  return (
    <section aria-labelledby="catalog-title">
      <div className="section-header">
        <h2 id="catalog-title">Catálogo</h2>
        <div className="cart-bar" aria-live="polite">
          <span className="cart-meta" data-testid="cart-count">
            Carrito: {cart.itemCount}
          </span>
          <span className="cart-meta" data-testid="cart-total">
            {cart.formattedTotal}
          </span>
          <button
            type="button"
            className="btn btn-accent"
            disabled={cart.items.length === 0 || paying}
            onClick={handleCheckout}
          >
            {paying ? 'Pagando...' : 'Pagar'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {statusMessage && (
        <div className="alert alert-success" role="status">
          {statusMessage}
        </div>
      )}

      {loading ? (
        <p className="empty-state">Cargando...</p>
      ) : products.length === 0 ? (
        <p className="empty-state">Sin productos disponibles.</p>
      ) : (
        <ul className="product-grid">
          {products.map((product) => {
            const inCart =
              cart.items.find((item) => item.product.id === product.id)?.quantity ?? 0;
            const disabled = product.stock <= 0 || inCart >= product.stock;

            return (
              <li key={String(product.id)} className="product-card">
                <div>
                  <h3 className="product-name">{product.name}</h3>
                  <p className="product-price">{formatQuetzales(product.price_cents)}</p>
                  <p className="product-stock">
                    {product.stock > 0 ? `Stock: ${product.stock}` : 'Agotado'}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn-primary btn-full"
                  disabled={disabled}
                  onClick={() => cart.addItem(product)}
                >
                  Agregar
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {cart.items.length > 0 && (
        <section className="cart-list" aria-label="Detalle del carrito">
          <h3>Carrito</h3>
          <ul className="cart-items">
            {cart.items.map((item) => (
              <li key={String(item.product.id)} className="cart-row">
                <span>
                  {item.product.name} x {item.quantity}
                </span>
                <div className="cart-controls">
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    aria-label={`Reducir ${item.product.name}`}
                    onClick={() =>
                      cart.updateQuantity(item.product.id, item.quantity - 1)
                    }
                  >
                    -
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    aria-label={`Aumentar ${item.product.name}`}
                    disabled={item.quantity >= item.product.stock}
                    onClick={() =>
                      cart.updateQuantity(item.product.id, item.quantity + 1)
                    }
                  >
                    +
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => cart.removeItem(item.product.id)}
                  >
                    Quitar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </section>
  );
}
