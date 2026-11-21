import { useCallback, useMemo, useState } from 'react';
import type { Product } from '../lib/api';

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface UseCartResult {
  items: CartItem[];
  itemCount: number;
  totalCents: number;
  formattedTotal: string;
  addItem: (product: Product) => void;
  updateQuantity: (productId: Product['id'], quantity: number) => void;
  removeItem: (productId: Product['id']) => void;
  clearCart: () => void;
}

export function formatQuetzales(cents: number): string {
  return `Q ${(cents / 100).toFixed(2)}`;
}

export function useCart(initialItems: CartItem[] = []): UseCartResult {
  const [items, setItems] = useState<CartItem[]>(initialItems);

  const addItem = useCallback((product: Product) => {
    // SOLUTION_START
    if (product.stock <= 0) {
      return;
    }
    setItems((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        if (existing.quantity >= product.stock) {
          return prev;
        }
        return prev.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
    // SOLUTION_REPLACE
    // throw new Error("TODO: implementa este método en useCart.ts");
    // SOLUTION_END
  }, []);

  const updateQuantity = useCallback((productId: Product['id'], quantity: number) => {
    setItems((prev) => {
      if (quantity <= 0) {
        return prev.filter((item) => item.product.id !== productId);
      }
      return prev.map((item) => {
        if (item.product.id !== productId) {
          return item;
        }
        const bounded = Math.min(quantity, item.product.stock);
        return { ...item, quantity: bounded };
      });
    });
  }, []);

  const removeItem = useCallback((productId: Product['id']) => {
    // SOLUTION_START
    setItems((prev) => prev.filter((item) => item.product.id !== productId));
    // SOLUTION_REPLACE
    // throw new Error("TODO: implementa este método en useCart.ts");
    // SOLUTION_END
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  const itemCount = useMemo(
    () => items.reduce((sum, item) => sum + item.quantity, 0),
    [items],
  );

  const totalCents = useMemo<number>(() => {
    // SOLUTION_START
    return items.reduce(
      (sum, item) => sum + item.product.price_cents * item.quantity,
      0,
    );
    // SOLUTION_REPLACE
    // throw new Error("TODO: implementa este método en useCart.ts");
    // SOLUTION_END
  }, [items]);

  const formattedTotal = useMemo(() => formatQuetzales(totalCents), [totalCents]);

  return {
    items,
    itemCount,
    totalCents,
    formattedTotal,
    addItem,
    updateQuantity,
    removeItem,
    clearCart,
  };
}
