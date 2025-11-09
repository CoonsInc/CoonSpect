// pages/ProfilePage.tsx
import Header from "../components/organisms/Header";
import Heading from "../components/atoms/Heading";
import Text from "../components/atoms/Text";
import Button from "../components/atoms/Button";
import { useAuthStore } from "../stores/authStore";
import { useNavigate } from "react-router-dom";

const ProfilePage = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <div className="bg-[#0B0C1C] text-white min-h-screen">
      <Header />
      <div className="pt-24 p-6">
        <div className="max-w-4xl mx-auto">
          <Heading level={1} className="text-3xl font-bold mb-6">
            Профиль пользователя
          </Heading>
          
          <div className="bg-[#16182D] rounded-lg p-6 border border-purple-800/40">
            <div className="grid gap-4">
              <div>
                <Text className="text-gray-400 text-sm">Имя пользователя</Text>
                <Text className="text-lg">{user?.username}</Text>
              </div>
              <div>
                <Text className="text-gray-400 text-sm">ID</Text>
                <Text className="text-lg">{user?.id}</Text>
              </div>
            </div>
            
            <div className="mt-8 pt-6 border-t border-purple-800/30">
              <Button 
                onClick={handleLogout}
                variant="secondary"
                className="bg-red-600 hover:bg-red-700 text-white border-red-600"
              >
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