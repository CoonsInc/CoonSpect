import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useUser } from "../contexts/UserContext";
import { useMainStore } from "../stores/mainStore";
import { useEffect } from 'react';
import LoginPage from '../pages/LoginPage';
import MainPage from '../pages/MainPage';
import FilesPage from '../pages/FilesPage';

const LoginRoute = () => <LoginPage />;

const AppRoutes = () => {
  const { isInitializing } = useUser();
  const location = useLocation();
  const { setCurrentRoute } = useMainStore();

  useEffect(() => {
    setCurrentRoute(location.pathname);
  }, [location.pathname, setCurrentRoute]);

  if (isInitializing) {
    return (
      <div className="bg-[#0B0C1C] text-white min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route
        path="/"
        element={<Navigate to="/upload" replace />}
      />
      <Route
        path="/upload"
        element={<MainPage />}
      />
      <Route
        path="/files"
        element={<FilesPage />}
      />
    </Routes>
  );
};

export default AppRoutes;
