import React from "react";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

interface EditorToolbarProps {
    onFormat: (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link') => void;
    onSave?: () => void;
    onEdit?: () => void;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ onFormat, onSave, onEdit }) => (
    
    <div className="flex items-center justify-between gap-4 mb-6 p-4 bg-[#1E1F3A] rounded-lg">

        <div className="flex items-center gap-1">
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('bold')}
                title="Жирный текст"
            >
                <Icon name="Bold" className="w-4 h-4" />
            </Button>
            
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('italic')}
                title="Курсив"
            >
                <Icon name="Italic" className="w-4 h-4" />
            </Button>
            
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('list')}
                title="Маркированный список"
            >
                <Icon name="List" className="w-4 h-4" />
            </Button>
            
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('heading')}
                title="Заголовок"
            >
                <Icon name="Heading" className="w-4 h-4" />
            </Button>
            
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('quote')}
                title="Цитата"
            >
                <Icon name="Quote" className="w-4 h-4" />
            </Button>
            
            <Button 
                variant="secondary" 
                size="sm"
                onClick={() => onFormat('link')}
                title="Ссылка"
            >
                <Icon name="Link" className="w-4 h-4" />
            </Button>
        </div>

        {onSave && (
            <Button onClick={onSave} variant="primary" size="sm">
                <Icon name="Save" className="w-4 h-4 mr-1" />
            </Button>
        )}
    </div>
);

export default EditorToolbar;