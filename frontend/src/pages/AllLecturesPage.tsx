import React from "react";
import Header from "../components/organisms/Header";
import Footer from "../components/organisms/Footer";
import LecturesCatalog from "../components/organisms/LecturesCatalog";
import Heading from "../components/atoms/Heading";
import Text from "../components/atoms/Text";

const AllLecturesPage: React.FC = () => {
  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow p-6 pt-24">
        <div className="max-w-6xl mx-auto">
          <div className="mb-10">
            <Heading level={1} className="text-3xl font-bold mb-2">
              Каталог лекций
            </Heading>
            <Text className="text-[var(--color-text-secondary)]">
              Публичные материалы от всех пользователей платформы
            </Text>
          </div>

          <LecturesCatalog 
            scope="all"
            emptyStateTitle="Каталог пуст"
            emptyStateText="Пока нет публичных лекций. Будьте первым!"
          />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AllLecturesPage;