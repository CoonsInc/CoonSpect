// components/organisms/EditorSection.tsx
import React, { useState, useEffect } from "react";
import { useTextStore } from "../../stores";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";
import Icon from "../atoms/Icon";

interface EditorSectionProps {
    initialText: string;
    onSave: (newText: string) => void;
    onBack?: () => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ initialText, onSave, onBack }) => {
    const { processedText, setProcessedText } = useTextStore();
    const [text, setText] = useState(processedText || initialText);

    useEffect(() => {
        setText(processedText || initialText);
    }, [processedText, initialText]);

    const handleTextChange = (newText: string) => {
        setText(newText);
        // Сохраняем изменения в хранилище в реальном времени
        setProcessedText(newText);
    };

    const handleSave = () => {
        // Сохраняем финальную версию
        setProcessedText(text);
        onSave(text);
    };

    return (
        <section className="min-h-screen py-20 px-6">
            <div className="w-full max-w-4xl mx-auto">
                {onBack && (
                    <Button
                        onClick={onBack}
                        variant="secondary"
                        className="flex items-center gap-2 mb-6"
                    >
                        <Icon name="ArrowLeft" className="w-4 h-4" />
                        Назад
                    </Button>
                )}
                <Heading level={2} className="mb-8 text-purple-400 text-center">Редактировать конспект</Heading>
                {/* <EditorToolbar onSave={handleSave} /> */}
                <div className="mt-8">
                    <textarea
                        value={text}
                        onChange={(e) => handleTextChange(e.target.value)}
                        className="w-full h-[480px] bg-[#16182D] text-white rounded-xl p-6 outline-none focus:ring-2 focus:ring-purple-500 resize-none text-lg leading-relaxed"
                        placeholder="Здесь будет ваш конспект..."
                    />
                </div>
                
                <div className="flex justify-end mt-8">
                    <EditorToolbar onSave={handleSave} />
                    {/* <Button onClick={handleSave} className="px-8 py-3 text-lg">
                        Сохранить изменения
                    </Button> */}
                </div>
            </div>
        </section>
    );
};

export default EditorSection;