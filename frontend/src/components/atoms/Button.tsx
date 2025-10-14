import { Children } from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
}

function Button ({ children, onClick, variant = "primary", className = ""}: ButtonProps
) {
    
    // стандартный вариант кнопки
    const base = 
        "px-6 py-2 rounded-lg font-medium translation duration-200 focus:outline-none";
        // горизонтальный, вертикальный отступы, скругление краев
        // вес шрифта, плавные переходы, убир. станд. рамку браузера при фокусе?
    
    // кастомные варианты
    const variants = {
        // фоновая пурпурная кнопка с белым текстом и эффектом при наведении
        primary: "bg-purple-600 hover:bg-purple-700 text-white",
        // прозрачная кнопка с рамкой
        secondary: "bg-transparent border border-purple-500 text-purple-400 hover:bg-purple500/20",
        // просто текстовый вариант
        ghost: "text-purple-400 hover:text-purple-300",
    };
    
    // Возвращаем JSX: кнопка с обработчиком клика и собранными классами
    return (
        <button onClick={onClick} className={`${base} ${variants[variant]} ${className}`}>
            {children}
        </button>
    )
};

export default Button;