import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../App';
import { signOut } from '../lib/auth';

const MOCK_PRODUCTS = [
  { id: 1, name: 'Café Antigua', price_cents: 4550, stock: 4 },
  { id: 2, name: 'Atol de elote', price_cents: 1500, stock: 0 },
];

const MOCK_ORDERS = [
  { id: 101, status: 'paid', total_cents: 4550 },
];

function createJsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('ca_5_2 App vistas y flujo principal', () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(async () => {
    await signOut();
    fetchMock.mockReset();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(async () => {
    await signOut();
    vi.unstubAllGlobals();
  });

  it('ca_5_2 protege rutas mostrando LoginView cuando no hay sesión', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Tiendita' })).toBeInTheDocument();
    expect(screen.getByLabelText('Correo')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Mis pedidos' })).not.toBeInTheDocument();
  });

  it('ca_5_2 permite iniciar sesión, cargar catálogo, agregar al carrito y pagar', async () => {
    const user = userEvent.setup();

    fetchMock.mockImplementation(async (input, init) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.endsWith('/api/products')) {
        return createJsonResponse(MOCK_PRODUCTS);
      }
      if (url.endsWith('/api/orders') && init?.method === 'POST') {
        return createJsonResponse({ id: 101, status: 'paid', total_cents: 4550 }, 201);
      }
      if (url.endsWith('/api/orders/mine')) {
        return createJsonResponse(MOCK_ORDERS);
      }
      return createJsonResponse({ status: 'ok' });
    });

    render(<App />);

    await user.type(screen.getByLabelText('Correo'), 'ana@galileo.edu');
    await user.type(screen.getByLabelText('Contraseña'), 'secreto123');
    await user.click(screen.getByRole('button', { name: 'Entrar' }));

    expect(await screen.findByText('Café Antigua')).toBeInTheDocument();
    expect(screen.getByText('Q 45.50')).toBeInTheDocument();
    expect(screen.getByText('Stock: 4')).toBeInTheDocument();
    expect(screen.getByText('Agotado')).toBeInTheDocument();

    const addButtons = screen.getAllByRole('button', { name: 'Agregar' });
    expect(addButtons[0]).toBeEnabled();
    expect(addButtons[1]).toBeDisabled();

    await user.click(addButtons[0]);
    expect(screen.getByTestId('cart-count')).toHaveTextContent('Carrito: 1');
    expect(screen.getByTestId('cart-total')).toHaveTextContent('Q 45.50');

    await user.click(screen.getByRole('button', { name: 'Pagar' }));

    expect(await screen.findByText('Pedido #101 creado.')).toBeInTheDocument();
    expect(screen.getByTestId('cart-count')).toHaveTextContent('Carrito: 0');

    // Verifica que POST /api/orders envió Authorization Bearer
    const orderCall = fetchMock.mock.calls.find(
      ([url, init]) => String(url).endsWith('/api/orders') && init?.method === 'POST',
    );
    expect(orderCall).toBeDefined();
    const headers = new Headers(orderCall?.[1]?.headers);
    expect(headers.get('Authorization')).toBe('Bearer dev-token:ana@galileo.edu');
  });

  it('ca_5_2 navega a OrdersView y cierra sesión correctamente', async () => {
    const user = userEvent.setup();

    fetchMock.mockImplementation(async (input) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.endsWith('/api/products')) {
        return createJsonResponse(MOCK_PRODUCTS);
      }
      if (url.endsWith('/api/orders/mine')) {
        return createJsonResponse(MOCK_ORDERS);
      }
      return createJsonResponse({ status: 'ok' });
    });

    render(<App />);

    await user.type(screen.getByLabelText('Correo'), 'ana@galileo.edu');
    await user.type(screen.getByLabelText('Contraseña'), 'secreto123');
    await user.click(screen.getByRole('button', { name: 'Entrar' }));

    await screen.findByText('Café Antigua');

    await user.click(screen.getByRole('button', { name: 'Mis pedidos' }));
    expect(await screen.findByText('Pedido #101')).toBeInTheDocument();
    expect(screen.getByText('paid')).toBeInTheDocument();
    expect(screen.getByText('Q 45.50')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Salir' }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument();
    });
  });
});
