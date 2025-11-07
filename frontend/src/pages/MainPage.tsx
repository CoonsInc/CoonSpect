// import { useEffect } from "react";
import type { FC } from "react";
import { useTextStore, useAuthStore, useAppStore } from "../stores";
import Header from "../components/organisms/Header";
import UploadSection from "../components/organisms/UploadSection";
import LoadingSection from "../components/organisms/LoadingSection";
import EditorSection from "../components/organisms/EditorSection";
import HowItWorksSection from "../components/organisms/HowItWorksSection";
import ExamplesSection from "../components/organisms/ExamplesSection";
import Footer from "../components/organisms/Footer";

const MainPage: FC = () => {
  const { user } = useAuthStore();
  const { appState, setAppState } = useAppStore();
  const { processedText, generateTranscript, progressStatus } = useTextStore();

  const handleGenerate = async (file: File) => {
    if (!user) {
      alert("Сначала нужно войти в систему");
      return;
    }

    setAppState("loading");

    try {
      await generateTranscript(file);
      setAppState("editor");
    } catch (err) {
      console.error(err);
      alert("Ошибка при обработке аудио");
      setAppState("upload");
    }
  };

  const handleSave = (newText: string) => {
    console.log("💾 Сохранён текст, длина:", newText.length);
    alert("Конспект сохранён!");
  };

  return (
    <div className="bg-[#0B0C1C] text-white min-h-screen font-sans overflow-x-hidden">
      <Header />

      {appState === "upload" && (
        <section className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[#0B0C1C] to-[#16182D]">
          <div className="max-w-5xl mx-auto text-center pt-24 pb-16">
            <UploadSection onGenerate={handleGenerate} />
          </div>
        </section>
      )}

      {appState === "loading" && (
        <section className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[#0B0C1C] to-[#16182D]">
          <div className="max-w-5xl mx-auto text-center pt-24 pb-16">
            <LoadingSection progressStatus={progressStatus}/>
          </div>
        </section>
      )}

      {appState === "editor" && (
        <>
          <EditorSection
            initialText={processedText}
            onSave={handleSave}
            onBack={() => setAppState("upload")}
          />
          <HowItWorksSection />
          <ExamplesSection />
          <Footer />
        </>
      )}

      {(appState === "upload" || appState === "loading") && (
        <>
          <HowItWorksSection />
          <ExamplesSection />
          <Footer />
        </>
      )}
    </div>
  );
};

export default MainPage;
