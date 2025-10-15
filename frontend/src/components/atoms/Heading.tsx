import type { ReactNode } from 'react';

interface HeadingProps {
    level?: 1 | 2 | 3;
    children: ReactNode;
    className?: string;
}

function Heading({ level = 1, children, className = "" }: HeadingProps) {
    const Tag = `h${level}` as 'h1' | 'h2' | 'h3';
    const sizes = {
        1: "text-3xl font-bold",
        2: "text-2xl font-semibold",
        3: "text-xl font-medium",
    };

    return <Tag className={`${sizes[level]} ${className}`}>
        {children}
    </Tag>;
}

export default Heading;