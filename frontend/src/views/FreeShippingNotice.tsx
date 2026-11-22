import { formatQuetzales } from '../hooks/useCart';

export interface FreeShippingNoticeProps {
  remainingCents: number;
}

export function FreeShippingNotice({ remainingCents }: FreeShippingNoticeProps) {
  return (
    <p role="status" className="cart-meta" data-testid="free-shipping">
      {remainingCents > 0
        ? `Te faltan ${formatQuetzales(remainingCents)} para envío gratis`
        : 'Tienes envío gratis'}
    </p>
  );
}
