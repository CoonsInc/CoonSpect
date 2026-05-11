import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTextStore, useAuthStore, useAppStore } from '../stores';
import MainPage from './MainPage';
import Header from '../components/organisms/Header';
import Footer from '../components/organisms/Footer';
import ViewLectureSection from '../components/organisms/ViewLectureSection';
import Spinner from '../components/atoms/Spinner';

const LectureRouterPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { loadLecture, currentLecture, progressStatus, audioUrl, reset } = useTextStore();
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
    
    return () => {
      reset(); 
      setAppState('upload');
    };
  }, [id, loadLecture, setAppState, reset]);

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
        <button onClick={() => navigate('/lectures')} className="text-[var(--color-text-purple)] underline">
          Вернуться в каталог
        </button>
      </div>
    );
  }

  const isOwner = user?.id === currentLecture.user.id;

  if (isOwner) {
    return <MainPage />;
  } else {
    return (
      <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen font-sans overflow-x-hidden">
        <Header /> 
        <ViewLectureSection 
          title={currentLecture.name || 'Без названия'} 
          text={currentLecture.text || ''} 
          audioUrl={audioUrl || undefined}
          onBack={() => navigate(-1)} 
        />
        <Footer />
      </div>
    );
  }
};

export default LectureRouterPage;
