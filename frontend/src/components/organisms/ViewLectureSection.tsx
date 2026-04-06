import React, { useRef } from "react";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import { parseMarkdownToHtml, copyToClipboard } from "../../utils/mdUtils";

interface ViewLectureSectionProps {
  title: string;
  text: string;
  audioUrl?: string;
  onBack: () => void;
}

const ViewLectureSection: React.FC<ViewLectureSectionProps> = ({
  title,
  text,
  audioUrl,
  onBack
}) => {
  const contentRef = useRef<HTMLDivElement>(null);

  const handleCopy = () => {
    copyToClipboard(text, null);
    alert("Конспект скопирован в буфер обмена!");
  };

  const handleDownload = () => {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${title.replace(/\s+/g, '_')}.txt`; 
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="py-20 px-6 mt-16 bg-[var(--color-bg-primary)] min-h-screen">
      <div className="w-full max-w-4xl mx-auto">
        
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <Button onClick={onBack} variant="secondary" className="flex items-center gap-2 self-start">
            <Icon name="ArrowLeft" className="w-4 h-4" />
            Назад
          </Button>

          <div className="flex items-center gap-3">
            <Button onClick={handleCopy} variant="secondary" className="flex items-center gap-2">
              <Icon name="Copy" className="w-4 h-4" />
              Скопировать
            </Button>
            <Button onClick={handleDownload} variant="primary" className="flex items-center gap-2">
              <Icon name="Download" className="w-4 h-4" />
              Скачать
            </Button>
          </div>
        </div>

        <div className="mb-6 text-center sm:text-left">
            <Text size="sm" className="uppercase tracking-wider mb-2 opacity-80">
            Конспект лекции
            </Text>
            <Heading level={1} className="font-bold text-[var(--color-text-purple)] text-xl sm:text-2xl">
            {title}
            </Heading>
        </div>

        <div className="bg-[var(--color-bg-accent)] rounded-lg border border-[var(--color-border)] p-6 sm:p-10 min-h-[500px] shadow-sm overflow-x-auto">
          <div 
            ref={contentRef}
            className="prose prose-invert max-w-none text-[var(--color-text-primary)] leading-relaxed"
            dangerouslySetInnerHTML={{ __html: parseMarkdownToHtml(text) }} 
          />
        </div>

        {audioUrl && (
          <div className="mt-8 max-w-md mx-auto sm:mx-0">
            <Heading level={3} className="text-[var(--color-text-purple)] mb-3 text-base">
              🎵 Запись лекции
            </Heading>
            <audio controls src={audioUrl} className="w-full rounded-lg outline-none">
              Ваш браузер не поддерживает воспроизведение аудио.
            </audio>
          </div>
        )}

      </div>
    </section>
  );
};

export default ViewLectureSection;
