import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { createLectureTask, uploadAudioViaWebSocket, getLectureResult } from '../api/lectureApi';

interface AudioState {
  audioFile: File | null;
  audioUrl: string | null;
  lastSavedPath: string | null;
  isSaving: boolean;
  processedText: string;
  progressStatus: string | null;

  setAudioFile: (file: File | null) => void;
  setLastSavedPath: (path: string | null) => void;
  setIsSaving: (saving: boolean) => void;
  setProcessedText: (text: string) => void;
  setProgressStatus: (status: string | null) => void;
  reset: () => void;
  clearAudioFile: () => void;

  generateTranscript: (file: File) => Promise<void>;
}

export const useTextStore = create<AudioState>()(
  persist(
    (set, get) => ({
      audioFile: null,
      audioUrl: null,
      lastSavedPath: null,
      isSaving: false,
      processedText: '',
      progressStatus: null,

      setAudioFile: (file) => {
        const prev = get().audioUrl;
        if (prev) URL.revokeObjectURL(prev);

        if (file) {
          const audioUrl = URL.createObjectURL(file);
          set({ audioFile: file, audioUrl, lastSavedPath: null });
        } else {
          set({ audioFile: null, audioUrl: null, lastSavedPath: null });
        }
      },

      setLastSavedPath: (path) => set({ lastSavedPath: path }),
      setIsSaving: (isSaving) => set({ isSaving }),
      setProcessedText: (text) => set({ processedText: text }),
      setProgressStatus: (status) => set({ progressStatus: status }),

      reset: () => set({
        audioFile: null,
        audioUrl: null,
        lastSavedPath: null,
        isSaving: false,
        processedText: '',
        progressStatus: null,
      }),

      clearAudioFile: () => {
        const prev = get().audioUrl;
        if (prev) URL.revokeObjectURL(prev);
        set({ audioFile: null, audioUrl: null, lastSavedPath: null, isSaving: false });
      },

      generateTranscript: async (file: File) => {
        const { setIsSaving, setProgressStatus, setProcessedText } = get();
        setIsSaving(true);
        setProgressStatus('uploading');

        try {
          const { task_id } = await createLectureTask();
          console.log('Created task_id:', task_id);

          await uploadAudioViaWebSocket(file, task_id, (status) => {
            console.log('Progress update:', status);
            setProgressStatus(status);
          });

          const result = await getLectureResult(task_id);
          console.log('Received result:', result);
          setProcessedText(result.content);
          setProgressStatus('finish');

        } catch (err) {
          console.error('Ошибка при обработке аудио:', err);
          setProgressStatus(null);
        } finally {
          setIsSaving(false);
        }
      },
    }),
    {
      name: 'audio-storage',
      partialize: (state) => ({
        processedText: state.processedText,
        progressStatus: state.progressStatus,
      }),
    }
  )
);
