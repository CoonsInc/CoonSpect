// components/molecules/EditorToolbar.tsx
import React from "react";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

interface EditorToolbarProps {
  onFormat: (type: "bold" | "italic" | "list" | "heading" | "quote" | "link") => void;
  onSave?: () => void;
  onCopy?: () => void;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ onFormat, onSave, onCopy }) => {
  const formatButtons = [
    { icon: "Bold", action: "bold", title: "Жирный текст" },
    { icon: "Italic", action: "italic", title: "Курсив" },
    { icon: "List", action: "list", title: "Маркированный список" },
    { icon: "Heading", action: "heading", title: "Заголовок" },
    { icon: "Quote", action: "quote", title: "Цитата" },
    { icon: "Link", action: "link", title: "Ссылка" },
  ] as const;

  const actionButtons = [
    { icon: "Copy", action: onCopy, show: onCopy },
    { icon: "Save", action: onSave, show: onSave },
  ] as const;

  return (
    <div className="flex items-center justify-between gap-4 mb-6 p-4 bg-[var(--color-bg-secondary)] rounded-lg">
      <div className="flex items-center gap-1">
        {formatButtons.map(({ icon, action, title }) => (
          <Button
            key={action}
            variant="secondary"
            size="sm"
            onClick={() => onFormat(action)}
            title={title}
          >
            <Icon name={icon} className="w-4 h-4" />
          </Button>
        ))}
      </div>

      <div className="flex items-center gap-1">
        {actionButtons.map(
          ({ icon, action, show }) =>
            show && (
              <Button
                key={icon}
                onClick={action}
                variant="outline"
                size="sm"
                className="border-[var(--color-text-purple)] text-[var(--color-text-purple)] hover:bg-[var(--color-text-purple)] hover:text-white"
              >
                <Icon name={icon} className="w-4 h-4" />
              </Button>
            )
        )}
      </div>
    </div>
  );
};

export default EditorToolbar;
