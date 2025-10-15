import { useState } from "react";
import UploadBox from "../molecules/UploadBox";
import Button from "../atoms/Button";
import Heading from "../atoms/Heading";

interface UploadSectionProps {
  onGenerate: (file: File) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onGenerate }) => {
  const [file, setFile] = useState<File | null>(null);

  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <Heading level={1} className="text-4xl sm:text-5xl font-bold text-purple-400">
        Преврати аудио в умный конспект
      </Heading>
      <p className="text-gray-400 text-lg max-w-md">
        Просто перетащи сюда файл или выбери его, чтобы получить понятный конспект за пару секунд.
      </p>
      <UploadBox onFileSelect={setFile} />
      <Button
        onClick={() => file && onGenerate(file)}
        variant="primary"
        className="mt-6 px-10 py-3 text-lg"
      >
        Сгенерировать конспект
      </Button>
    </div>
  );
};

export default UploadSection;
