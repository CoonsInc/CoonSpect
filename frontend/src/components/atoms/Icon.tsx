import {
  Upload, Edit3, Loader2, Check, Download, FileX, FileAudio, Trash2, ArrowLeft,
  Bold, Italic, List, Heading, Quote, Link, Save, Copy,
  LogOut, FileText, Home, Sun, Moon, Menu, User, LogIn,
  Brain, Languages, ScanEye, Network, Clock, FolderPlus, Plus, DockIcon, 
  ArrowRight, Minus, Search, X, Play, Trash, ArrowUp, ArrowDown, Globe, Lock
} from "lucide-react";

export type IconName = 
  | "Upload" | "Edit3" | "Loader2" | "Check" | "Download" | "FileX" | "FileAudio" | "Trash2" | "ArrowLeft"
  | "Bold" | "Italic" | "List" | "Heading" | "Quote" | "Link" | "Save" | "Copy"
  | "LogOut" | "FileText" | "Home" | "Sun" | "Moon" | "Menu" | "User" | "LogIn"
  | "Brain" | "Languages" | "ScanEye" | "Network" | "Clock" | "FolderPlus" | "Plus" 
  | "DockIcon" | "ArrowRight" | "Minus" | "Search" | "X" | "Play" | "Trash" | "ArrowUp" | "ArrowDown" | "Globe" | "Lock";

interface IconProps {
  name: IconName;
  className?: string;
}

const Icon: React.FC<IconProps> = ({ name, className = "w-5 h-5" }) => {
  const icons: Record<IconName, React.ElementType> = {
    Upload, Edit3, Loader2, Check, Download, FileX, FileAudio, Trash2, ArrowLeft,
    Bold, Italic, List, Heading, Quote, Link, Save, Copy,
    LogOut, FileText, Home, Sun, Moon, Menu, User, LogIn,
    Brain, Languages, ScanEye, Network, Clock, FolderPlus, Plus, DockIcon, 
    ArrowRight, Minus, Search, X, Play, Trash, ArrowUp, ArrowDown, Globe, Lock
  };

  const IconComponent = icons[name];
  return <IconComponent className={className} />;
};

export default Icon;
