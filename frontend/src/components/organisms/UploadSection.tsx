// components/organisms/UploadSection.tsx
import React from "react";
import { useTextStore, useAuthStore } from "../../stores";
import { useNavigate } from "react-router-dom";
import UploadBox from "../molecules/UploadBox";
import Button from "../atoms/Button";
import Heading from "../atoms/Heading";

interface UploadSectionProps {
  onGenerate: (file: File) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onGenerate }) => {
  const { audioFile } = useTextStore();
  const { user } = useAuthStore();
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
    </div>
  );
};

export default UploadSection;