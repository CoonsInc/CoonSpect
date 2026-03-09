import React, { useState, useEffect, useRef, useMemo } from "react";
import { useTextStore } from "../../stores";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import { copyToClipboard, applyFormat, parseMarkdownToHtml } from "../../utils/mdUtils";

interface EditorSectionProps {
    initialText: string;
    onSave: (newText: string, title: string) => void;
    onAddToFiles?: (newText: string, title: string) => void;
    onBack?: () => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ 
    initialText,
    onSave,
    onAddToFiles,
    onBack
}) => {
    const { processedText, setProcessedText, audioUrl, audioFile } = useTextStore();
    const defaultTitle = audioFile?.name 
        ? audioFile.name.replace(/\.[^/.]+$/, "") 
        : "";
        
    const [text, setText] = useState(processedText || initialText);
    const [lectureTitle, setLectureTitle] = useState(defaultTitle);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    
    const mockExistingTitles = useMemo(() => ["Введение в AI", "Основы React", "История нейросетей"], []);
    const isTitleUnique = lectureTitle.trim().length > 0 && !mockExistingTitles.includes(lectureTitle.trim());

    useEffect(() => {
        setText(processedText || initialText);
    }, [processedText, initialText]);

    const handleTextChange = (newText: string) => {
        setText(newText);
        setProcessedText(newText);
    };

    const handleSave = () => {
        setProcessedText(text);
        onSave(text, lectureTitle);
    };

    const handleCopy = () => {
        copyToClipboard(text, textareaRef.current);
    };

    const handleAddToFiles = () => {
        if (!lectureTitle.trim()) {
            alert("Пожалуйста, введите название лекции перед добавлением.");
            return;
        }
        if (!isTitleUnique) {
            alert("Лекция с таким названием уже существует. Пожалуйста, придумайте уникальное имя.");
            return;
        }
        
        setProcessedText(text);
        if (onAddToFiles) {
            onAddToFiles(text, lectureTitle);
        }
    };

    const handleFormat = (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link') => {
        if (!textareaRef.current) return;

        const textarea = textareaRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;

        // Вызываем нашу чистую функцию из утилит
        const { newText, newCursorPos } = applyFormat(text, start, end, type);

        handleTextChange(newText);

        setTimeout(() => {
            textarea.focus();
            textarea.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);
    };

    const renderPreview = () => {
        if (!text.trim()) {
            return (
                <div className="flex items-center justify-center h-full">
                    <Text size="lg" className="text-[var(--color-text-secondary)]">
                        Здесь будет предпросмотр вашего конспекта
                    </Text>
                </div>
            );
        }

        const htmlContent = parseMarkdownToHtml(text);
        return <div className="h-full" dangerouslySetInnerHTML={{ __html: htmlContent }} />;
    };

    return (
    <section className="min-h-screen py-20 px-6 bg-[var(--color-bg-primary)]">
      <div className="w-full max-w-5xl mx-auto">
        <div className="mb-6 text-center">
          <Heading level={1} className="font-bold text-[var(--color-text-purple)] text-2xl sm:text-3xl">
            Отредактируй и скачай конспект
          </Heading>
        </div>

        <div className="mb-8 flex items-center justify-between">
          {onBack && (
            <Button onClick={onBack} variant="secondary" className="flex items-center gap-2">
              <Icon name="ArrowLeft" className="w-4 h-4" />
              Назад
            </Button>
          )}
        </div>

        <div className="mb-6 flex flex-col gap-2">
            <label className="text-sm font-medium text-[var(--color-text-secondary)] ml-1">
                Название лекции
            </label>
            <div className="relative flex items-center">
                <input
                    type="text"
                    value={lectureTitle}
                    onChange={(e) => setLectureTitle(e.target.value)}
                    placeholder="Например: Введение в нейронные сети"
                    className="w-full bg-[var(--color-bg-accent)] text-[var(--color-text-primary)] px-4 py-3 rounded-lg border border-[var(--color-border)] outline-none focus:border-[var(--color-text-purple)] transition-all pr-12"
                />
                <div className={`absolute right-4 transition-all duration-300 ${isTitleUnique ? 'opacity-100 scale-110' : 'opacity-20 scale-100'}`}>
                    <Icon 
                        name="Check" 
                        className={`w-6 h-6 ${isTitleUnique ? 'text-[var(--color-success)]' : 'text-[var(--color-text-secondary)]'}`} 
                    />
                </div>
            </div>
            {lectureTitle.length > 0 && !isTitleUnique && (
                <span className="text-xs text-[var(--color-warning)] ml-1">
                    Лекция с таким названием уже существует
                </span>
            )}
        </div>

        <div className="mb-8">
            <EditorToolbar 
                onFormat={handleFormat}
                onSave={handleSave}
                onCopy={handleCopy}
                onAddToFiles={handleAddToFiles}
            />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="flex flex-col">
            <div className="h-[450px] bg-[var(--color-bg-accent)] rounded-lg border border-[var(--color-border)] overflow-hidden">
              <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => handleTextChange(e.target.value)}
                className="w-full h-full bg-transparent text-[var(--color-text-primary)] p-5 outline-none resize-none text-sm leading-relaxed font-mono"
                placeholder="Введите текст здесь..."
              />
            </div>
          </div>

          <div className="flex flex-col">
            <div className="h-[450px] bg-[var(--color-bg-accent)] rounded-lg border border-[var(--color-border)] p-5 overflow-y-auto">
              {renderPreview()}
            </div>
          </div>    
        </div>    

        {audioUrl && (
          <div className="mt-8 max-w-md mx-auto">
            <Heading level={3} className="text-[var(--color-text-purple)] mb-3 text-base">
              {audioFile?.name ? `🎵 ${audioFile.name}` : ''}
            </Heading>
            <audio controls src={audioUrl} className="w-full rounded-lg">
              Ваш браузер не поддерживает воспроизведение аудио.
            </audio>
          </div>
        )}
      </div>
    </section>
  );
};

export default EditorSection;
