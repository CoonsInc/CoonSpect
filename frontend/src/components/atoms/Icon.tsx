import { Upload, Edit3, Loader2 } from "lucide-react";

interface IconProps {
  name: "Upload" | "Edit3" | "Loader2";
  className?: string;
}

const Icon: React.FC<IconProps> = ({ name, className = "w-5 h-5" }) => {
  const icons = { Upload, Edit3, Loader2 };
  const IconComponent = icons[name];
  return (<IconComponent className={className} />);
};

export default Icon;
