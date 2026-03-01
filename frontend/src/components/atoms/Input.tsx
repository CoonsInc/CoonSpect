
interface InputProps {
  type?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const Input: React.FC<InputProps> = ({
  type = "text",
  value,
  onChange,
  placeholder,
  disabled = false,
  className = "",
}) => (
  <input
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    disabled={disabled}
    className={`
      bg-[var(--color-bg-secondary)] 
      text-[var(--color-text-primary)] 
      placeholder:text-[var(--color-text-secondary)] 
      px-4 py-2 rounded-lg 
      outline-none focus:ring-2 focus:ring-[var(--color-text-purple)] 
      disabled:opacity-50 disabled:cursor-not-allowed 
      transition-all duration-200
      ${className}
    `}
  />
);

export default Input;
