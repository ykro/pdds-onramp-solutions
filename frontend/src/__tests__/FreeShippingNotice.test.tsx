import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { FreeShippingNotice } from '../views/FreeShippingNotice';

describe('ca_5_3 FreeShippingNotice', () => {
  it('ca_5_3 dice cuánto falta para el envío gratis', () => {
    render(<FreeShippingNotice remainingCents={5000} />);
    expect(screen.getByRole('status')).toHaveTextContent(/te faltan q 50\.00/i);
  });

  it('ca_5_3 avisa cuando el envío ya es gratis', () => {
    render(<FreeShippingNotice remainingCents={0} />);
    expect(screen.getByRole('status')).toHaveTextContent(/tienes envío gratis/i);
  });
});
