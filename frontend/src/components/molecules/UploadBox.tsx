// components/molecules/UploadBox.tsx
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
        if (audioFile) {
            setFileName(audioFile.name);
        } else {
            setFileName(null);
        }
    }, [audioFile]);

    const handleFile = async (file: File) => {
        if (file && file.type.startsWith('audio/')) {
            setFileName(file.name);
            setAudioFile(file);
            onFileSelect(file);
        } else {
            alert("Пожалуйста, выберите аудио файл."); //или видео (ну пока без выебонов)
        }
    };

    const handleDragEnter = (e: React.DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (!e.currentTarget.contains(e.relatedTarget as Node)) {
            setIsDragging(false);
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDrop = (e: React.DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleClick = () => inputRef.current?.click();

    return (
        <div
            onClick={handleClick}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className={`
                w-4/5 h-80 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300
                ${isDragging
                    ? 'border-purple-400 bg-purple-500/10 scale-105 shadow-lg'
                    : 'border-purple-600/50 hover:border-purple-400 hover:bg-purple-500/5'
                }
                ${fileName ? 'border-green-500 bg-green-500/5' : ''}
                ${isSaving ? 'opacity-50 cursor-wait' : ''}
            `}
        >
            <input
                type="file"
                accept="audio/*"
                ref={inputRef}
                onChange={handleFileChange}
                className="hidden"
            />

            <div className="text-center p-8">
                {isSaving ? (
                    <>
                        <Icon name="Loader2" className="w-16 h-16 text-blue-400 mb-4 mx-auto animate-spin" />
                        <Text size="lg" className="text-blue-400 font-semibold mb-2">
                            Сохраняем на диск...
                        </Text>
                        <Text size="sm" className="text-gray-400">
                            Файл: {fileName}
                        </Text>
                    </>
                ) : fileName ? (
                    <>
                        <Icon name="Check" className="w-16 h-16 text-green-400 mb-4 mx-auto" />
                        <Text size="lg" className="text-green-400 font-semibold mb-2">
                            Файл готов
                        </Text>
                        <Text size="sm" className="text-gray-300 break-all mb-2">
                            {fileName}
                        </Text>
                        <Text size="sm" className="text-gray-500">
                            Нажмите для выбора другого файла
                        </Text>
                    </>
                ) : (
                     <>
                        <Icon
                            name={isDragging ? "Download" : "Upload"}
                            className={`w-16 h-16 mb-4 mx-auto transition-transform ${
                                isDragging ? 'text-purple-400 scale-110' : 'text-purple-400'
                            }`}
                        />
                        <Text size="lg" className="text-white font-semibold mb-2">
                            {isDragging ? "Отпустите файл" : "Перетащите аудиофайл"}
                        </Text>
                        <Text size="sm" className="text-gray-400 mb-2">
                            или нажмите для выбора
                        </Text>
                        <Text size="sm" className="text-gray-500">
                            Поддерживаемые форматы: MP3, WAV, M4A и другие аудиофайлы
                        </Text>
                    </>
                )}
            </div>
        </div>
    );
}

export default UploadBox;
