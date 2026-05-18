import { useState, useEffect } from 'react';
import Button from '../atoms/Button';
import Input from '../atoms/Input';
import Text from '../atoms/Text';

interface LoginFormProps {
  onLogin: (username: string, password: string) => Promise<void>;
  onRegister: (username: string, password: string) => Promise<void>;
  isLoading?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onLogin,
  onRegister,
  isLoading = false
}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

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

  const validateForm = (): boolean => {
    if (username.length < 3 || username.length > 50) {
      setErrorMsg('Имя пользователя должно быть от 3 до 50 символов');
      return false;
    }
    if (password.length < 6) {
      setErrorMsg('Пароль должен содержать минимум 6 символов');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!validateForm()) return;

    try {
      if (isRegister) {
        await onRegister(username, password);
      } else {
        await onLogin(username, password);
      }
    } catch (error: any) {
      const backendError = error.response?.data?.detail || error.response?.data?.message;

      if (backendError) {
        if (Array.isArray(backendError)) {
          setErrorMsg(backendError[0].msg || 'Ошибка валидации данных на сервере');
        } else {
          setErrorMsg(backendError);
        }
      } else if (error.message?.includes('400')) {
        setErrorMsg(isRegister ? 'Пользователь с таким именем уже существует' : 'Неверные данные');
      } else if (error.message?.includes('401')) {
        setErrorMsg('Неверное имя пользователя или пароль');
      } else {
        setErrorMsg(error.message || 'Произошла неизвестная ошибка');
      }
    }
  };

  const isFormValid = username.length >= 3 && username.length <= 50 && password.length >= 6;

  return (
    <div className="bg-[var(--color-bg-secondary)] p-6 rounded-lg border border-[var(--color-border)] max-w-md w-full">
      <Text size="lg" className="text-[var(--color-text-primary)] font-semibold mb-4 text-center">
        {isRegister ? 'Регистрация' : 'Вход в систему'}
      </Text>

      {/* Блок ошибки*/}
      {errorMsg && (
        <div className="mb-4 p-3 bg-[var(--color-bg-tertiary)] border border-[var(--color-warning)] rounded text-[var(--color-warning)] text-sm text-center shadow-[0_0_8px_var(--color-warning)]">
          {errorMsg === 'Invalid credentials' ? 'Неверное имя пользователя или пароль' : 
           errorMsg === 'Username already exists' ? 'Пользователь с таким именем уже существует' : 
           errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            localStorage.setItem('username', e.target.value);
            if (errorMsg) setErrorMsg('');
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
            if (errorMsg) setErrorMsg('');
          }}
          disabled={isLoading}
        />
        
        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={isLoading || !isFormValid}
        >
          {isLoading ? 'Загрузка...' : (isRegister ? 'Зарегистрироваться' : 'Войти')}
        </Button>
      </form>

      <div className="mt-4 text-center">
        <Text size="sm" className="text-[var(--color-text-secondary)]">
          {isRegister ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}{' '}
          <button
            type="button"
            onClick={() => {
              const newIsRegister = !isRegister;
              setIsRegister(newIsRegister);
              localStorage.setItem('isRegister', JSON.stringify(newIsRegister));
              setErrorMsg('');
            }}
            className="text-[var(--color-text-purple)] hover:opacity-80 underline transition-opacity"
          >
            {isRegister ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </Text>
      </div>
    </div>
  );
};

export default LoginForm;