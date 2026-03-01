import React from 'react';
import Header from '../components/organisms/Header';
import Footer from '../components/organisms/Footer';
import LecturesCatalog from '../components/organisms/LecturesCatalog';

const LecturesPage: React.FC = () => {
  return (
    <div className="bg-[var(--color-bg-primary)] min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow pt-24 px-6">
        <div className="max-w-6xl mx-auto">
          <LecturesCatalog />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default LecturesPage;