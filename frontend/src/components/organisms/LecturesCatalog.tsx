import React from 'react';
import LectureCard, { type Lecture } from '../molecules/LectureCard';

const demoLectures: Lecture[] = [
  {
    id: "1",
    title: "Введение в нейронные сети",
    description: "Основные концепции искусственных нейронных сетей, история развития и базовые архитектуры.",
    duration: 45,
    level: "beginner",
    icon: "Brain"
  },
  {
    id: "2",
    title: "Обработка естественного языка",
    description: "Методы и подходы к анализу текстов, трансформеры и современные NLP модели.",
    duration: 60,
    level: "intermediate",
    icon: "Languages"
  },
  {
    id: "3",
    title: "Компьютерное зрение",
    description: "Распознавание изображений, сверточные нейросети и практические применения.",
    duration: 55,
    level: "intermediate",
    icon: "ScanEye"
  },
  {
    id: "4",
    title: "Рекуррентные нейросети",
    description: "Архитектуры для последовательных данных, LSTM, GRU и их применение.",
    duration: 50,
    level: "advanced",
    icon: "Network"
  }
];

const LecturesCatalog: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {demoLectures.map((lecture) => (
        <LectureCard key={lecture.id} lecture={lecture} />
      ))}
    </div>
  );
};

export default LecturesCatalog;
