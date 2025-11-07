import React from "react";
import Heading from "../atoms/Heading";

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

const LoadingSection: React.FC<LoadingSectionProps> = ({ progressStatus }) => {
  return (
    <div className="flex flex-col items-center justify-center gap-8 min-h-[400px]">
      <Heading level={2} className="text-purple-400 text-3xl">
        Ваш конспект генерируется
      </Heading>

      {/* Текущий статус */}
      <p className="text-gray-400 text-lg">
        {progressStatus ? statusLabels[progressStatus] || "Идёт обработка..." : "Ожидание..."}
      </p>

      {/* Индикатор прогресса */}
      <div className="flex items-center gap-4 mt-4">
        {["uploading", "stt", "rag", "llm", "finish"].map((step) => (
          <div key={step} className="flex flex-col items-center">
            <div
              className={`w-4 h-4 rounded-full border-2 ${
                step === progressStatus
                  ? "border-purple-400 bg-purple-400 animate-pulse"
                  : "border-gray-600"
              }`}
            />
            <span className="text-xs text-gray-400 mt-1">
              {stepLabels(step)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

function stepLabels(step: string) {
  switch (step) {
    case "uploading":
      return "Загрузка";
    case "stt":
      return "STT";
    case "rag":
      return "RAG";
    case "llm":
      return "LLM";
    case "finish":
      return "Готово";
    default:
      return "";
  }
}

export default LoadingSection;
