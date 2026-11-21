import { useState } from 'react';
import { useCart } from './hooks/useCart';
import { AuthUser, getCurrentUser, signOut } from './lib/auth';
import { CatalogView } from './views/CatalogView';
import { LoginView } from './views/LoginView';
import { OrdersView } from './views/OrdersView';

type ActiveRoute = 'catalog' | 'orders';

export default function App() {
  const [user, setUser] = useState<AuthUser | null>(() => getCurrentUser());
  const [route, setRoute] = useState<ActiveRoute>('catalog');
  const [ordersRefreshKey, setOrdersRefreshKey] = useState(0);
  const cart = useCart();

  async function handleSignOut() {
    await signOut();
    cart.clearCart();
    setUser(null);
    setRoute('catalog');
  }

  if (!user) {
    return (
      <LoginView
        onSuccess={(authenticatedUser) => {
          setUser(authenticatedUser);
          setRoute('catalog');
        }}
      />
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1 className="brand">Tiendita</h1>
        <nav className="nav" aria-label="Principal">
          <button
            type="button"
            className="nav-btn"
            aria-current={route === 'catalog' ? 'page' : undefined}
            onClick={() => setRoute('catalog')}
          >
            Catálogo
          </button>
          <button
            type="button"
            className="nav-btn"
            aria-current={route === 'orders' ? 'page' : undefined}
            onClick={() => setRoute('orders')}
          >
            Mis pedidos
          </button>
        </nav>
        <div className="user-actions">
          <span className="user-email">{user.email}</span>
          <button type="button" className="btn btn-ghost btn-sm" onClick={handleSignOut}>
            Salir
          </button>
        </div>
      </header>

      <main className="main-content">
        {route === 'catalog' ? (
          <CatalogView
            cart={cart}
            onOrderCreated={() => setOrdersRefreshKey((count) => count + 1)}
          />
        ) : (
          <OrdersView refreshKey={ordersRefreshKey} />
        )}
      </main>
    </div>
  );
}
