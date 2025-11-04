// панель для редактирования

import React from "react";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

interface EditorToolbarProps {
    onSave?: () => void;
    onEdit?: () => void;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ onSave, onEdit}) => (
    <div className="flex gap-4 mb-4">
        <Button onClick={onEdit} variant="secondary">
            <Icon name="Edit3" className="inline-block mr-2" />
            Редактировать
        </Button>
        <Button onClick={onSave}>
            <Icon name="Upload" className="inline-block mr-2" />
            Сохранить
        </Button>
    </div>
);

export default EditorToolbar;