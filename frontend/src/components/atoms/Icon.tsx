import { Upload, Edit3, Loader2, Check, Download, FileX, FileAudio, Trash2, ArrowLeft } from "lucide-react";

interface IconProps {
  name: "Upload" | "Edit3" | "Loader2" | "Check" | "Download" | "FileX" | "FileAudio" | "Trash2" | "ArrowLeft";
  className?: string;
}

const Icon: React.FC<IconProps> = ({ name, className = "w-5 h-5" }) => {
  const icons = { Upload, Edit3, Loader2, Check, Download, FileX, FileAudio, Trash2, ArrowLeft };
  const IconComponent = icons[name];
  return (<IconComponent className={className} />);
};

export default Icon;
