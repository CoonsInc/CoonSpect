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
    className={`bg-[#16182D] text-white px-4 py-2 rounded-lg outline-none focus:ring-2 focus:ring-purple-500 ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
  />
);

export default Input;
