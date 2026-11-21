import { getToken } from './auth';

export interface Product {
  id: string | number;
  sku?: string;
  name: string;
  price_cents: number;
  stock: number;
}

export interface OrderItem {
  product_id: string | number;
  name?: string;
  quantity: number;
  unit_price_cents?: number;
}

export interface Order {
  id: string | number;
  status: string;
  total_cents: number;
  created_at?: string;
  items?: OrderItem[];
}

export interface CreateOrderRequest {
  items: Array<{
    product_id: string | number;
    quantity: number;
  }>;
}

export interface HealthResponse {
  status: string;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  explicitToken?: string | null,
): Promise<T> {
  const token = explicitToken !== undefined ? explicitToken : getToken();
  const headers = new Headers(options.headers);

  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Error HTTP ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string; error?: string };
      if (typeof body.detail === 'string') {
        detail = body.detail;
      } else if (typeof body.error === 'string') {
        detail = body.error;
      }
    } catch {
      // Keep generic HTTP error message when response has no JSON body.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health', { method: 'GET' }, null);
}

export async function fetchProducts(token?: string | null): Promise<Product[]> {
  const data = await request<Product[] | { items?: Product[]; products?: Product[] }>(
    '/api/products',
    { method: 'GET' },
    token,
  );
  if (Array.isArray(data)) {
    return data;
  }
  return data.items ?? data.products ?? [];
}

export async function createOrder(
  payload: CreateOrderRequest,
  token?: string | null,
): Promise<Order> {
  return request<Order>(
    '/api/orders',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    token,
  );
}

export async function fetchMyOrders(token?: string | null): Promise<Order[]> {
  const data = await request<Order[] | { items?: Order[]; orders?: Order[] }>(
    '/api/orders/mine',
    { method: 'GET' },
    token,
  );
  if (Array.isArray(data)) {
    return data;
  }
  return data.items ?? data.orders ?? [];
}
