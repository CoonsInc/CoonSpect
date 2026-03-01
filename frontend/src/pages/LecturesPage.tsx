import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/organisms/Header";
import Footer from "../components/organisms/Footer";
import LecturesCatalog from "../components/organisms/LecturesCatalog";
import Heading from "../components/atoms/Heading";
import Text from "../components/atoms/Text";
import Button from "../components/atoms/Button";
import Icon from "../components/atoms/Icon";
import { useAppStore, useTextStore } from "../stores";

const LecturesPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAppState } = useAppStore();
  const { reset } = useTextStore();

  const handleNewNote = () => {
    reset();
    setAppState("upload");
    navigate('/');
  }

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow p-6 pt-24">
        <div className="max-w-6xl mx-auto">
          <div className="mb-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <Heading level={1} className="text-3xl font-bold mb-2">
                Библиотека лекций
              </Heading>
              <Text className="text-[var(--color-text-secondary)]">
                Здесь собраны все ваши обработанные материалы
              </Text>
          </div>

          <Button
            variant="primary"
            onClick={handleNewNote}
            className="flex items-center gap-2 self-start sm:self-auto shadow-sm hover:shadow-md transition-shadow"
          >
            <Icon name="Plus" className="w-5 h-5" />
            <span className="font-meduim">Новый конспект</span>
          </Button>
        </div>

          <LecturesCatalog />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default LecturesPage;
