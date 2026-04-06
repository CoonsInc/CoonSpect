import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from "../stores";

import LoginPage from '../pages/LoginPage';
import MainPage from '../pages/MainPage';
import LecturesPage from '../pages/LecturesPage';
import ProfilePage from '../pages/ProfilePage';
import ViewLecturePage from '../pages/ViewLecturePage';

import ProtectedRoute from './ProtectedRoute';
import Spinner from '../components/atoms/Spinner';

const AppRoutes = () => {
  const { isInitializing } = useAuthStore();
  // const location = useLocation();
  // const { setCurrentRoute } = useAppStore();

  // useEffect(() => {
  //   setCurrentRoute(location.pathname);
  // }, [location.pathname, setCurrentRoute]);

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

      {/* ЗАЩИЩЕННЫЕ РОУТЫ */}
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/lectures" element={<LecturesPage />} />
        <Route path="/view-lecture" element={<ViewLecturePage />} />
      </Route>
      
      {/* FALLBACK (если путь не найден) */}
      <Route path="*" element={<Navigate to="/upload" replace />} />
    </Routes>
  );
};

export default AppRoutes;
