import React, { useEffect, useRef, useCallback } from 'react'; // 👈 добавили useCallback
import { useNavigate } from 'react-router-dom';
import { useCatalogStore, useAuthStore } from '../../stores/';
import type { GetLecturesParams } from '../../types/lecture';
import Text from '../atoms/Text';
import Button from '../atoms/Button';
import Heading from '../atoms/Heading';
import Icon from '../atoms/Icon';
import LectureCard from '../molecules/LectureCard';
import CatalogControls from '../molecules/CatalogControls';

export type CatalogScope = 'my' | 'all';

interface LecturesCatalogProps {
  scope?: CatalogScope;
  emptyStateTitle?: string;
  emptyStateText?: string;
}

const LecturesCatalog: React.FC<LecturesCatalogProps> = ({ 
  scope = 'my',
  emptyStateTitle = 'Здесь пока пусто',
  emptyStateText = 'Загрузите аудио, чтобы создать свой первый конспект'
}) => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  const { 
    lectures, isLoading, error, currentPage, totalPages,
    sortBy, order, fetchLectures, setPage, setSortBy, toggleOrder,
  } = useCatalogStore();

  const isInitialMount = useRef(true);

  const loadLectures = useCallback((contextParams: GetLecturesParams) => {
    fetchLectures(contextParams);
  }, [fetchLectures]);

  useEffect(() => {
    const params: GetLecturesParams = scope === 'my' && user?.id 
      ? { user_id: user.id, page: 1 } 
      : { page: 1 };
    
    loadLectures(params);
    isInitialMount.current = false;
  }, [scope, user?.id, loadLectures]);

  useEffect(() => {
    if (isInitialMount.current) return;

    const params: GetLecturesParams = scope === 'my' && user?.id 
      ? { user_id: user.id, page: 1, sort_by: sortBy, order } 
      : { page: 1, sort_by: sortBy, order };
    
    loadLectures(params);
  }, [sortBy, order, scope, user?.id, loadLectures]);

  const handleOpenLecture = (id: string) => navigate(`/lec/${id}`);

  const handleSortByChange = (newSort: typeof sortBy) => {
    setSortBy(newSort);
  };

  const handleOrderToggle = () => {
    toggleOrder();
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    const params: GetLecturesParams = scope === 'my' && user?.id 
      ? { user_id: user.id, page: newPage, sort_by: sortBy, order } 
      : { page: newPage, sort_by: sortBy, order };
    loadLectures(params);
  };

  if (isLoading && lectures.length === 0) {
    return (
      <div className="py-20 flex justify-center items-center">
        <Text className="text-[var(--color-text-secondary)]">
          {scope === 'my' ? 'Загрузка вашей библиотеки...' : 'Загрузка каталога...'}
        </Text>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center">
        <Text className="text-[var(--color-warning)] mb-4">Ошибка: {error}</Text>
        <Button 
          onClick={() => {
            const params = scope === 'my' && user?.id ? { user_id: user.id } : {};
            fetchLectures(params);
          }} 
          variant="secondary"
        >
          Попробовать снова
        </Button>
      </div>
    );
  }

  if (lectures.length === 0) {
    return (
      <div className="py-24 text-center bg-[var(--color-bg-accent)] rounded-xl border border-dashed border-[var(--color-border)]">
        <div className="w-16 h-16 mx-auto mb-4 bg-[var(--color-bg-secondary)] rounded-full flex items-center justify-center">
          <Icon name="DockIcon" className="w-8 h-8 text-[var(--color-text-secondary)]" />
        </div>
        <Heading level={3} className="text-xl mb-2">{emptyStateTitle}</Heading>
        <Text className="text-[var(--color-text-secondary)] mb-6">{emptyStateText}</Text>
        {scope === 'all' && (
          <Button variant="primary" onClick={() => navigate('/my-lectures')}>
            Перейти в мою библиотеку
          </Button>
        )}
      </div>
    );
  }

  return (
    <div>
      {/* Контролы сортировки */}
      <div className="mb-6 flex justify-end">
        <CatalogControls
          sortBy={sortBy}
          order={order}
          onSortByChange={handleSortByChange}
          onOrderToggle={handleOrderToggle}
        />
      </div>

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
            onClick={() => handlePageChange(currentPage - 1)}
          >
            Назад
          </Button>
          <Text className="font-medium">{currentPage} / {totalPages}</Text>
          <Button 
            variant="secondary" 
            disabled={currentPage === totalPages} 
            onClick={() => handlePageChange(currentPage + 1)}
          >
            Вперед
          </Button>
        </div>
      )}
    </div>
  );
};

export default LecturesCatalog;
