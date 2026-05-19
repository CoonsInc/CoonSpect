import React, { useRef, useState } from "react";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import AudioSearchPanel from "./AudioSearchPanel";
import { copyToClipboard } from "../../utils/mdUtils";
import MarkdownViewer from "../../utils/MarkdownViewer";

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

  const audioRef = useRef<HTMLAudioElement>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

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

  const handleJumpToTime = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play(); 
    }
  };

  return (
    <section className="py-4 px-6 mt-16 bg-[var(--color-bg-primary)] min-h-screen relative overflow-hidden">
      <div className="w-full max-w-4xl mx-auto">
        
        {/* Верхняя панель (Назад + Скопировать/Скачать) */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <Button onClick={onBack} variant="secondary" className="flex items-center gap-2 self-start">
            <Icon name="ArrowLeft" className="w-4 h-4" />
            <span className="hidden xs:inline">Назад</span>
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

        {/* Заголовок */}
        <div className="mb-2 text-center sm:text-left">
            <Text size="sm" className="uppercase tracking-wider mb-2 opacity-80">
            Конспект лекции
            </Text>
            <Heading level={1} className="font-bold text-[var(--color-text-purple)] text-xl sm:text-2xl">
            {title}
            </Heading>
        </div>

        {/* Кнопка поиска по аудио */}
        <div className="mb-4 flex justify-end">
          <Button 
            onClick={() => setIsSearchOpen(true)} 
            variant="secondary"
            disabled={!audioUrl}
            className="w-full sm:w-auto flex items-center justify-center gap-2 border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white disabled:opacity-50 transition-all"
          >
            <Icon name="Search" className="w-4 h-4" />
            Поиск по аудио
          </Button>
        </div>

        {/* Текст конспекта */}
        <div className="bg-[var(--color-bg-accent)] rounded-lg border border-[var(--color-border)] p-6 sm:p-10 h-[450px] shadow-sm overflow-y-auto">
          <div 
            ref={contentRef}
            className="prose prose-invert max-w-none text-[var(--color-text-primary)] leading-relaxed"
          >
            <MarkdownViewer content={text} />
          </div>
        </div>

        {/* Плеер */}
        {audioUrl && (
          <div className="mt-8 max-w-md mx-auto">
            <Heading level={3} className="text-[var(--color-text-purple)] mb-3 text-base">
              🎵 Запись лекции
            </Heading>
            <audio ref={audioRef} controls src={audioUrl} className="w-full rounded-lg outline-none">
              Ваш браузер не поддерживает воспроизведение аудио.
            </audio>
          </div>
        )}

      </div>

      {/* Выезжающая панель поиска */}
      <AudioSearchPanel
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onTimeClick={handleJumpToTime}
      />
    </section>
  );
};

export default ViewLectureSection;
