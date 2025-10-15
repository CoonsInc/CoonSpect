import { Upload, Edit3, Loader2, Check, Download } from "lucide-react";

interface IconProps {
  name: "Upload" | "Edit3" | "Loader2" | "Check" | "Download";
  className?: string;
}

const Icon: React.FC<IconProps> = ({ name, className = "w-5 h-5" }) => {
  const icons = { Upload, Edit3, Loader2, Check, Download };
  const IconComponent = icons[name];
  return (<IconComponent className={className} />);
};

export default Icon;
