import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import LoginForm from '../components/molecules/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, register } = useUser();
  const [authLoading, setAuthLoading] = useState(false);

  const handleAuth = async (authFn: (username: string, password: string) => Promise<void>, username: string, password: string) => {
    setAuthLoading(true);
    try {
      await authFn(username, password);
      navigate('/upload');
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <div className="bg-[#0B0C1C] text-white min-h-screen flex items-center justify-center p-6">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-purple-400 mb-8">
          AudioNotes AI
        </h1>
        <LoginForm
          onLogin={(username, password) => handleAuth(login, username, password)}
          onRegister={(username, password) => handleAuth(register, username, password)}
          isLoading={authLoading}
        />
      </div>
    </div>
  );
};

export default LoginPage;
