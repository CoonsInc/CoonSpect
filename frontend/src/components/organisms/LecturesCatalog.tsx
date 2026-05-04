import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCatalogStore, useAuthStore } from '../../stores/';
import Text from '../atoms/Text';
import Button from '../atoms/Button';
import Heading from '../atoms/Heading';
import Icon from '../atoms/Icon';
import LectureCard from '../molecules/LectureCard';

const LecturesCatalog: React.FC = () => {
  const navigate = useNavigate();
  // const { setAppState } = useAppStore();
  // const { loadLecture } = useTextStore();

  const { user } = useAuthStore();
  
  const { 
    lectures, 
    isLoading, 
    error, 
    currentPage, 
    totalPages, 
    fetchLectures, 
    setPage 
  } = useCatalogStore();

  useEffect(() => {
    if (user?.id) {
      fetchLectures({ user_id: user.id });
    }
  }, [fetchLectures]);

  const handleOpenLecture = (id: string) => {
    navigate(`/lec/${id}`);
  };

  if (isLoading && lectures.length === 0) {
    return (
      <div className="py-20 flex justify-center items-center">
        <Text className="text-[var(--color-text-secondary)]">Загрузка библиотеки...</Text>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center">
        <Text className="text-[var(--color-warning)] mb-4">Ошибка: {error}</Text>
        <Button onClick={() => fetchLectures()} variant="secondary">Попробовать снова</Button>
      </div>
    );
  }

  if (lectures.length === 0) {
    return (
      <div className="py-24 text-center bg-[var(--color-bg-accent)] rounded-xl border border-dashed border-[var(--color-border)]">
        <div className="w-16 h-16 mx-auto mb-4 bg-[var(--color-bg-secondary)] rounded-full flex items-center justify-center">
          <Icon name="DockIcon" className="w-8 h-8 text-[var(--color-text-secondary)]" />
        </div>
        <Heading level={3} className="text-xl mb-2">Здесь пока пусто</Heading>
        <Text className="text-[var(--color-text-secondary)] mb-6">
          Загрузите аудио, чтобы создать свой первый конспект
        </Text>
      </div>
    );
  }

  return (
    <div>
      {/* Сетка карточек */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {lectures.map((lecture) => (
          <LectureCard 
            key={lecture.id} 
            lecture={lecture} 
            onClick={() => handleOpenLecture(lecture.id)} 
          />
        ))}
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="mt-12 flex justify-center items-center gap-6">
          <Button 
            variant="secondary"
            disabled={currentPage === 1} 
            onClick={() => setPage(currentPage - 1)}
          >
            Назад
          </Button>
          
          <Text className="font-medium">
            {currentPage} / {totalPages}
          </Text>

          <Button 
            variant="secondary"
            disabled={currentPage === totalPages} 
            onClick={() => setPage(currentPage + 1)}
          >
            Вперед
          </Button>
        </div>
      )}
    </div>
  );
};

export default LecturesCatalog;
