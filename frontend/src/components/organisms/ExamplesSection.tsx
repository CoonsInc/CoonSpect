import React, { useEffect, useState } from "react";
import Heading from "../atoms/Heading";
import Text from "../atoms/Text";
import { getExampleList } from "../../api/lecturesApi";
import type { ExampleTaskDescription } from "../../types/lecture"
import { useTextStore, useAuthStore, useAppStore } from "../../stores";

const ExamplesSection: React.FC = () => {
  const [examples, setExamples] = useState<ExampleTaskDescription[]>([]);
  const [isLoadingList, setIsLoadingList] = useState<boolean>(true);

  const { user } = useAuthStore();
  const { setAppState } = useAppStore();
  const { generateExampleTranscript } = useTextStore();

  useEffect(() => {
    getExampleList()
      .then((data) => setExamples(data))
      .catch((err) => console.error("[FRONT] Ошибка при получении списка примеров:", err))
      .finally(() => setIsLoadingList(false));
  }, []);

  const handleExampleClick = async (example: ExampleTaskDescription) => {
    if (!user) {
      alert("Сначала нужно войти в систему");
      return;
    }

    setAppState("loading");

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });

    try {
      await generateExampleTranscript(example.filename, example.title);
      setAppState("editor");
    } catch (err) {
      alert("Произошла ошибка при обработке примера лекции. Пожалуйста, попробуйте снова.");
      setAppState("upload");
    }
  };

  if (isLoadingList) {
    return (
      <section className="py-24 bg-[var(--color-bg-primary)] text-center">
        <Text size="base" className="text-[var(--color-text-secondary)]">Загрузка примеров...</Text>
      </section>
    );
  }

  if (examples.length === 0) return null;

  return (
    <section id="examples" className="py-24 bg-[var(--color-bg-primary)] text-center">
      <Heading level={2} className="text-[var(--color-text-purple)] mb-12 text-3xl font-bold">
        Примеры конспектов
      </Heading>
      
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
        {examples.map((example, index) => (
          <div
            key={index}
            onClick={() => handleExampleClick(example)}
            className="group bg-[var(--color-bg-accent)] p-8 rounded-2xl border border-[var(--color-border)] hover:border-[var(--color-text-purple)] transition-all duration-300 hover:-translate-y-1 hover:shadow-lg cursor-pointer text-left"
          >
            <Text size="lg" className="text-[var(--color-text-primary)] font-semibold mb-3">
              {example.title}
            </Text>
            <Text size="sm" className="text-[var(--color-text-secondary)] leading-relaxed">
              {example.description}
            </Text>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ExamplesSection;
