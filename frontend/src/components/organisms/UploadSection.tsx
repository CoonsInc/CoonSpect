// components/organisms/UploadSection.tsx
import React from "react";
import { useMainStore } from "../../stores/mainStore";
import { useUser } from "../../contexts/UserContext";
import { useNavigate } from "react-router-dom";
import UploadBox from "../molecules/UploadBox";
import Button from "../atoms/Button";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

interface UploadSectionProps {
  onGenerate: (file: File) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onGenerate }) => {
  const { audioFile, lastSavedPath } = useMainStore();
  const { user } = useUser();
  const navigate = useNavigate();



  const handleGenerate = () => {
    if (!audioFile) {
      alert('Пожалуйста, загрузите аудиофайл перед генерацией конспекта.');
      return;
    }
    if (!user) {
      navigate('/login');
      return;
    }
    onGenerate(audioFile);

    console.log('Передаем файл на обработку:', {
      name: audioFile.name,
      size: audioFile.size,
      type: audioFile.type
    });
  };

  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <Heading level={1} className="text-4xl sm:text-5xl font-bold text-purple-400">
        Преврати аудио в умный конспект
      </Heading>
      <p className="text-gray-400 text-lg max-w-md">
        Просто перетащи сюда файл или выбери его, чтобы получить понятный конспект за пару секунд.
      </p>
      <UploadBox onFileSelect={() => {}} />
      <Button
        onClick={handleGenerate}
        variant="primary"
        className="mt-6 px-10 py-3 text-lg"
        disabled={!audioFile}
      >
        Сгенерировать конспект
      </Button>
      {audioFile && (
        <div className="mt-4 p-4 bg-gray-800 rounded-lg text-sm">
          <Text size="sm" className="text-green-400 font-mono">
            {lastSavedPath ? '✅ Файл сохранен на диск' : '📱 Файл в памяти приложения'}
          </Text>
          <Text size="sm" className="text-gray-400">
            {audioFile.name} ({(audioFile.size / 1024 / 1024).toFixed(2)} MB)
          </Text>
          {lastSavedPath && (
            <Text size="sm" className="text-green-400">
              📍 {lastSavedPath}
            </Text>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadSection;