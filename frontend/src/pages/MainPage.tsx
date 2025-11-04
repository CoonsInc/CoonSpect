import { useEffect } from "react";
import type { FC } from "react";
import { useUser } from "../contexts/UserContext";
import { mockApi } from "../api/mockClient";
import { useMainStore } from "../stores/mainStore";
import Header from "../components/organisms/Header";
import UploadSection from "../components/organisms/UploadSection";
import LoadingSection from "../components/organisms/LoadingSection";
import EditorSection from "../components/organisms/EditorSection";
import ExamplesSection from "../components/organisms/ExamplesSection";
import Footer from "../components/organisms/Footer";
import HowItWorksSection from "../components/organisms/HowItWorksSection";

const MainPage: FC = () => {
  const { user } = useUser();
  const {
    appState,
    processedText,
    setAudioFile,
    setUser,
    setProcessedText,
    setAppState
  } = useMainStore();

  // Синхронизируем пользователя из контекста с хранилищем
  useEffect(() => {
    setUser(user);
  }, [user, setUser]);

  const handleGenerate = async (file: File) => {
    if (!user) {
      alert("Сначала нужно войти в систему");
      return;
    }

    // Сохраняем файл в папку downloads перед обработкой
    const { FileSystemManager } = await import("../../utils/fileSystem");
    const { setIsSaving, setLastSavedPath } = useMainStore.getState();

    setIsSaving(true);
    try {
      const result = await FileSystemManager.saveFileToDisk(file, 'downloads');

      if (result.success) {
        setLastSavedPath(result.path!);
        console.log('✅ Файл успешно сохранен в downloads:', result.path);
      } else {
        console.warn('⚠️ Не удалось сохранить файл:', result.error);
      }
    } catch (error) {
      console.error('❌ Ошибка сохранения:', error);
    } finally {
      setIsSaving(false);
    }

    setAudioFile(file);
    setAppState("loading");
    console.log('🎬 Начинаем обработку файла:', file.name);

    try {
      const filePath = `data/${file.name}`;
      const lecture = await mockApi.uploadAudio(filePath);

      let status = lecture.status;
      let attempts = 0;
      const maxAttempts = 5;

      while (status !== 'transcribed' && status !== 'failed' && attempts < maxAttempts) {
        attempts++;
        console.log(`🔄 Проверка статуса (попытка ${attempts}/${maxAttempts})...`);

        await new Promise(resolve => setTimeout(resolve, 1500));
        const statusResponse = await mockApi.getStatus(lecture.lecture_id);
        status = statusResponse.status;

        console.log('📊 Текущий статус:', status);

        if (status === 'transcribed') {
          break;
        }
      }

      // Получаем результат
      if (status === 'transcribed') {
        console.log('✅ Обработка завершена, получаем текст...');
        const result = await mockApi.getResult(lecture.lecture_id);
        setProcessedText(result.transcription);
        setAppState("editor");
        console.log('📝 Текст получен, длина:', result.transcription.length);
      } else {
        throw new Error("Обработка аудио заняла слишком много времени");
      }

    } catch (error) {
      console.error("❌ Ошибка:", error);
      alert(error instanceof Error ? error.message : "Произошла ошибка при обработке аудио");
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

    
      <section id="hero" className="relative flex flex-col justify-center items-center min-h-screen px-6 bg-gradient-to-b from-[#0B0C1C] to-[#16182D]">
        <div className="max-w-5xl mx-auto text-center pt-24 pb-16">
          {appState === "upload" && <UploadSection onGenerate={handleGenerate} />}
          {appState === "loading" && <LoadingSection />}
          {appState === "editor" && (
            <EditorSection initialText={processedText} onSave={handleSave} />
          )}
        </div>
      </section>

      <HowItWorksSection />
      <ExamplesSection />
      <Footer />
    </div>
  );
};

export default MainPage;
