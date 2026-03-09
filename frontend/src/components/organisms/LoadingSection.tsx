
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";

interface LoadingSectionProps {
  progressStatus?: string | null;
}

const statusLabels: Record<string, string> = {
  uploading: "Загрузка аудио...",
  stt: "Преобразование речи в текст...",
  rag: "Обработка RAG (поиск информации)...",
  llm: "Генерация конспекта LLM...",
  finish: "Готово! Конспект сформирован",
};

const stepLabels: Record<string, string> = {
  uploading: "Загрузка",
  stt: "STT",
  rag: "RAG",
  llm: "LLM",
  finish: "Готово",
};

const steps = ["uploading", "stt", "rag", "llm", "finish"];

const LoadingSection: React.FC<LoadingSectionProps> = ({ progressStatus }) => {
  const currentStatus = progressStatus 
    ? statusLabels[progressStatus] || "Идёт обработка..." 
    : "Ожидание...";

  return (
    <div className="flex flex-col items-center justify-center gap-8 min-h-[400px]">
      <Heading level={2} className="text-[var(--color-text-purple)] text-3xl font-semibold">
        Ваш конспект генерируется
      </Heading>

      <Text size="lg" className="text-[var(--color-text-secondary)]">
        {currentStatus}
      </Text>

      <div className="flex items-center gap-6 mt-4">
        {steps.map((step) => (
          <div key={step} className="flex flex-col items-center gap-2">
            <div
              className={`
                w-4 h-4 rounded-full border-2 transition-all duration-300
                ${step === progressStatus 
                  ? "border-[var(--color-text-purple)] bg-[var(--color-text-purple)] animate-pulse scale-110" 
                  : "border-[var(--color-border)] bg-transparent"
                }
                ${step === "finish" && progressStatus === "finish" 
                  ? "bg-[var(--color-success)] border-[var(--color-success)]" 
                  : ""
                }
              `}
            />
            <span className="text-xs text-[var(--color-text-secondary)] font-medium">
              {stepLabels[step]}
            </span>
          </div>
        ))}
      </div>

      {progressStatus === "finish" && (
        <Text size="sm" className="text-[var(--color-success)] mt-2">
          ✓ Конспект успешно сформирован
        </Text>
      )}
    </div>
  );
};

export default LoadingSection;
