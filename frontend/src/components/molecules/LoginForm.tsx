import { useState, useEffect } from 'react';
import Button from '../atoms/Button';
import Input from '../atoms/Input';
import Text from '../atoms/Text';

interface LoginFormProps {
  onLogin: (username: string, password: string) => Promise<void>;
  onRegister: (username: string, password: string) => Promise<void>;
  isLoading?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, onRegister, isLoading = false }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);

  useEffect(() => {
    const savedUsername = localStorage.getItem('username');
    const savedPassword = localStorage.getItem('password');
    const savedIsRegister = localStorage.getItem('isRegister');
    if (savedUsername) setUsername(savedUsername);
    if (savedPassword) setPassword(savedPassword);
    if (savedIsRegister) setIsRegister(JSON.parse(savedIsRegister));

    const handleBeforeUnload = () => {
      sessionStorage.setItem('loginPageReloaded', 'true');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      const reloaded = sessionStorage.getItem('loginPageReloaded');
      sessionStorage.removeItem('loginPageReloaded');
      if (!reloaded) {
        localStorage.removeItem('username');
        localStorage.removeItem('password');
        localStorage.removeItem('isRegister');
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;

    try {
      if (isRegister) {
        await onRegister(username, password);
      } else {
        await onLogin(username, password);
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Произошла ошибка');
    }
  };

  return (
    <div className="bg-dark-100 p-6 rounded-lg border border-purple-500/20 max-w-md w-full">
      <Text size="lg" className="text-white font-semibold mb-4 text-center">
        {isRegister ? 'Регистрация' : 'Вход в систему'}
      </Text>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            localStorage.setItem('username', e.target.value);
          }}
          disabled={isLoading}
        />
        
        <Input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            localStorage.setItem('password', e.target.value);
          }}
          disabled={isLoading}
        />
        
        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={isLoading || !username || !password}
        >
          {isLoading ? 'Загрузка...' : (isRegister ? 'Зарегистрироваться' : 'Войти')}
        </Button>
      </form>

      <div className="mt-4 text-center">
        <Text size="sm" className="text-gray-400">
          {isRegister ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}{' '}
          <button
            type="button"
            onClick={() => {
              const newIsRegister = !isRegister;
              setIsRegister(newIsRegister);
              localStorage.setItem('isRegister', JSON.stringify(newIsRegister));
            }}
            className="text-purple-400 hover:text-purple-300 underline"
          >
            {isRegister ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </Text>
      </div>
    </div>
  );
};

export default LoginForm;