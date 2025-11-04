// stores/mainStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AudioFileState {
  audioFile: File | null;
  audioUrl: string | null;
  lastSavedPath: string | null;
  isSaving: boolean;

  processedText: string;

  currentRoute: string;

  appState: 'upload' | 'loading' | 'editor';

  user: { id: string; username: string; profile?: string; settings?: string } | null;

  setAudioFile: (file: File | null) => void;
  setLastSavedPath: (path: string | null) => void;
  setIsSaving: (saving: boolean) => void;
  setProcessedText: (text: string) => void;
  setCurrentRoute: (route: string) => void;
  setAppState: (state: 'upload' | 'loading' | 'editor') => void;
  setUser: (user: { id: string; username: string; profile?: string; settings?: string } | null) => void;
  reset: () => void;
  clearAudioFile: () => void;
}

export const useMainStore = create<AudioFileState>()(
  persist(
    (set) => ({
      audioFile: null,
      audioUrl: null,
      lastSavedPath: null,
      isSaving: false,
      processedText: '',
      currentRoute: '/',
      appState: 'upload',
      user: null,

      setAudioFile: (file: File | null) => {
        if (file) {
          const audioUrl = URL.createObjectURL(file);
          set({ audioFile: file, audioUrl, lastSavedPath: null });
        } else {
          set({ audioFile: null, audioUrl: null, lastSavedPath: null });
        }
      },
      setLastSavedPath: (path: string | null) => set({ lastSavedPath: path }),
      setIsSaving: (isSaving: boolean) => set({ isSaving }),
      setProcessedText: (text: string) => set({ processedText: text }),
      setCurrentRoute: (route: string) => set({ currentRoute: route }),
      setAppState: (state: 'upload' | 'loading' | 'editor') => set({ appState: state }),
      setUser: (user: { id: string; username: string; profile?: string; settings?: string } | null) => set({ user }),
      reset: () => set({
        audioFile: null,
        audioUrl: null,
        lastSavedPath: null,
        isSaving: false,
        processedText: '',
        appState: 'upload'
      }),
      clearAudioFile: () => {
        set({
          audioFile: null,
          audioUrl: null,
          lastSavedPath: null,
          isSaving: false
        });
      },
    }),
    {
      name: 'audio-storage',
      partialize: (state) => ({
       audioFile: null,
        audioUrl: state.audioUrl,
        lastSavedPath: state.lastSavedPath,
        processedText: state.processedText,
        currentRoute: state.currentRoute,
        appState: 'upload', // Всегда сбрасываем состояние на upload при перезагрузке
        user: state.user
      }),
    }
  )
);
