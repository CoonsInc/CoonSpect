// pages/LoginPage.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores';
import LoginForm from '../components/molecules/LoginForm';
import Heading from '../components/atoms/Heading';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, register } = useAuthStore();
  const [authLoading, setAuthLoading] = useState(false);

  const handleAuth = async (
    authFn: (username: string, password: string) => Promise<void>, 
    username: string, 
    password: string
  ) => {
    setAuthLoading(true);
    try {
      await authFn(username, password);
      navigate('/upload');
    } catch (error) {
      console.error('Auth error:', error);
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen flex flex-col items-center justify-center p-6">
      <div className="text-center max-w-md w-full">
        <Heading 
          level={1} 
          className="text-4xl font-bold text-[var(--color-text-purple)] mb-8"
        >
          Coonspect <span className="text-2xl">(●'◡'●)</span>
        </Heading>
        
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
