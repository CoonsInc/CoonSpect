import React, { useState, useEffect, useRef, useMemo } from "react";
import { useTextStore } from "../../stores";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

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
        if (!navigator.clipboard) {
            if (textareaRef.current) {
                textareaRef.current.select();
                document.execCommand('copy');
                textareaRef.current.setSelectionRange(
                    textareaRef.current.value.length,
                    textareaRef.current.value.length
                );
            }
        } else {
            navigator.clipboard.writeText(text).catch(() => {
                if (textareaRef.current) {
                    textareaRef.current.select();
                    document.execCommand('copy');
                    textareaRef.current.setSelectionRange(
                        textareaRef.current.value.length,
                        textareaRef.current.value.length
                    );
                }
            });
        }
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

    const getCurrentLineInfo = (position: number) => {
        const textBeforeCursor = text.substring(0, position);
        const textAfterCursor = text.substring(position);
        const linesBefore = textBeforeCursor.split('\n');
        const linesAfter = textAfterCursor.split('\n');

        const currentLineIndex = linesBefore.length - 1;
        const currentLine = linesBefore[currentLineIndex] + linesAfter[0];
        const lineStartPosition = position - linesBefore[currentLineIndex].length;
        const lineEndPosition = lineStartPosition + currentLine.length;
        return { currentLine, currentLineIndex, lineStartPosition, lineEndPosition };
    };

    const handleFormat = (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link') => {
        if (!textareaRef.current) return;

        const textarea = textareaRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = text.substring(start, end);

        let newText = '';
        let newCursorPos = start;

        switch (type) {
            case 'bold':
                const boldBefore = text.substring(start - 2, start) === '**';
                const boldAfter = text.substring(end, end + 2) === '**';
                
                if (boldBefore && boldAfter) {
                    newText = text.substring(0, start - 2) + selectedText + text.substring(end + 2);
                    newCursorPos = start - 2;
                } else {
                    newText = text.substring(0, start) + `**${selectedText}**` + text.substring(end);
                    newCursorPos = start + 2;
                }
                handleTextChange(newText);
                break;
            case 'italic':
                const italicBefore = text.substring(start - 1, start) === '*';
                const italicAfter = text.substring(end, end + 1) === '*';
                
                if (italicBefore && italicAfter) {
                    newText = text.substring(0, start - 1) + selectedText + text.substring(end + 1);
                    newCursorPos = start - 1;
                } else {
                    newText = text.substring(0, start) + `*${selectedText}*` + text.substring(end);
                    newCursorPos = start + 1;
                }
                handleTextChange(newText);
                break;
            case 'list':
            case 'heading':
            case 'quote':
                const lineInfo = getCurrentLineInfo(start);
                const prefix = type === 'list' ? '- ' : type === 'heading' ? '## ' : '> ';
                const currentLine = lineInfo.currentLine;
                
                if (currentLine.startsWith(prefix)) {
                const newLine = currentLine.substring(prefix.length);
                newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineStartPosition + newLine.length;
                } else {
                const newLine = prefix + currentLine;
                newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineStartPosition + newLine.length;
                }
                handleTextChange(newText);
                break;
                
            case 'link':
                if (selectedText) {
                const linkRegex = /^\[(.*)\]\((.*)\)$/;
                const match = selectedText.match(linkRegex);
                
                if (match) {
                    const linkText = match[1];
                    newText = text.substring(0, start) + linkText + text.substring(end);
                    newCursorPos = start + linkText.length;
                } else {
                    const formattedText = `[${selectedText}](https://)`;
                    newText = text.substring(0, start) + formattedText + text.substring(end);
                    newCursorPos = start + 1 + selectedText.length + 2;
                }
                } else {
                const formattedText = '[текст ссылки](https://)';
                newText = text.substring(0, start) + formattedText + text.substring(end);
                newCursorPos = start + 13;
                }
                handleTextChange(newText);
                break;
            }

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

        const formattedText = text
        .split('\n')
        .map(line => {
            if (line.startsWith('## ')) {
                return `<h3 class="text-xl font-bold mt-4 mb-2 text-[var(--color-text-primary)]">${line.slice(3)}</h3>`;
            }
            if (line.startsWith('> ')) {
                return `<blockquote class="border-l-4 border-[var(--color-text-purple)] pl-4 my-2 text-[var(--color-text-secondary)] italic">${line.slice(2)}</blockquote>`;
            }
            if (line.startsWith('- ')) {
                return `<li class="ml-4 text-[var(--color-text-primary)] mb-1 list-disc">${line.slice(2)}</li>`;
            }
            if (line.trim() === '') {
                return '<br>';
            }

            let processedLine = line
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[var(--color-text-primary)]">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="italic text-[var(--color-text-secondary)]">$1</em>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-[var(--color-text-purple)] hover:opacity-80 underline" target="_blank" rel="noopener noreferrer">$1</a>');
            
            return `<p class="mb-3 text-[var(--color-text-primary)] leading-relaxed">${processedLine}</p>`;
        })
        .join('');

    return <div className="h-full" dangerouslySetInnerHTML={{ __html: formattedText }} />;
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
