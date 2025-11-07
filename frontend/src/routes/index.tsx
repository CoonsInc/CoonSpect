import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
// import { useUser } from "../contexts/UserContext";
import { useAppStore, useAuthStore } from "../stores";
import { useEffect } from 'react';
import LoginPage from '../pages/LoginPage';
import MainPage from '../pages/MainPage';
import FilesPage from '../pages/FilesPage';
import ProfilePage from '../pages/ProfilePage';

// const LoginRoute = () => <LoginPage />;

const AppRoutes = () => {
  const { user, isInitializing } = useAuthStore();
  const location = useLocation();
  const { setCurrentRoute } = useAppStore();

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
      <Route 
        path="/login" 
        element={!user ? <LoginPage /> : <Navigate to="/upload" replace />} 
      />
      <Route path="/" element={<Navigate to="/upload" replace />} />
      <Route path="/upload" element={<MainPage />} />
      <Route 
        path="/files" 
        element={user ? <FilesPage /> : <Navigate to="/login" replace />} 
      />
      <Route 
        path="/profile" 
        element={user ? <ProfilePage /> : <Navigate to="/login" replace />} 
      />
      
      <Route path="*" element={<Navigate to="/upload" replace />} />
    </Routes>
  );
};

export default AppRoutes;
