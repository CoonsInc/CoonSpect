import type { ReactNode } from 'react';

interface HeadingProps {
  level?: 1 | 2 | 3 | 4;
  children: ReactNode;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

const Heading = ({ 
  level = 1, 
  children, 
  className = "",
  as 
}: HeadingProps) => {
  const Tag = as || (`h${level}` as 'h1' | 'h2' | 'h3' | 'h4');
  
  const sizes = {
    1: "text-4xl md:text-5xl font-bold",
    2: "text-3xl md:text-4xl font-semibold",
    3: "text-2xl md:text-3xl font-medium",
    4: "text-xl md:text-2xl font-medium",
  };

  return (
    <Tag className={`${sizes[level]} text-[var(--color-text-primary)] ${className}`}>
      {children}
    </Tag>
  );
};

export default Heading;
