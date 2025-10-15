interface SpinnerProps {
  size?: number;
  color?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ size = 8, color = "border-purple-500" }) => (
  <div
    className={`w-${size} h-${size} border-4 ${color} border-t-transparent rounded-full animate-spin`}
  ></div>
);

export default Spinner;
