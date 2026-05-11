import React from 'react';
import type { SortByOption } from '../../stores/catalogStore';

interface SortSelectProps {
  value: SortByOption;
  onChange: (value: SortByOption) => void;
  className?: string;
}

const OPTIONS: Array<{ label: string; value: SortByOption }> = [
  { label: 'По дате', value: 'created_at' },
  { label: 'По названию', value: 'name' },
  { label: 'По обновлению', value: 'updated_at' },
];

const SortSelect: React.FC<SortSelectProps> = ({ value, onChange, className = '' }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value as SortByOption)}
    className={`
      bg-[var(--color-bg-secondary)] 
      text-[var(--color-text-primary)] 
      border border-[var(--color-border)] 
      rounded-lg px-3 py-2 text-sm font-medium
      focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]
      cursor-pointer ${className}
    `}
    aria-label="Сортировка"
  >
    {OPTIONS.map((opt) => (
      <option key={opt.value} value={opt.value}>{opt.label}</option>
    ))}
  </select>
);

export default SortSelect;
