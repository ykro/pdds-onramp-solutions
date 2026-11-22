import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { FREE_SHIPPING_CENTS, formatQuetzales, useCart } from '../hooks/useCart';
import type { Product } from '../lib/api';

const CAFE: Product = {
  id: 1,
  sku: 'CAF-ANT-01',
  name: 'Café Antigua',
  category: 'Bebidas',
  price_cents: 4550,
  stock: 3,
};

const PAN: Product = {
  id: 2,
  sku: 'PAN-DUL-01',
  name: 'Pan dulce',
  category: 'Panadería',
  price_cents: 1200,
  stock: 5,
};

const AGOTADO: Product = {
  id: 3,
  sku: 'CHO-ART-01',
  name: 'Chocolate artesanal',
  category: 'Bebidas',
  price_cents: 2500,
  stock: 0,
};

describe('ca_5_2 useCart', () => {
  it('ca_5_2 inicia vacío con total Q 0.00', () => {
    const { result } = renderHook(() => useCart());

    expect(result.current.items).toEqual([]);
    expect(result.current.itemCount).toBe(0);
    expect(result.current.totalCents).toBe(0);
    expect(result.current.formattedTotal).toBe('Q 0.00');
  });

  it('ca_5_2 agrega productos, respeta stock y calcula total en centavos y quetzales', () => {
    const { result } = renderHook(() => useCart());

    act(() => {
      result.current.addItem(CAFE);
      result.current.addItem(CAFE);
      result.current.addItem(PAN);
      result.current.addItem(AGOTADO);
    });

    expect(result.current.items).toHaveLength(2);
    expect(result.current.itemCount).toBe(3);
    expect(result.current.totalCents).toBe(4550 * 2 + 1200);
    expect(result.current.formattedTotal).toBe('Q 103.00');

    // Intenta superar el stock disponible de CAFE (stock: 3)
    act(() => {
      result.current.addItem(CAFE);
      result.current.addItem(CAFE);
    });

    const cafeItem = result.current.items.find((item) => item.product.id === CAFE.id);
    expect(cafeItem?.quantity).toBe(3);
  });

  it('ca_5_2 actualiza cantidades, quita productos y vacía el carrito', () => {
    const { result } = renderHook(() => useCart());

    act(() => {
      result.current.addItem(CAFE);
      result.current.addItem(PAN);
    });

    act(() => {
      result.current.updateQuantity(PAN.id, 3);
    });
    expect(result.current.totalCents).toBe(4550 + 1200 * 3);
    expect(result.current.formattedTotal).toBe(formatQuetzales(8150));

    act(() => {
      result.current.removeItem(CAFE.id);
    });
    expect(result.current.items).toHaveLength(1);
    expect(result.current.totalCents).toBe(3600);

    act(() => {
      result.current.clearCart();
    });
    expect(result.current.items).toEqual([]);
    expect(result.current.totalCents).toBe(0);
    expect(result.current.formattedTotal).toBe('Q 0.00');
  });
});

describe('ca_5_3 envío gratis en useCart', () => {
  it('ca_5_3 calcula cuánto falta y nunca devuelve negativos', () => {
    const { result } = renderHook(() => useCart());
    expect(result.current.freeShippingRemainingCents).toBe(FREE_SHIPPING_CENTS);

    act(() => {
      result.current.addItem({ ...PAN, stock: 50 });
    });
    expect(result.current.freeShippingRemainingCents).toBe(FREE_SHIPPING_CENTS - 1200);

    act(() => {
      result.current.updateQuantity(2, 30);
    });
    expect(result.current.freeShippingRemainingCents).toBe(0);
  });
});
