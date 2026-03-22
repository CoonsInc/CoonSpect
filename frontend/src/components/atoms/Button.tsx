import React from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";

  variant?: "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";

  className?: string;
  disabled?: boolean;
  title?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  size = "md",
  variant = "primary",
  onClick,
  disabled = false,
  className = "",
  type = "button",
  title,
}) => {
  const variants = {
    primary: "bg-[var(--color-text-purple)] text-white hover:opacity-90 focus:ring-[var(--color-text-purple)]",
    secondary: "bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)] hover:bg-[var(--color-border)]",
    ghost: "bg-transparent text-[var(--color-text-primary)] hover:bg-[var(--color-bg-secondary)]",
    outline: "bg-transparent border-2 hover:text-white",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        font-medium rounded-lg transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--color-bg-primary)]
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      title={title}
    >
      {children}
    </button>
  );
};

export default Button;
