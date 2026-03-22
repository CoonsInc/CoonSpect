// components/organisms/EditorSection.tsx
import React, { useState, useEffect, useRef } from "react";
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
  onBack?: () => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ 
  initialText,
  onSave,
  onBack
}) => {
  const { processedText, setProcessedText, lectureTitle: storeTitle, audioUrl, audioFile, isSaving } = useTextStore();
  
  const [text, setText] = useState(processedText || initialText);
  const [localTitle, setLocalTitle] = useState(storeTitle);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setText(processedText || initialText);
  }, [processedText, initialText]);

  useEffect(() => {
    setLocalTitle(storeTitle);
  }, [storeTitle]);

  const handleTextChange = (newText: string) => {
    setText(newText);
    setProcessedText(newText);
  };

  const handleCopy = () => {
    copyToClipboard(text, textareaRef.current);
  };

  const handleSaveClick = () => {
    if (!localTitle.trim()) {
      alert("Пожалуйста, введите название лекции перед сохранением.");
      return;
    }
    setProcessedText(text);
    onSave(text, localTitle);
  };

  // Скачивание на ПК
  const handleDownloadLocally = () => {
    if (!localTitle.trim()) {
      alert("Пожалуйста, введите название лекции перед скачиванием.");
      return;
    }
    
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = `${localTitle.replace(/\s+/g, '_')}.txt`; 
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleFormat = (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link') => {
    if (!textareaRef.current) return;
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

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
              value={localTitle}
              onChange={(e) => setLocalTitle(e.target.value)}
              placeholder="Например: Введение в нейронные сети"
              className="w-full bg-[var(--color-bg-accent)] text-[var(--color-text-primary)] px-4 py-3 rounded-lg border border-[var(--color-border)] outline-none focus:border-[var(--color-text-purple)] transition-all"
            />
          </div>
        </div>

        <div className="mb-8">
          <EditorToolbar 
            onFormat={handleFormat}
            onSave={handleSaveClick}
            onDownload={handleDownloadLocally}
            onCopy={handleCopy}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="flex flex-col">
            <div className="h-[450px] bg-[var(--color-bg-accent)] rounded-lg border border-[var(--color-border)] overflow-hidden relative">
              <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => handleTextChange(e.target.value)}
                disabled={isSaving}
                className="w-full h-full bg-transparent text-[var(--color-text-primary)] p-5 outline-none resize-none text-sm leading-relaxed font-mono disabled:opacity-50"
                placeholder="Введите текст здесь..."
              />
              {isSaving && (
                 <div className="absolute inset-0 bg-black/10 flex items-center justify-center">
                    <span className="text-sm font-medium">Сохранение...</span>
                 </div>
              )}
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
              {audioFile?.name ? `🎵 ${audioFile.name}` : 'Аудиофайл'}
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
