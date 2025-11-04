import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '../api/mockClient';
import { mockApi } from '../api/mockClient';

interface UserContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isInitializing: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initializeUser = async () => {
      try {
        console.log('🚀 Инициализация пользователя...');
        const currentUser = await mockApi.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
          console.log('✅ Автоматический вход:', currentUser.username);
        } else {
          // Если пользователь не аутентифицирован, перенаправляем на /upload после инициализации
          console.log('⚠️ Пользователь не аутентифицирован, перенаправление на /upload');
        }

      } catch (error) {
        console.log('⚠️ Ошибка инициализации пользователя:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeUser();
  }, []);

  const login = async (username: string, password: string) => {
    const userData = await mockApi.login(username, password);
    setUser(userData);
  };

  const register = async (username: string, _password: string) => {
    const userData = await mockApi.register(username);
    setUser(userData);
  };

  const logout = async () => {
    await mockApi.logout();
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ user, login, register, logout, isInitializing }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};