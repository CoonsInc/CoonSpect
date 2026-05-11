import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from "../stores";

import LoginPage from '../pages/LoginPage';
import MainPage from '../pages/MainPage';
import MyLecturesPage from '../pages/MyLecturesPage';
import AllLecturesPage from '../pages/AllLecturesPage';
import ProfilePage from '../pages/ProfilePage';
import LectureRouterPage from '../pages/LectureRouterPage';

import ProtectedRoute from './ProtectedRoute';
import Spinner from '../components/atoms/Spinner';

const AppRoutes = () => {
  const { isInitializing } = useAuthStore();

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
      <Route path="/lec/:id" element={<LectureRouterPage />} />
      <Route path="/lectures" element={<AllLecturesPage />} />

      {/* ЗАЩИЩЕННЫЕ РОУТЫ */}
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/my-lectures" element={<MyLecturesPage />} />
        {/* <Route path="/view-lecture" element={<ViewLecturePage />} /> */}
      </Route>
      
      {/* FALLBACK (если путь не найден) */}
      <Route path="*" element={<Navigate to="/upload" replace />} />
    </Routes>
  );
};

export default AppRoutes;
