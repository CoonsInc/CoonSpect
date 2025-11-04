

interface TextProps {
  children: React.ReactNode;
  size?: "sm" | "base" | "lg";
  color?: string;
  className?: string;
}

const Text: React.FC<TextProps> = ({
  children,
  size = "base",
  color = "text-gray-300",
  className = "",
}) => {
  const sizes = {
    sm: "text-sm",
    base: "text-base",
    lg: "text-lg",
  };

    return (
        <p className={`${sizes[size]} ${color} ${className}`}>
            {children}
        </p>
    );
};

export default Text;
