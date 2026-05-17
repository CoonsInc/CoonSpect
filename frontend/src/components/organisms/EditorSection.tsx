// components/organisms/EditorSection.tsx
import React, { useState, useEffect, useRef} from "react";
import { useNavigate } from 'react-router-dom';
import { useTextStore } from "../../stores";
import EditorToolbar from "../molecules/EditorToolbar";
import AudioSearchPanel from "./AudioSearchPanel";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";
import { copyToClipboard, applyFormat } from "../../utils/mdUtils";
import MarkdownViewer from "../../utils/MarkdownViewer";

import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

(pdfMake as any).addVirtualFileSystem(pdfFonts);


interface EditorSectionProps {
  initialText: string;
  onSave: (newText: string, title: string) => void;
  onBack?: () => void;
}

type DownloadFormat = "txt" | "md" | "docx" | "pdf";

const EditorSection: React.FC<EditorSectionProps> = ({ 
  initialText,
  onSave,
  onBack
}) => {
  const { processedText, setProcessedText, setLectureTitle, deleteCurrentLecture, lectureTitle: storeTitle, audioUrl, audioFile, isSaving, activeLectureId } = useTextStore();
  
  const [text, setText] = useState(processedText || initialText);
  const [localTitle, setLocalTitle] = useState(storeTitle);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const navigate = useNavigate();
  const [isDeleting, setIsDeleting] = useState(false); 

  const audioRef = useRef<HTMLAudioElement>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);


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

  const convertMarkdownToHtml = (markdown: string): string => {
    let html = markdown;
    
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    html = html.replace(/^---$/gm, '<hr>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    html = html.replace(/^(?!<[hulb]|<\/?[hulb])(.+)$/gm, '<p>$1</p>');
    
    return html;
  };

  const handleDownloadLocally = (format: DownloadFormat) => {
    if (!localTitle.trim()) {
      alert("Пожалуйста, введите название лекции перед скачиванием.");
      return;
    }

    const safeTitle = localTitle.replace(/\s+/g, '_');
    let content = "";
    let fileName = "";
    let mimeType = "";

    switch (format) {
      case "txt":
        content = text;
        fileName = `${safeTitle}.txt`;
        mimeType = "text/plain;charset=utf-8";
        break;

      case "md":
        content = text;
        fileName = `${safeTitle}.md`;
        mimeType = "text/markdown;charset=utf-8";
        break;

      case "docx": {
        const docxHtml = convertMarkdownToHtml(text);
        content = `
  <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
  <head><meta charset="UTF-8"><title>${localTitle}</title></head>
  <body><h1>${localTitle}</h1>${docxHtml}</body></html>`;
        fileName = `${safeTitle}.doc`;
        mimeType = "application/msword";
        break;
      }

      case "pdf": {
  const lines = text.split('\n');
  const content: any[] = [];
  
  lines.forEach((line) => {
    if (line.trim() === '') {
      content.push({ text: '', margin: [0, 5] });
    } else if (line.startsWith('# ')) {
      content.push({ text: line.substring(2), bold: true, fontSize: 16, margin: [0, 10, 0, 5] });
    } else if (line.startsWith('## ')) {
      content.push({ text: line.substring(3), bold: true, fontSize: 14, margin: [0, 8, 0, 4] });
    } else if (line.startsWith('### ')) {
      content.push({ text: line.substring(4), bold: true, fontSize: 12, margin: [0, 6, 0, 3] });
    } else {
      content.push({ text: line, fontSize: 11, margin: [0, 2] });
    }
  });

  const docDefinition = {
    content: [
      { text: localTitle, fontSize: 20, bold: true, margin: [0, 0, 0, 15], alignment: 'center' },
      ...content
    ]
  };

  pdfMake.createPdf(docDefinition).download(`${safeTitle}.pdf`);
  return;
}
      default:
        content = text;
        fileName = `${safeTitle}.txt`;
        mimeType = "text/plain;charset=utf-8";
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleFormat = (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link' | 'divider') => {
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

  const handleDelete = async () => {
    if (!activeLectureId) {
      alert("Нет активной лекции для удаления");
      return;
    }

    const confirmed = window.confirm(
      "Вы уверены, что хотите удалить эту лекцию? Это действие нельзя отменить."
    );
      
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteCurrentLecture();
      navigate('/lectures');
    } catch (error) {
      console.error('Ошибка при удалении лекции:', error);
      alert('Не удалось удалить лекцию. Пожалуйста, попробуйте снова.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleJumpToTime = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play(); 
    }
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
    
    return (
      <div className="h-full pr-2">
        <MarkdownViewer content={text} />
      </div>
    );
  };

  return (
    <section className="min-h-screen py-20 px-8 bg-[var(--color-bg-primary)] relative overflow-hidden">
      <div className="w-full max-w-5xl mx-auto">
        <div className="flex flex-row items-end gap-6 sm:gap-10 mb-54 min-h-[44px]">
          {onBack && (
            <Button onClick={onBack} variant="secondary" className="flex items-center gap-2 shrink-0">
              <Icon name="ArrowLeft" className="w-4 h-4" />
              <span className="hidden xs:inline">Назад</span>
            </Button>
          )}

          <Heading 
            level={1} 
            className="font-bold text-[var(--color-text-purple)] text-xl sm:text-2xl md:text-3xl whitespace-normal text-left leading-none pb-[4px]"
          >
            Редактор конспекта
          </Heading>
        </div>

        <div className="mb-50 flex justify-end">
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

        <div className="mb-6 flex flex-col gap-2">
          <label className="text-sm font-medium text-[var(--color-text-secondary)] ml-1">
            Название лекции
          </label>
          <div className="relative flex items-center">
            <input
              type="text"
              value={localTitle}
              onChange={(e) => {
                setLocalTitle(e.target.value); 
                if (setLectureTitle) setLectureTitle(e.target.value);
              }}
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
            onDelete={handleDelete}
            isDeleting={isDeleting} 
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
                <div className="absolute inset-0 bg-black/10 flex items-center justify-center z-10">
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
          <div className="mt-8 max-w-xl mx-auto p-5 bg-[var(--color-bg-accent)] rounded-xl border border-[var(--color-border)] shadow-sm">
            <Heading level={3} className="text-[var(--color-text-purple)] mb-3 text-base flex items-center gap-2">
              🎵 {audioFile?.name || 'Аудиофайл'}
            </Heading>
            <audio ref={audioRef} controls src={audioUrl} className="w-full rounded-lg">
              Ваш браузер не поддерживает воспроизведение аудио.
            </audio>
          </div>
        )}
      </div>

      <AudioSearchPanel
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onTimeClick={handleJumpToTime}
      />
    </section>
  );
};

export default EditorSection;
