// зона для перетаскивания файла
import { useState, useRef } from "react"; 
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

interface UploadBoxProps {
    onFileSelect: (file: File) => void;
}

function UploadBox({ onFileSelect }: UploadBoxProps) {
    const [isDragging, setIsDrragging] = useState(false);
    const [fileName, setFileName] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setFileName(file.name);
            onFileSelect(file);
        }
    };

    const handleClick = () => inputRef.current?.click();

    return (
        <div
            onClick={handleClick}
            className="w-4/5 h-80 border-2 border-dashed rounded-lg flex items-center justify-center cursor-pointer"
        >
            <input
                type="file"
                accept="audio/*"
                ref={inputRef}
                onChange={handleFileChange}
                className="hidden"
            />

            <Icon name="Upload" className="w-8 h-8 text-purple-400 mb-2 mr-2" />
            <Text size="sm">{fileName ?? "Перетащите или выберите файл"}</Text>
        </div>
    );
}

export default UploadBox;