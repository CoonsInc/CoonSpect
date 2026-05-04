import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useTextStore, useAuthStore, useAppStore } from '../stores';
import MainPage from './MainPage';
import ViewLecturePage from './ViewLecturePage';
import Spinner from '../components/atoms/Spinner';

const LectureRouterPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { loadLecture, currentLecture, progressStatus } = useTextStore();
  const { user } = useAuthStore();
  const { setAppState } = useAppStore();
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    
    loadLecture(id)
      .then(() => {
        setIsLoading(false);
        setAppState('editor');
      })
      .catch(() => {
        setError(true);
        setIsLoading(false);
      });
  }, [id, loadLecture, setAppState]);

  if (isLoading || progressStatus === 'loading') {
    return (
      <div className="bg-[var(--color-bg-primary)] min-h-screen flex flex-col items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !currentLecture) {
    return (
      <div className="bg-[var(--color-bg-primary)] min-h-screen flex flex-col items-center justify-center text-white">
        <h1 className="text-2xl font-bold mb-4">Лекция не найдена</h1>
        <p className="text-[var(--color-text-secondary)]">Возможно, ссылка устарела или удалена.</p>
      </div>
    );
  }

  const isOwner = user?.id === currentLecture.user.id;

  if (isOwner) {
    return <MainPage />;
  } else {
    return <ViewLecturePage />;
  }
};

export default LectureRouterPage;
