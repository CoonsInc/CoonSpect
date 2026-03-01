

interface TextProps {
  children: React.ReactNode;
  size?: "sm" | "base" | "lg";
  className?: string;
  as?: "p" | "span" | "div";
}

const Text: React.FC<TextProps> = ({
  children,
  size = "base",
  className = "",
  as: Component = "p",
}) => {
  const sizes = {
    sm: "text-sm",
    base: "text-base",
    lg: "text-lg",
  };

    return (
      <Component className={`${sizes[size]} text-[var(--color-text-secondary)] ${className}`}>
        {children}
      </Component>
    );
};

export default Text;
