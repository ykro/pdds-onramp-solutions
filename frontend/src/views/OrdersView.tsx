import { useEffect, useState } from 'react';
import { fetchMyOrders, Order } from '../lib/api';
import { formatQuetzales } from '../hooks/useCart';

export interface OrdersViewProps {
  refreshKey?: number;
}

export function OrdersView({ refreshKey = 0 }: OrdersViewProps) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    fetchMyOrders()
      .then((list) => {
        if (active) {
          setOrders(list);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : 'Error al cargar pedidos.');
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
  }, [refreshKey]);

  return (
    <section aria-labelledby="orders-title">
      <div className="section-header">
        <h2 id="orders-title">Mis pedidos</h2>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <p className="empty-state">Cargando...</p>
      ) : orders.length === 0 ? (
        <p className="empty-state">Sin pedidos.</p>
      ) : (
        <ul className="orders-list">
          {orders.map((order) => (
            <li key={String(order.id)} className="order-card">
              <span className="order-id">Pedido #{order.id}</span>
              <span className="order-status">{order.status}</span>
              <span className="order-total">
                {formatQuetzales(order.total_cents)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
