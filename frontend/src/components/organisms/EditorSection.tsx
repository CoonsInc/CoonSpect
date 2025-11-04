// components/organisms/EditorSection.tsx
import React, { useState, useEffect } from "react";
import { useMainStore } from "../../stores/mainStore";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Button from "../atoms/Button";

interface EditorSectionProps {
    initialText: string;
    onSave: (newText: string) => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ initialText, onSave }) => {
    const { processedText } = useMainStore();
    const [text, setText] = useState(initialText);

    useEffect(() => {
        setText(processedText || initialText);
    }, [processedText, initialText]);



    return (
        <section className="min-h-screen flex flex-col items-center py-20 px-6">
            <Heading level={2} className="mb-6 text-purple-400">Редактировать конспект</Heading>
            <EditorToolbar onSave={() => onSave(text)} />
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full max-w-3xl h-80 bg-[#16182D] text-white rounded-xl p-4 outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            />
            <Button onClick={() => onSave(text)} className="mt-6">Сохранить изменения</Button>
        </section>
    );
};

export default EditorSection;