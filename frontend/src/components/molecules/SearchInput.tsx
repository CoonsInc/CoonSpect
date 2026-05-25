import React, { useState, useEffect } from 'react';
import Icon from '../atoms/Icon';

interface SearchInputProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  className?: string; 
}

const SearchInput: React.FC<SearchInputProps> = ({ 
  value, 
  onChange, 
  placeholder = "Поиск...", 
  className = ""
}) => {
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) onChange(localValue);
    }, 300);
    return () => clearTimeout(timer);
  }, [localValue, onChange, value]);

  return (
    <div className={`relative flex items-center w-full ${className}`}>
      <div className="absolute left-3 text-[var(--color-text-secondary)]">
        <Icon name="Search" className="w-4 h-4" />
      </div>
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-[var(--color-bg-accent)] text-[var(--color-text-primary)] pl-10 pr-4 py-2 rounded-lg border border-[var(--color-border)] outline-none focus:border-[var(--color-text-purple)] transition-all"
      />
    </div>
  );
};

export default SearchInput;