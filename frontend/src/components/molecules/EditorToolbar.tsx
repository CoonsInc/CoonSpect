// components/molecules/EditorToolbar.tsx
import React from "react";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

interface EditorToolbarProps {
  onFormat: (type: "bold" | "italic" | "list" | "heading" | "quote" | "link" | "divider") => void;
  onDownload?: () => void;
  onSave?: () => void;
  onCopy?: () => void;
  onDelete?: () => void;
  isDeleting?: boolean;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ onFormat, onSave, onCopy, onDownload, onDelete, isDeleting }) => {
  const formatButtons = [
    { icon: "Bold", action: "bold", title: "Жирный текст" },
    { icon: "Italic", action: "italic", title: "Курсив" },
    { icon: "List", action: "list", title: "Маркированный список" },
    { icon: "Heading", action: "heading", title: "Заголовок" },
    { icon: "Quote", action: "quote", title: "Цитата" },
    { icon: "Link", action: "link", title: "Ссылка" },
    { icon: "Minus", action: "divider", title: "Разделитель" },
  ] as const;

  const actionButtons = [
    { icon: "Download", action: onDownload, show: onDownload, title: "Скачать на ПК", danger: false },
    { icon: "Copy", action: onCopy, show: onCopy, title: "Скопировать текст", danger: false },
    { icon: "Save", action: onSave, show: onSave, title: "Сохранить на сервер", danger: false },
    { icon: "Trash", action: onDelete, show: onDelete, title: "Удалить лекцию", danger: true },
  ] as const;

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
        {actionButtons.map(
          ({ icon, action, show, title, danger }) =>
            show && (
              <Button
                key={icon}
                onClick={action}
                variant="outline"
                size="sm"
                title={title}
                disabled={isDeleting}
                className={danger 
                  ? "border-red-500 text-red-500 hover:bg-red-500 hover:text-white" 
                  : "border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white"
                }
              >
                <Icon name={icon as any} className="w-4 h-4" />
              </Button>
            )
        )}
      </div>
    </div>
  );
};

export default EditorToolbar;