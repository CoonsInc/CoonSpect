import { useEffect } from "react";
import Header from "../components/organisms/Header";
import Heading from "../components/atoms/Heading";
import Text from "../components/atoms/Text";
import Button from "../components/atoms/Button";
import Icon from "../components/atoms/Icon";
import { useAuthStore } from "../stores/authStore";
import { useAppStore } from "../stores";
import { useNavigate } from "react-router-dom";

const ProfilePage = () => {
  const { user, logout } = useAuthStore();
  const { setAppState } = useAppStore();
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

  const handleNewLecture = () => {
    setAppState("upload");
    navigate("/");
  };

  const handleMyLectures = () => {
    navigate("/my-lectures");
  };

  if (!user) {
    return null;
  }

  return (
    <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen">
      <Header />
      
      <div className="pt-24 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Heading level={2} className="text-3xl font-bold">
              Профиль пользователя
            </Heading>
          </div>
          
          <div className="bg-[var(--color-bg-secondary)] rounded-xl p-8 border border-[var(--color-border)] shadow-sm">
            <div className="flex items-center gap-6 mb-8 pb-6 border-b border-[var(--color-border)]">
              <div className="w-20 h-20 rounded-full bg-[var(--color-text-purple)]/10 flex items-center justify-center">
                <span className="text-3xl font-bold text-[var(--color-text-purple)]">
                  {user.username?.[0]?.toUpperCase() || "?"}
                </span>
              </div>
              
              <div>
                <div className="space-y-1">
                  <Text size="sm" className="text-[var(--color-text-secondary)] uppercase">
                    Имя пользователя
                  </Text>
                  <div className="flex items-center gap-2">
                    <Text className="text-lg font-medium">{user.username}</Text>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <Button
                onClick={handleMyLectures}
                variant="secondary"
                className="flex items-center gap-2 justify-center"
              >
                <Icon name="FileText" className="w-4 h-4" />
                Мои лекции
              </Button>
              
              <Button
                onClick={handleNewLecture}
                variant="secondary"
                className="flex items-center gap-2 justify-center"
              >
                <Icon name="Upload" className="w-4 h-4" />
                Новая лекция
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
