import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useUser();

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  const handleProfileClick = () => {
    if (user) {
      // Если пользователь авторизован, показываем меню или перенаправляем
      // Пока просто выходим
      logout();
    } else {
      // Если не авторизован, переходим на страницу входа
      navigate('/login');
    }
  };

  return (
    <header className="fixed top-0 left-0 w-full bg-[#0B0C1C]/80 backdrop-blur-md border-b border-purple-800/30 z-50">
      <div className="max-w-6xl mx-auto flex justify-between items-center py-4 px-6">

        <h1 className="text-2xl font-semibold text-purple-400">CoonSpect</h1>
        <nav className="flex gap-6 text-sm">
          <button onClick={() => scrollTo("hero")} className="hover:text-purple-400 transition">
            Главная
          </button>
          <button onClick={() => scrollTo("how")} className="hover:text-purple-400 transition">
            Как это работает
          </button>
          <button onClick={() => scrollTo("examples")} className="hover:text-purple-400 transition">
            Примеры
          </button>
          <button onClick={() => navigate('/files')} className="hover:text-purple-400 transition">
            Мои файлы
          </button>
          <button onClick={handleProfileClick} className="hover:text-purple-400 transition">
            {user ? 'Профиль' : 'Войти'}
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
