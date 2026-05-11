import React from 'react';
import SortSelect from '../atoms/SortSelect';
import OrderToggle from '../atoms/OrderToggle';
import type { SortByOption, OrderOption } from '../../stores/catalogStore';

interface CatalogControlsProps {
  sortBy: SortByOption;
  order: OrderOption;
  onSortByChange: (value: SortByOption) => void;
  onOrderToggle: () => void;
  className?: string;
}

const CatalogControls: React.FC<CatalogControlsProps> = ({
  sortBy, order, onSortByChange, onOrderToggle, className = ''
}) => (
  <div className={`flex items-center gap-3 ${className}`}>
    <SortSelect value={sortBy} onChange={onSortByChange} />
    <OrderToggle order={order} onToggle={onOrderToggle} />
  </div>
);

export default CatalogControls;
