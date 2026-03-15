import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { startAndTrackLectureTask, getLectureResult } from '../api/generateApi';

interface AudioState {
  audioFile: File | null;
  audioUrl: string | null;
  isSaving: boolean;
  processedText: string;
  progressStatus: string | null;

  setAudioFile: (file: File | null) => void;
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
      isSaving: false,
      processedText: '',
      progressStatus: null,

      setAudioFile: (file) => {
        const prev = get().audioUrl;
        if (prev) URL.revokeObjectURL(prev);

        if (file) {
          const audioUrl = URL.createObjectURL(file);
          set({ audioFile: file, audioUrl });
        } else {
          set({ audioFile: null, audioUrl: null });
        }
      },

      setIsSaving: (isSaving) => set({ isSaving }),
      setProcessedText: (text) => set({ processedText: text }),
      setProgressStatus: (status) => set({ progressStatus: status }),

      reset: () => set({
        audioFile: null,
        audioUrl: null,
        isSaving: false,
        processedText: '',
        progressStatus: null,
      }),

      clearAudioFile: () => {
        const prev = get().audioUrl;
        if (prev) URL.revokeObjectURL(prev);
        set({ audioFile: null, audioUrl: null, isSaving: false });
      },

      generateTranscript: async (file: File) => {
        set({ isSaving: true, progressStatus: 'uploading' });

        try {
          const { lectureId } = await startAndTrackLectureTask(
            file,
            (status) => set({ progressStatus: status })
          );

          console.log('[FRONT] lecture_id received:', lectureId);

          const lecture = await getLectureResult(lectureId);
          
          const text = lecture.text || lecture.transcription || ''; 
          
          set({ processedText: text, progressStatus: 'finish' });

        } catch (e) {
          console.error('[FRONT] Audio processing error:', e);
          set({ progressStatus: 'error' });
        } finally {
          set({ isSaving: false });
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
