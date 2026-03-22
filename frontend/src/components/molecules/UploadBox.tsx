import { useState, useRef, useEffect } from "react";
import { useTextStore } from "../../stores";

import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

interface UploadBoxProps {
    onFileSelect: (file: File) => void;
}

function UploadBox({ onFileSelect }: UploadBoxProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [fileName, setFileName] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const { audioFile, setAudioFile, isSaving } = useTextStore();

    useEffect(() => {
        setFileName(audioFile?.name || null);
    }, [audioFile]);

    const handleFile = async (file: File) => {
        if (file && file.type.startsWith('audio/')) {
            const maxSize = 50 * 1024 * 1024;
        
            if (file.size > maxSize) {
                const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                alert(`Файл слишком большой: ${fileSizeMB} МБ. Максимальный размер: 50 МБ.`);
                return;
            }

            setFileName(file.name);
            setAudioFile(file);
            onFileSelect(file);
        } else {
            alert("Пожалуйста, выберите аудио файл.");
        }
    };

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!e.currentTarget.contains(e.relatedTarget as Node)) {
            setIsDragging(false);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files?.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
    };

    const handleClick = () => !isSaving && inputRef.current?.click();

    return (
        <div
            onClick={handleClick}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className={`
                w-4/5 h-80 border-2 border-dashed rounded-xl 
                flex flex-col items-center justify-center 
                cursor-pointer transition-all duration-300
                ${isSaving ? 'opacity-50 cursor-wait' : ''}
                ${isDragging 
                  ? 'border-[var(--color-text-purple)] bg-[var(--color-text-purple)]/10 scale-105 shadow-lg' 
                  : 'border-[var(--color-border)] hover:border-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)]/5'
                }
                ${fileName && !isSaving ? 'border-[var(--color-text-purple)] bg-[var(--color-text-purple)]/5' : ''}
            `}
        >
            <input
                type="file"
                accept="audio/*"
                ref={inputRef}
                onChange={handleFileChange}
                className="hidden"
                disabled={isSaving}
            />

            <div className="text-center p-8">
        {isSaving ? (
          <>
            <Icon name="Loader2" className="w-16 h-16 text-[var(--color-text-purple)] mb-4 mx-auto animate-spin" />
            <Text size="lg" className="text-[var(--color-text-purple)] font-semibold mb-2">
              Сохраняем на диск...
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)]">
              Файл: {fileName}
            </Text>
          </>
        ) : fileName ? (
          <>
            <Icon name="Check" className="w-16 h-16 text-[var(--color-text-purple)] mb-4 mx-auto" />
            <Text size="lg" className="text-[var(--color-text-purple)] font-semibold mb-2">
              Файл готов
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)] break-all mb-2">
              {fileName}
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)]">
              Нажмите для выбора другого файла
            </Text>
          </>
        ) : (
          <>
            <Icon
              name={isDragging ? "Download" : "Upload"}
              className={`
                w-16 h-16 mb-4 mx-auto transition-all
                ${isDragging 
                  ? 'text-[var(--color-text-purple)] scale-110' 
                  : 'text-[var(--color-text-purple)]'
                }
              `}
            />
            <Text size="lg" className="text-[var(--color-text-primary)] font-semibold mb-2">
              {isDragging ? "Отпустите файл" : "Перетащите аудиофайл"}
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)] mb-2">
              или нажмите для выбора
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)]">
              Поддерживаемые форматы: MP3, WAV, M4A и другие аудиофайлы
            </Text>
          </>
        )}
      </div>
    </div>
  );
};

export default UploadBox;