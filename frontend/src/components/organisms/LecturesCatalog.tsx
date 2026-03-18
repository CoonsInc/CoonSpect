// components/organisms/LecturesCatalog.tsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCatalogStore, useTextStore, useAppStore } from '../../stores';
import Text from '../atoms/Text';
import Button from '../atoms/Button';
import Heading from '../atoms/Heading';
import Icon from '../atoms/Icon';

const LecturesCatalog: React.FC = () => {
  const navigate = useNavigate();
  const { setAppState } = useAppStore();
  const { loadLecture } = useTextStore();
  
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
    fetchLectures();
  }, [fetchLectures]);

  const handleOpenLecture = async (id: string) => {
    try {
      await loadLecture(id);
      
      setAppState("editor");
      
      navigate('/');
    } catch (e) {
      alert("Не удалось загрузить лекцию");
    }
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
          <div 
            key={lecture.id} 
            onClick={() => handleOpenLecture(lecture.id)}
            className="flex flex-col p-5 bg-[var(--color-bg-accent)] rounded-xl border border-[var(--color-border)] shadow-sm hover:shadow-md hover:border-[var(--color-text-purple)] transition-all cursor-pointer group"
          >
            <div className="mb-4">
              <Heading level={4} className="text-lg font-semibold group-hover:text-[var(--color-text-purple)] transition-colors line-clamp-2">
                {lecture.name || 'Лекция без названия'}
              </Heading>
              {lecture.lecturer && (
                <Text className="text-sm text-[var(--color-text-secondary)] mt-1">
                  Преподаватель: {lecture.lecturer}
                </Text>
              )}
            </div>

            <div className="mt-auto pt-4 border-t border-[var(--color-border)] flex items-center justify-between text-xs text-[var(--color-text-secondary)]">
              <span>{new Date(lecture.created_at).toLocaleDateString('ru-RU')}</span>
              <span className="flex items-center gap-1 group-hover:text-[var(--color-text-purple)] transition-colors">
                Открыть <Icon name="ArrowRight" className="w-3 h-3" />
              </span>
            </div>
          </div>
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
