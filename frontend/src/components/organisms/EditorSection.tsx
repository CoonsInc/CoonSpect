// компонент с полем для редактирования и кнопками сохранения 
import React, { useState } from "react";
import EditorToolbar from "../molecules/EditorToolbar";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";
import Button from "../atoms/Button";

interface EditorSectionProps {
    initialText: string;
    onSave: (newText: string) => void;
}

const EditorSection: React.FC<EditorSectionProps> = ({ initialText, onSave }) => {
    const [text, setText] = useState(initialText);

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

