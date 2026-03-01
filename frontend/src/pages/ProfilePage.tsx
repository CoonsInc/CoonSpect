
import { useEffect } from "react";
import Header from "../components/organisms/Header";
import Heading from "../components/atoms/Heading";
import Text from "../components/atoms/Text";
import Button from "../components/atoms/Button";
import Icon from "../components/atoms/Icon";
import { useAuthStore } from "../stores/authStore";
import { useNavigate } from "react-router-dom";

const ProfilePage = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/");
    } catch (error) {
      console.error("Ошибка при выходе:", error);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen">
      <Header />
      
      <div className="pt-24 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Заголовок с кнопкой назад */}
          <div className="flex items-center gap-4 mb-8">
            <Button
              onClick={() => navigate(-1)}
              variant="ghost"
              size="sm"
              className="flex items-center gap-2"
            >
              <Icon name="ArrowLeft" className="w-4 h-4" />
              Назад
            </Button>
            <Heading level={1} className="text-3xl font-bold">
              Профиль пользователя
            </Heading>
          </div>
          
          {/* Карточка профиля */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl p-8 border border-[var(--color-border)] shadow-sm">
            {/* Аватар и основная информация */}
            <div className="flex items-center gap-6 mb-8 pb-6 border-b border-[var(--color-border)]">
              <div className="w-20 h-20 rounded-full bg-[var(--color-text-purple)]/10 flex items-center justify-center">
                <span className="text-3xl font-bold text-[var(--color-text-purple)]">
                  {user.username?.[0]?.toUpperCase() || "?"}
                </span>
              </div>
              <div>
                <Heading level={2} className="text-2xl font-semibold mb-1">
                  {user.username}
                </Heading>
                <Text className="text-[var(--color-text-secondary)]">
                  Участник с {new Date().toLocaleDateString('ru-RU', { 
                    month: 'long', 
                    year: 'numeric' 
                  })}
                </Text>
              </div>
            </div>
            
            {/* Детальная информация - только существующие поля */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="space-y-1">
                <Text size="sm" className="text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Имя пользователя
                </Text>
                <div className="flex items-center gap-2">
                  <Text className="text-lg font-medium">{user.username}</Text>
                  <span className="px-2 py-0.5 text-xs bg-[var(--color-success)]/10 text-[var(--color-success)] rounded-full">
                    Активен
                  </span>
                </div>
              </div>
              
              <div className="space-y-1">
                <Text size="sm" className="text-[var(--color-text-secondary)] uppercase tracking-wider">
                  ID пользователя
                </Text>
                <Text className="font-mono text-sm bg-[var(--color-bg-tertiary)] px-3 py-1.5 rounded-md inline-block">
                  {user.id}
                </Text>
              </div>
            </div>
            
            {/* Действия */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-[var(--color-border)]">
              <Button
                onClick={() => navigate("/files")}
                variant="secondary"
                className="flex items-center gap-2 justify-center"
              >
                <Icon name="FileText" className="w-4 h-4" />
                Мои файлы
              </Button>
              
              <Button
                onClick={() => navigate("/upload")}
                variant="secondary"
                className="flex items-center gap-2 justify-center"
              >
                <Icon name="Upload" className="w-4 h-4" />
                Загрузить аудио
              </Button>
              
              <Button
                onClick={handleLogout}
                variant="outline"
                className="flex items-center gap-2 justify-center ml-auto border-[var(--color-warning)] text-[var(--color-warning)] hover:bg-[var(--color-warning)] hover:text-white"
              >
                <Icon name="LogOut" className="w-4 h-4" />
                Выйти из аккаунта
              </Button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
