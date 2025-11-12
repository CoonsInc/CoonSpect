// components/organisms/EditorSection.tsx
import React, { useState, useEffect, useRef } from "react";
import { useTextStore } from "../../stores";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";
import Text from "../atoms/Text";

interface EditorSectionProps {
    initialText: string;
    onSave: (newText: string) => void;
    onBack?: () => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ initialText, onSave, onBack }) => {
    const { processedText, setProcessedText } = useTextStore();
    const [text, setText] = useState(processedText || initialText);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        setText(processedText || initialText);
    }, [processedText, initialText]);

    const handleTextChange = (newText: string) => {
        setText(newText);
        setProcessedText(newText);
    };

    const handleSave = () => {
        setProcessedText(text);
        onSave(text);
    };

     const handleFormat = (type: 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link') => {
        if (!textareaRef.current) return;

        const textarea = textareaRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = text.substring(start, end);

        let formattedText = '';
        let newCursorPos = start;

        switch (type) {
            case 'bold':
                formattedText = `**${selectedText}**`;
                newCursorPos = start + 2 + selectedText.length + 2;
                break;
                
            case 'italic':
                formattedText = `*${selectedText}*`;
                newCursorPos = start + 1 + selectedText.length + 1;
                break;
                
            case 'list':
                if (selectedText) {
                    formattedText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
                } else {
                    formattedText = '- ';
                    newCursorPos = start + 2;
                }
                break;
                
            case 'heading':
                if (selectedText) {
                    formattedText = `## ${selectedText}`;
                    newCursorPos = start + 3 + selectedText.length;
                } else {
                    formattedText = '## ';
                    newCursorPos = start + 3;
                }
                break;
                
            case 'quote':
                if (selectedText) {
                    formattedText = `> ${selectedText}`;
                    newCursorPos = start + 2 + selectedText.length;
                } else {
                    formattedText = '> ';
                    newCursorPos = start + 2;
                }
                break;
                
            case 'link':
                if (selectedText) {
                    formattedText = `[${selectedText}](https://)`;
                    newCursorPos = start + 1 + selectedText.length + 2;
                } else {
                    formattedText = '[текст ссылки](https://)';
                    newCursorPos = start + 13;
                }
                break;
        }

        const newText = text.substring(0, start) + formattedText + text.substring(end);
        handleTextChange(newText);

        setTimeout(() => {
            textarea.focus();
            textarea.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);
    };

    const renderPreview = () => {
        if (!text.trim()) {
            return (
                <div className="flex items-center justify-center h-full text-gray-500">
                    <Text size="lg">Здесь будет предпросмотр вашего конспекта</Text>
                </div>
            );
        }

        const formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/##(.*?)(\n|$)/g, '<h3 class="text-xl font-bold mt-4 mb-4">$1</h3>')
            .replace(/- (.*?)(\n|$)/g, '<li class="ml-4">$1</li>')
            .replace(/> (.*?)(\n|$)/g, '<blockquote class="border-l-4 border-purple-500 pl-4 my-2 text-gray-300">&1</blockquote>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="&2" class="text-purple-400 hover:text-purple-300">$1</a>')
            .replace(/\n/g, '<br>');

        return (
            <div className="prose prose-invert max-w-none"
                dangerouslySetInnerHTML={{ __html: formattedText }}
            />
        );
    };

    return (
        <section className="min-h-screen py-20 px-6">
            <div className="w-full max-w-4xl mx-auto">
                
                <div className="flex items-center justify-center gap-6 mb-4">
                    <Heading level={1} className="font-bold text-purple-400">
                        Отредактируй и скачай конспект
                    </Heading>
                </div>
                
                <div className="flex items-center gap-4 mb-8">
                    {onBack && (
                        <Button
                            onClick={onBack}
                            variant="secondary"
                            className="flex items-center gap-2"
                        >
                            <Icon name="ArrowLeft" className="w-4 h-4" />
                            Назад
                        </Button>
                    )}
                </div>

                

                <EditorToolbar 
                    onFormat={handleFormat}
                    onSave={handleSave}
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="flex flex-col">
                        <Heading level={3} className="text-gray-400 mb-4">
                            Редактор
                        </Heading>
                        <div className="flex-1">
                            <textarea
                                ref={textareaRef}
                                value={text}
                                onChange={(e) => handleTextChange(e.target.value)}
                                className="w-full h-[480px] bg-[#16182D] text-white rounded-xl p-6 outline-none focus:ring-2 focus:ring-purple-500 resize-none text-lg leading-relaxed font-mono"
                                placeholder="Введите текст здесь..."
                            />
                        </div>
                    </div>

                    <div className="flex flex-col">
                        <Heading level={3} className="text-gray-400 mb-4">
                            Предпросмотр
                        </Heading>
                        <div className="flex-1 bg-[#16182D] rounded-xl p-6 h-[480px] overflow-auto">
                            {renderPreview()}
                        </div>
                    </div>    
                </div>
            </div>
        </section>
    );
};

export default EditorSection;