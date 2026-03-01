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
      console.error("Ошибка при обработке аудио:", err);
      alert("Произошла ошибка при обработке аудио. Пожалуйста, попробуйте снова.");
      setAppState("upload");
    }
  };

  const handleSave = (newText: string) => {
    console.log("💾 Конспект сохранён. Длина:", newText.length);
    alert("Конспект успешно сохранён!");
  };

  const renderContent = () => {
    switch (appState) {
      case "upload":
        return (
          <section className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[var(--color-bg-primary)] to-[var(--color-bg-secondary)]">
            <div className="w-full max-w-5xl mx-auto text-center pt-24 pb-16">
              <UploadSection onGenerate={handleGenerate} />
            </div>
          </section>
        );
      
      case "loading":
        return (
          <section className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[var(--color-bg-accent)] to-[var(--color-bg-secondary)]">
            <div className="w-full max-w-5xl mx-auto text-center pt-24 pb-16">
              <LoadingSection progressStatus={progressStatus} />
            </div>
          </section>
        );
      
      case "editor":
        return (
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
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen font-sans overflow-x-hidden">
      <Header />
      {renderContent()}
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
