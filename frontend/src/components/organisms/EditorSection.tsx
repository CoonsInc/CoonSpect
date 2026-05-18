// components/organisms/EditorSection.tsx
import React, { useState, useEffect, useRef } from "react";
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
    
    const codeBlocks: string[] = [];
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, language, code) => {
      const placeholder = `%%CODEBLOCK_${codeBlocks.length}%%`;
      codeBlocks.push(`<pre><code class="language-${language || 'plaintext'}">${code.trim()}</code></pre>`);
      return placeholder;
    });
    
    const lines = html.split('\n');
    let result: string[] = [];
    let inTable = false;
    let tableRows: string[] = [];
    let tableSeparator = '|';
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      
      if (line.startsWith('%%CODEBLOCK_')) {
        if (inTable) {
          result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
          inTable = false;
          tableRows = [];
        }
        result.push(line);
        continue;
      }
      
      const isPipeSeparator = /^\|[\s\-\|:]+\|$/.test(line);
      const hasTabs = line.includes('\t');
      const isTabSeparator = /^[\-\s\t]+$/.test(line) && hasTabs;
      
      if (isPipeSeparator) {
        tableSeparator = '|';
        if (tableRows.length > 0) {
          const lastRow = tableRows[tableRows.length - 1];
          tableRows[tableRows.length - 1] = lastRow.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>');
        }
        continue;
      }
      
      if (isTabSeparator) {
        tableSeparator = '\t';
        if (tableRows.length > 0) {
          const lastRow = tableRows[tableRows.length - 1];
          tableRows[tableRows.length - 1] = lastRow.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>');
        }
        continue;
      }

      const isPipeLine = /^\|.+\|$/.test(line);
      const isTabLine = hasTabs && !isTabSeparator;
      
      if (isPipeLine) {
        if (!inTable || tableSeparator !== '|') {
          if (inTable) {
            result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
            tableRows = [];
          }
          inTable = true;
          tableSeparator = '|';
        }
        const cells = line.split('|').map(c => c.trim()).filter((cell, idx, arr) => {
          if ((idx === 0 || idx === arr.length - 1) && cell === '') return false;
          return true;
        });
        
        const cellHtml = cells.map(cell => `<td>${cell}</td>`).join('');
        tableRows.push(`<tr>${cellHtml}</tr>`);
        continue;
      } else if (isTabLine) {
        if (!inTable || tableSeparator !== '\t') {
          if (inTable) {
            result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
            tableRows = [];
          }
          inTable = true;
          tableSeparator = '\t';
        }
        const cells = line.split('\t').filter(cell => cell.trim() !== '');
        const cellHtml = cells.map(cell => `<td>${cell.trim()}</td>`).join('');
        tableRows.push(`<tr>${cellHtml}</tr>`);
        continue;
      } else {
        if (inTable) {
          result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
          inTable = false;
          tableRows = [];
        }
        result.push(line);
      }
    }
    
    if (inTable) {
      result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
    }
    
    html = result.join('\n');

    html = html.replace(/^###### (.+)$/gm, '<h6>$1</h6>');
    html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    html = html.replace(/^---$/gm, '<hr>');
    html = html.replace(/^\*\*\*$/gm, '<hr>');
    html = html.replace(/^___$/gm, '<hr>');

    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

    html = html.replace(/%%CODEBLOCK_(\d+)%%/g, (match, index) => {
      return codeBlocks[parseInt(index)] || match;
    });

    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    html = html.replace(/^[\*\-+] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, (match) => {
      return `<ul>${match}</ul>`;
    });

    html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    html = html.replace(/<\/blockquote>\n<blockquote>/g, '<br>');

    html = html.replace(/^(?!<[hultroblc]|<\/?[hultroblc]|<\/?table|<\/?tr|<\/?t[dh]|<\/?code|<\/?blockquote|<\/?pre)(.+)$/gm, '<p>$1</p>');

    html = html.replace(/<p>\s*<\/p>/g, '<br>');
    
    return html;
  };

  const handleDownloadLocally = (format: DownloadFormat) => {
    if (!localTitle.trim()) {
      alert("Пожалуйста, введите название лекции перед скачиванием.");
      return;
    }

    const safeTitle = localTitle.replace(/\s+/g, '_');

    switch (format) {
      case "txt": {
        const content = text;
        const fileName = `${safeTitle}.txt`;
        const mimeType = "text/plain;charset=utf-8";
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        break;
      }

      case "md": {
        const content = text;
        const fileName = `${safeTitle}.md`;
        const mimeType = "text/markdown;charset=utf-8";
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        break;
      }

      case "docx": {
        const docxHtml = convertMarkdownToHtml(text);
        const content = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
      <head>
        <meta charset="UTF-8">
        <title>${localTitle}</title>
        <style>
          body { font-family: Arial, sans-serif; }
          h1 { font-size: 18pt; color: #333; }
          h2 { font-size: 14pt; color: #555; }
          h3 { font-size: 12pt; color: #777; }
          h4 { font-size: 11pt; color: #888; }
          h5 { font-size: 10pt; color: #999; }
          h6 { font-size: 9pt; color: #aaa; }
          table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 10px 0;
          }
          th {
            background-color: #f0f0f0;
            font-weight: bold;
            border: 1px solid #ddd;
            padding: 8px;
          }
          td { 
            border: 1px solid #ddd; 
            padding: 8px; 
          }
          ul, ol { 
            margin-left: 20px; 
            margin-bottom: 10px;
          }
          li { 
            margin-bottom: 5px; 
          }
          blockquote {
            border-left: 3px solid #ccc;
            padding-left: 10px;
            color: #666;
            margin: 10px 0;
          }
          pre {
            background-color: #f4f4f4;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
          }
          code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
          }
          p { margin: 5px 0; }
          hr { border: 1px solid #ddd; }
        </style>
      </head>
      <body>
        <h1>${localTitle}</h1>
        ${docxHtml}
      </body>
      </html>`;
        const fileName = `${safeTitle}.doc`;
        const mimeType = "application/msword";
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        break;
      }

      case "pdf": {
        const docxHtml = convertMarkdownToHtml(text);
        const fullHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>${localTitle}</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              line-height: 1.6; 
              padding: 40px;
              color: #333;
              max-width: 800px;
              margin: 0 auto;
            }
            h1 { font-size: 24pt; margin: 12pt 0 6pt; }
            h2 { font-size: 18pt; margin: 10pt 0 4pt; }
            h3 { font-size: 14pt; margin: 8pt 0 4pt; }
            h4 { font-size: 12pt; margin: 8pt 0 4pt; }
            h5 { font-size: 11pt; margin: 6pt 0 4pt; }
            h6 { font-size: 10pt; margin: 6pt 0 4pt; }
            table { 
              border-collapse: collapse; 
              width: 100%; 
              margin: 10pt 0;
              page-break-inside: avoid;
            }
            th {
              background-color: #f0f0f0;
              font-weight: bold;
              text-align: left;
              border: 1px solid #ddd;
              padding: 8pt;
            }
            td { 
              border: 1px solid #ddd; 
              padding: 8pt; 
              word-wrap: break-word;
            }
            ul { 
              margin-left: 20pt; 
              margin-bottom: 10pt;
              list-style-type: disc;
            }
            ol { 
              margin-left: 20pt; 
              margin-bottom: 10pt;
              list-style-type: decimal;
            }
            li { 
              margin-bottom: 5pt; 
            }
            blockquote {
              border-left: 3pt solid #ccc;
              padding-left: 10pt;
              color: #666;
              margin: 10pt 0;
            }
            pre {
              background-color: #f4f4f4;
              padding: 12pt;
              border-radius: 4pt;
              overflow-x: auto;
              font-family: 'Courier New', monospace;
              font-size: 9pt;
              page-break-inside: avoid;
              white-space: pre-wrap;
              word-wrap: break-word;
            }
            code {
              background-color: #f4f4f4;
              padding: 2pt 4pt;
              border-radius: 3pt;
              font-family: 'Courier New', monospace;
              font-size: 9pt;
            }
            pre code {
              background-color: transparent;
              padding: 0;
            }
            p { margin: 5pt 0; }
            hr { 
              border: none;
              border-top: 1pt solid #ddd;
              margin: 15pt 0;
            }
            strong { font-weight: bold; }
            em { font-style: italic; }
            a { color: #0066cc; }
            @media print {
              body { padding: 0; }
              @page { margin: 15mm; }
            }
          </style>
        </head>
        <body>
          <h1>${localTitle}</h1>
          ${docxHtml}
        </body>
        </html>`;
        
        const iframe = document.createElement('iframe');
        iframe.style.position = 'fixed';
        iframe.style.right = '0';
        iframe.style.bottom = '0';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = '0';
        document.body.appendChild(iframe);
        
        iframe.contentWindow?.document.open();
        iframe.contentWindow?.document.write(fullHtml);
        iframe.contentWindow?.document.close();
        
        setTimeout(() => {
          iframe.contentWindow?.print();
          setTimeout(() => {
            document.body.removeChild(iframe);
          }, 1000);
        }, 500);
        
        break;
      }
    }
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
