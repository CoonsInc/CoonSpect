
interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ 
  size = "md", 
  className = "" 
}) => {
  const sizes = {
    sm: "w-4 h-4 border-2",
    md: "w-8 h-8 border-4",
    lg: "w-12 h-12 border-4",
  };

  return (
    <div
      className={`
        ${sizes[size]} 
        border-[var(--color-text-purple)] 
        border-t-transparent 
        rounded-full 
        animate-spin
        ${className}
      `}
    />
  );
};

export default Spinner;
