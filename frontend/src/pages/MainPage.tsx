// pages/MainPage.tsx
import type { FC } from "react";
import { useTextStore, useAuthStore, useAppStore } from "../stores";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "../components/organisms/Header";
import UploadSection from "../components/organisms/UploadSection";
import LoadingSection from "../components/organisms/LoadingSection";
import EditorSection from "../components/organisms/EditorSection";
import HowItWorksSection from "../components/organisms/HowItWorksSection";
import ExamplesSection from "../components/organisms/ExamplesSection";
import Footer from "../components/organisms/Footer";
import { useEffect } from 'react';

const MainPage: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  const { appState, setAppState } = useAppStore();
  const { processedText, generateTranscript, progressStatus, isSaving, saveLectureChanges, restoreAudio, reset} = useTextStore();

  useEffect(() => {
    if (appState === 'editor') {
      restoreAudio();
    }
  }, [appState, restoreAudio]);

  useEffect(() => {
    if (appState === 'upload' && processedText) {
      setAppState('editor');
    }
  }, [appState, processedText, setAppState]);

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (isSaving) {
        event.preventDefault();
        event.returnValue = ''; 
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isSaving]);

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
      alert("Произошла ошибка при обработке аудио. Пожалуйста, попробуйте снова.");
      setAppState("upload");
    }
  };

  const handleSave = async (newText: string, title: string) => {
    try {
      await saveLectureChanges(newText, title);
      alert("Конспект успешно сохранён!");

      reset();
      navigate("/lectures");
    } catch (e) {
      alert("Ошибка при сохранении. Попробуйте еще раз.");
    }
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
          <EditorSection
            initialText={processedText}
            onSave={handleSave}
            onBack={() => {
              reset(); 
              
              if (location.pathname.startsWith('/lec/')) {
                setAppState("upload"); 
                navigate('/lectures'); 
              } else {
                setAppState("upload");
              }
            }}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen font-sans overflow-x-hidden">
      <Header />
      {renderContent()} 
      <HowItWorksSection />
      <ExamplesSection />
      <Footer />
    </div>
  );
};

export default MainPage;
