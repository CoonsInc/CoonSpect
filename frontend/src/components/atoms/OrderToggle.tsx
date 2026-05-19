import React from 'react';
import Icon from './Icon';
import type { OrderOption } from '../../stores/catalogStore';

interface OrderToggleProps {
  order: OrderOption;
  onToggle: () => void;
  className?: string;
}

const OrderToggle: React.FC<OrderToggleProps> = ({ order, onToggle, className = '' }) => (
  <button
    onClick={onToggle}
    className={`
      flex items-center gap-1.5
      bg-[var(--color-bg-secondary)] 
      text-[var(--color-text-primary)] 
      border border-[var(--color-border)] 
      rounded-lg px-3 py-2 text-sm font-medium
      hover:bg-[var(--color-bg-tertiary)] transition-colors
      focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]
      ${className}
    `}
    aria-label={order === 'asc' ? 'По убыванию' : 'По возрастанию'}
    title={order === 'asc' ? 'По возрастанию' : 'По убыванию'}
  >
    <Icon name={order === 'asc' ? 'ArrowUp' : 'ArrowDown'} className="w-4 h-4" />
    <span className="hidden sm:inline">{order === 'asc' ? 'А → Я' : 'Я → А'}</span>
  </button>
);

export default OrderToggle;
