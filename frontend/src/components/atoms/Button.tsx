interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
}

function Button({ children, onClick, variant = "primary", className = "" }: ButtonProps) {

    const base =
        "px-6 py-2 rounded-lg font-medium transition duration-200 focus:outline-none";

    const variants = {
        primary: "bg-purple-600 hover:bg-purple-700 text-white",
        secondary: "bg-transparent border border-purple-500 text-purple-400 hover:bg-purple-500/20",
        ghost: "text-purple-400 hover:text-purple-300",
    };

    return (
        <button onClick={onClick} className={`${base} ${variants[variant]} ${className}`}>
            {children}
        </button>
    )
};

export default Button;