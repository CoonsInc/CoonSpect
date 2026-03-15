import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores';

const ProtectedRoute = () => {
  const { user } = useAuthStore();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
