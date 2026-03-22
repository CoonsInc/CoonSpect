
import { useTextStore, useAuthStore } from "../../stores";
import { useNavigate } from "react-router-dom";
import UploadBox from "../molecules/UploadBox";
import Button from "../atoms/Button";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

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
  };

  return (
    <div className="flex flex-col items-center justify-center gap-6 max-w-3xl mx-auto">
      <Heading level={1} className="text-4xl sm:text-5xl font-bold text-[var(--color-text-purple)]">
        Преврати аудио в умный конспект
      </Heading>
      
      <Text size="lg" className="text-[var(--color-text-secondary)] text-center max-w-md">
        Просто перетащи сюда файл или выбери его, чтобы получить понятный конспект за пару секунд.
      </Text>
      
      <UploadBox onFileSelect={() => {}} />
      
      <Button
        onClick={handleGenerate}
        variant="primary"
        size="lg"
        className="mt-4 px-10 py-3 text-lg hover:ring-2 hover:ring-[var(--color-text-purple)] hover:ring-offset-2 hover:ring-offset-[var(--color-bg-primary)] transition-all"
        disabled={!audioFile}
      >
        Сгенерировать конспект
      </Button>

      {audioFile && (
        <Text size="sm" className="text-[var(--color-text-purple)] mt-2">
          ✓ Выбран файл: {audioFile.name}
        </Text>
      )}
    </div>
  );
};

export default UploadSection;
