import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAppStore, useAuthStore } from "../stores";
import { useEffect } from 'react';

import LoginPage from '../pages/LoginPage';
import MainPage from '../pages/MainPage';
import LecturesPage from '../pages/LecturesPage';
import ProfilePage from '../pages/ProfilePage';

import ProtectedRoute from './ProtectedRoute';
import Spinner from '../components/atoms/Spinner';

const AppRoutes = () => {
  const { isInitializing } = useAuthStore();
  // const location = useLocation();
  // const { setCurrentRoute } = useAppStore();

  // useEffect(() => {
  //   setCurrentRoute(location.pathname);
  // }, [location.pathname, setCurrentRoute]);

  // Заменяем хардкод на твой аккуратный Spinner
  if (isInitializing) {
    return (
      <div className="bg-[var(--color-bg-primary)] min-h-screen flex flex-col items-center justify-center">
        <Spinner size="lg" />
        <p className="text-[var(--color-text-secondary)] mt-4 text-sm font-medium">
          Загрузка...
        </p>
      </div>
    );
  }

  return (
    <Routes>
      {/* ПУБЛИЧНЫЕ РОУТЫ */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/upload" replace />} />
      <Route path="/upload" element={<MainPage />} />

      {/* ЗАЩИЩЕННЫЕ РОУТЫ (Группируем их внутри ProtectedRoute) */}
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/lectures" element={<LecturesPage />} />
      </Route>
      
      {/* FALLBACK (если путь не найден) */}
      <Route path="*" element={<Navigate to="/upload" replace />} />
    </Routes>
  );
};

export default AppRoutes;
