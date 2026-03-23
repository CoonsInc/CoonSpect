// stores/textStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { startAndTrackLectureTask, getLectureResult } from '../api/generateApi';
import { editLecture } from '../api/lecturesApi'

interface AudioState {
  audioFile: File | null;
  audioUrl: string | null;
  
  activeLectureId: string | null;
  lectureTitle: string;
  processedText: string;
  
  isSaving: boolean;
  progressStatus: string | null;

  setAudioFile: (file: File | null) => void;
  setLectureTitle: (title: string) => void;
  setProcessedText: (text: string) => void;
  reset: () => void;
  clearAudioFile: () => void;

  generateTranscript: (file: File) => Promise<void>;
  loadLecture: (id: string) => Promise<void>;
  saveLectureChanges: (text: string, title: string) => Promise<void>;
}

export const useTextStore = create<AudioState>()(
  persist(
    (set, get) => ({
      audioFile: null,
      audioUrl: null,
      activeLectureId: null,
      lectureTitle: '',
      processedText: '',
      isSaving: false,
      progressStatus: null,

      setAudioFile: (file) => {
        const prev = get().audioUrl;
        if (prev) URL.revokeObjectURL(prev);

        if (file) {
          const audioUrl = URL.createObjectURL(file);
          const defaultTitle = file.name.replace(/\.[^/.]+$/, "");
          set({ audioFile: file, audioUrl, lectureTitle: defaultTitle });
        } else {
          set({ audioFile: null, audioUrl: null, lectureTitle: '' });
        }
      },

      setLectureTitle: (title) => set({ lectureTitle: title }),
      setProcessedText: (text) => set({ processedText: text }),

      reset: () => set({
        audioFile: null,
        audioUrl: null,
        activeLectureId: null,
        lectureTitle: '',
        processedText: '',
        isSaving: false,
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

          const lecture = await getLectureResult(lectureId);
          const text = lecture.text || lecture.transcription || ''; 
          
          set({ 
            activeLectureId: lectureId,
            processedText: text, 
            lectureTitle: lecture.name || get().lectureTitle,
            progressStatus: 'finish' 
          });

        } catch (e) {
          console.error('[FRONT] Audio processing error:', e);
          set({ progressStatus: 'error' });
          throw e;
        } finally {
          set({ isSaving: false });
        }
      },

      loadLecture: async (id: string) => {
        set({ isSaving: true, progressStatus: 'loading' });
        try {
          const lecture = await getLectureResult(id);
          set({
            activeLectureId: lecture.id,
            lectureTitle: lecture.name || '',
            processedText: lecture.text || lecture.transcription || '',
            progressStatus: 'finish'
          });
        } catch (e) {
          console.error('[FRONT] Failed to load lecture:', e);
          set({ progressStatus: 'error' });
        } finally {
          set({ isSaving: false });
        }
      },

      saveLectureChanges: async (text: string, title: string) => {
        const id = get().activeLectureId;
        if (!id) throw new Error("Нет активной лекции для сохранения");

        set({ isSaving: true });
        try {
          await editLecture(id, { name: title, text: text });
          set({ processedText: text, lectureTitle: title });
        } catch (e) {
          console.error('[FRONT] Failed to save lecture:', e);
          throw e;
        } finally {
          set({ isSaving: false });
        }
      }
    }),
    {
      name: 'audio-storage',
      partialize: (state) => ({
        activeLectureId: state.activeLectureId,
        lectureTitle: state.lectureTitle,
        processedText: state.processedText,
      }),
    }
  )
);
