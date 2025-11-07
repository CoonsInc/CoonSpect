//управление состоянием приложения (маршруты, состояния экранов)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  currentRoute: string;
  appState: 'upload' | 'loading' | 'editor';
  setCurrentRoute: (route: string) => void;
  setAppState: (state: 'upload' | 'loading' | 'editor') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentRoute: '/',
      appState: 'upload',

      setCurrentRoute: (route: string) => set({ currentRoute: route }),
      setAppState: (state: 'upload' | 'loading' | 'editor') => set({ appState: state }),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        currentRoute: state.currentRoute,
        appState: state.appState,
      }),
    }
  )
);
