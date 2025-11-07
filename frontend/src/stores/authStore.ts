// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../api/authApi';

export interface User {
  id: string;
  username: string;
  profile?: string;
  settings?: string;
}

interface AuthState {
  user: User | null;
  isInitializing: boolean;

  setUser: (user: User | null) => void;
  initialize: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isInitializing: true,

      setUser: (user) => set({ user }),

      initialize: async () => {
        set({ isInitializing: true });
        try {
          const currentUser = await authApi.getCurrentUser();
          if (currentUser) {
            set({ user: currentUser });
            console.log('✅ Восстановлен пользователь:', currentUser.username);
          } else {
            console.log('⚠️ Пользователь не найден');
          }
        } catch (error) {
          console.warn('Ошибка при инициализации authStore', error);
        } finally {
          set({ isInitializing: false });
        }
      },

      login: async (username, password) => {
        try {
          const user = await authApi.login({ username, password });
          set({ user });
        } catch (error) {
          console.error('Ошибка входа', error);
          throw error;
        }
      },

      register: async (username, password) => {
        try {
          const user = await authApi.register({ username, password });
          set({ user });
        } catch (error) {
          console.error('Ошибка регистрации', error);
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch (e) {
          console.warn('Ошибка выхода, очищаем локально', e);
        } finally {
          set({ user: null });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
      }),
    }
  )
);
