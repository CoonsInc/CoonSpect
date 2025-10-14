import { useState } from "react";
import Header from "./components/organisms/Header";
import UploadSection from "./components/organisms/UploadSection";
import LoadingSection from "./components/organisms/LoadingSection";
import EditorSection from "./components/organisms/EditorSection";
import ExamplesSection from "./components/organisms/ExamplesSection";
import Footer from "./components/organisms/Footer";
import HowItWorksSection from "./components/organisms/HowItWorksSection";

type AppState = "upload" | "loading" | "editor";

function App() {
  const [state, setState] = useState<AppState>("upload");
  const [generatedText, setGeneratedText] = useState<string>("");

  const handleGenerate = (file: File) => {
    setState("loading");
    setTimeout(() => {
      setGeneratedText(
        `Конспект из аудио "${file.name}"\n\n1. Основные идеи лекции...\n2. Ключевые цитаты...\n3. Выводы и заметки.`
      );
      setState("editor");
    }, 2000);
  };

  const handleSave = (newText: string) => {
    console.log("Сохранён текст:", newText);
    alert("Конспект сохранён!");
  };

  return (
    <div className="bg-[#0B0C1C] text-white min-h-screen font-sans overflow-x-hidden">
      <Header />

      <section
        id="hero"
        className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[#0B0C1C] to-[#16182D]"
      >
        <div className="relative max-w-5xl mx-auto text-center pt-24 pb-16">
          {state === "upload" && <UploadSection onGenerate={handleGenerate} />}
          {state === "loading" && <LoadingSection />}
          {state === "editor" && (
            <EditorSection initialText={generatedText} onSave={handleSave} />
          )}
        </div>
      </section>

      <HowItWorksSection />
      <ExamplesSection />
      <Footer />
    </div>
  );
}

export default App;