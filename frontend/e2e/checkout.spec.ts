import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

const MOCK_PRODUCTS = [
  {
    id: 1,
    sku: 'CAF-ANT-01',
    name: 'Café Antigua',
    category: 'Bebidas',
    price_cents: 4550,
    stock: 4,
  },
  {
    id: 2,
    sku: 'PAN-DUL-01',
    name: 'Pan dulce',
    category: 'Panadería',
    price_cents: 1200,
    stock: 6,
  },
];

test('CA-5.4: flujo de compra completo sin violaciones críticas ni serias de accesibilidad', async ({
  page,
}) => {
  const createdOrders: Array<{
    id: number;
    user_id: string;
    status: string;
    total_cents: number;
  }> = [];

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());

    if (url.pathname === '/api/health') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok' }),
      });
      return;
    }

    if (url.pathname === '/api/products' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_PRODUCTS),
      });
      return;
    }

    if (url.pathname === '/api/orders' && request.method() === 'POST') {
      const payload = request.postDataJSON() as { sku: string; quantity: number };
      expect(payload).toEqual({ sku: 'CAF-ANT-01', quantity: 1 });
      const order = {
        id: 501,
        user_id: 'local-estudiante@galileo.edu',
        status: 'paid',
        total_cents: 4550,
      };
      createdOrders.push(order);
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(order),
      });
      return;
    }

    if (url.pathname === '/api/orders/mine' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(createdOrders),
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Not found' }),
    });
  });

  async function assertNoBlockingA11yViolations() {
    const results = await new AxeBuilder({ page }).analyze();
    const blocking = results.violations.filter(
      (violation) =>
        violation.impact === 'critical' || violation.impact === 'serious',
    );
    expect(blocking).toEqual([]);
  }

  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Tiendita' })).toBeVisible();
  await assertNoBlockingA11yViolations();

  await page.getByLabel('Correo').fill('estudiante@galileo.edu');
  await page.getByLabel('Contraseña').fill('clave-segura');
  await page.getByRole('button', { name: 'Entrar' }).click();

  await expect(page.getByText('Café Antigua')).toBeVisible();
  await assertNoBlockingA11yViolations();

  await page.getByRole('button', { name: 'Agregar' }).first().click();
  await expect(page.getByTestId('cart-count')).toHaveText('Carrito: 1');
  await expect(page.getByTestId('cart-total')).toHaveText('Q 45.50');

  await page.getByRole('button', { name: 'Pagar' }).click();
  await expect(page.getByText('Pedido #501 creado.')).toBeVisible();

  await page.getByRole('button', { name: 'Mis pedidos' }).click();
  await expect(page.getByText('Pedido #501')).toBeVisible();
  await assertNoBlockingA11yViolations();
});
