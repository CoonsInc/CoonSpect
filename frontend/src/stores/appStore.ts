//управление состоянием приложения (маршруты, состояния экранов)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // currentRoute: string;
  appState: 'upload' | 'loading' | 'editor';
  theme: 'dark' | 'light';
  // setCurrentRoute: (route: string) => void;
  setAppState: (state: 'upload' | 'loading' | 'editor') => void;
  setTheme: (theme: 'dark' | 'light') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // currentRoute: '/',
      appState: 'upload',
      theme: 'dark',

      // setCurrentRoute: (route: string) => set({ currentRoute: route }),
      setAppState: (state: 'upload' | 'loading' | 'editor') => set({ appState: state }),
      setTheme: (theme: 'dark' | 'light') => set({ theme }),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        // currentRoute: state.currentRoute,
        // appState: state.appState,
        theme: state.theme,
        appState: state.appState === 'editor' ? 'editor' : 'upload',
      }),
    }
  )
);
