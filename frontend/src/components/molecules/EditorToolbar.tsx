import React, { useState, useRef, useEffect } from "react";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

type FormatType = "bold" | "italic" | "list" | "heading" | "quote" | "link" | "divider";
type DownloadFormat = "txt" | "md" | "docx" | "pdf";

interface EditorToolbarProps {
  onFormat: (type: FormatType) => void;
  onDownload?: (format: DownloadFormat) => void;
  onSave?: () => void;
  onCopy?: () => void;
  onDelete?: () => void;
  isDeleting?: boolean;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ onFormat, onSave, onCopy, onDownload, onDelete, isDeleting }) => {
  const [isDownloadMenuOpen, setIsDownloadMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const formatButtons = [
    { icon: "Bold", action: "bold" as FormatType, title: "Жирный текст" },
    { icon: "Italic", action: "italic" as FormatType, title: "Курсив" },
    { icon: "List", action: "list" as FormatType, title: "Маркированный список" },
    { icon: "Heading", action: "heading" as FormatType, title: "Заголовок" },
    { icon: "Quote", action: "quote" as FormatType, title: "Цитата" },
    { icon: "Link", action: "link" as FormatType, title: "Ссылка" },
    { icon: "Minus", action: "divider" as FormatType, title: "Разделитель" },
  ];

  const downloadFormats = [
    { format: "txt" as DownloadFormat, label: "TXT", description: "Простой текст" },
    { format: "md" as DownloadFormat, label: "Markdown", description: "С разметкой" },
    { format: "docx" as DownloadFormat, label: "DOCX", description: "Microsoft Word" },
    { format: "pdf" as DownloadFormat, label: "PDF", description: "Документ PDF" },
  ];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsDownloadMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleDownloadClick = (format: DownloadFormat) => {
    if (onDownload) {
      onDownload(format);
    }
    setIsDownloadMenuOpen(false);
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6 p-3 sm:p-4 bg-[var(--color-bg-secondary)] rounded-lg">
      <div className="flex flex-wrap items-center justify-center sm:justify-start gap-1 w-full sm:w-auto">
        {formatButtons.map(({ icon, action, title }) => (
          <Button
            key={action}
            variant="secondary"
            size="sm"
            onClick={() => onFormat(action)}
            title={title}
          >
            <Icon name={icon as any} className="w-4 h-4" />
          </Button>
        ))}
      </div>

      <div className="flex flex-wrap items-center justify-center sm:justify-end gap-2 w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-none border-[var(--color-border)]">
        {onCopy && (
          <Button
            onClick={onCopy}
            variant="outline"
            size="sm"
            title="Скопировать текст"
            className="border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white"
          >
            <Icon name="Copy" className="w-4 h-4" />
          </Button>
        )}

        {onDownload && (
          <div className="relative" ref={menuRef}>
            <Button
              onClick={() => setIsDownloadMenuOpen(!isDownloadMenuOpen)}
              variant="outline"
              size="sm"
              title="Скачать конспект"
              className="border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white"
            >
              <Icon name="Download" className="w-4 h-4" />
            </Button>

            {isDownloadMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-[var(--color-bg-primary)] border border-[var(--color-border)] rounded-lg shadow-lg z-50 py-2">
                <div className="px-3 py-2 text-xs font-semibold text-[var(--color-text-secondary)] uppercase">
                  Формат файла
                </div>
                {downloadFormats.map(({ format, label, description }) => (
                  <button
                    key={format}
                    onClick={() => handleDownloadClick(format)}
                    className="w-full px-4 py-2.5 text-left hover:bg-[var(--color-bg-accent)] transition-colors flex items-center justify-between group"
                  >
                    <div>
                      <div className="text-sm font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-text-purple)]">
                        {label}
                      </div>
                      <div className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                        {description}
                      </div>
                    </div>
                    <Icon name="ArrowRight" className="w-4 h-4 text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-purple)]" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {onSave && (
          <Button
            onClick={onSave}
            variant="outline"
            size="sm"
            title="Сохранить на сервер"
            className="border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white"
          >
            <Icon name="Save" className="w-4 h-4" />
          </Button>
        )}

        {onDelete && (
          <Button
            onClick={onDelete}
            variant="outline"
            size="sm"
            title="Удалить лекцию"
            disabled={isDeleting}
            className="border-red-500 text-red-500 hover:bg-red-500 hover:text-white"
          >
            <Icon name="Trash" className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};

export default EditorToolbar;