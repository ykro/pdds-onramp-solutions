import { useCallback, useMemo, useState } from 'react';
import type { Product } from '../lib/api';

export interface CartItem {
  product: Product;
  quantity: number;
}

export function formatQuetzales(cents: number): string {
  const safe = Math.max(0, Math.round(cents));
  return `Q ${(safe / 100).toFixed(2)}`;
}

export function useCart() {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = useCallback((product: Product) => {
    setItems((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        if (existing.quantity >= product.stock) return prev;
        return prev.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }
      if (product.stock <= 0) return prev;
      return [...prev, { product, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((productId: number) => {
    setItems((prev) => prev.filter((item) => item.product.id !== productId));
  }, []);

  const updateQuantity = useCallback((productId: number, quantity: number) => {
    setItems((prev) => {
      if (quantity <= 0) {
        return prev.filter((item) => item.product.id !== productId);
      }
      return prev.map((item) => {
        if (item.product.id !== productId) return item;
        const clamped = Math.min(quantity, item.product.stock);
        return { ...item, quantity: clamped };
      });
    });
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  const totalCents = useMemo(() => {
    return items.reduce(
      (sum, item) => sum + item.product.price_cents * item.quantity,
      0,
    );
  }, [items]);

  const itemCount = useMemo(
    () => items.reduce((sum, item) => sum + item.quantity, 0),
    [items],
  );

  return {
    items,
    itemCount,
    totalCents,
    formattedTotal: formatQuetzales(totalCents),
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
  };
}

export type UseCartResult = ReturnType<typeof useCart>;
