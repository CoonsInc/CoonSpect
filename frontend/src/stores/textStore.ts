// stores/textStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Lecture } from '../types/lecture.ts';
import { startAndTrackLectureTask, getLectureResult, startAndTrackExampleTask } from '../api/generateApi';
import { getLectureAudioLink, editLecture, deleteLecture } from '../api/lecturesApi';

interface AudioState {
  audioFile: File | null;
  audioUrl: string | null;
  
  activeLectureId: string | null;
  lectureTitle: string;
  processedText: string;
  currentLecture: Lecture | null;
  
  isSaving: boolean;
  progressStatus: string | null;

  setAudioFile: (file: File | null) => void;
  setLectureTitle: (title: string) => void;
  setProcessedText: (text: string) => void;
  deleteCurrentLecture: () => Promise<void>;
  restoreAudio: () => Promise<void>;
  reset: () => void;
  clearAudioFile: () => void;

  generateTranscript: (file: File) => Promise<void>;
  generateExampleTranscript: (filename: string, title: string) => Promise<void>;
  loadLecture: (id: string) => Promise<void>;
  saveLectureChanges: (text: string, title: string) => Promise<void>;
  toggleLecturePrivacy: () => Promise<void>;
}

export const useTextStore = create<AudioState>()(
  persist(
    (set, get) => ({
      audioFile: null,
      audioUrl: null,
      activeLectureId: null,
      lectureTitle: '',
      currentLecture: null,
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
            lectureTitle: (lecture.name && !lecture.name.includes('.ogg')) ? lecture.name : get().lectureTitle,
            currentLecture: lecture,
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

      generateExampleTranscript: async (filename: string, title: string) => {
        set({ 
          isSaving: true, 
          progressStatus: 'starting_example', 
          lectureTitle: title,
          audioFile: null, 
          audioUrl: null 
        });

        try {
          const { lectureId } = await startAndTrackExampleTask(
            filename,
            (status) => set({ progressStatus: status })
          );

          const lecture = await getLectureResult(lectureId);
          const text = lecture.text || lecture.transcription || ''; 
          
          set({ 
            activeLectureId: lectureId,
            processedText: text, 
            lectureTitle: lecture.name || title,
            currentLecture: lecture,
            progressStatus: 'finish' 
          });

        } catch (e) {
          console.error('[FRONT] Example audio processing error:', e);
          set({ progressStatus: 'error' });
          throw e;
        } finally {
          set({ isSaving: false });
        }
      },

      restoreAudio: async () => {
        const id = get().activeLectureId;
        const currentAudio = get().audioUrl;

        if (!id || (currentAudio && currentAudio.startsWith('blob:'))) return;

        try {
          console.log(`[STORE] Запрашиваем audiolink для:`, id);
          const res: any = await getLectureAudioLink(id);
          console.log(`[STORE] Ответ от бэкенда (audiolink):`, res);

          let link = typeof res === 'string' ? res : (res?.msg || res?.data || res?.url || res?.link || res?.audio_url);

          if (!link) {
            console.warn('[STORE] audiolink не отдал понятную ссылку, дергаем саму лекцию...');
            const lecture = await getLectureResult(id);
            link = lecture.audio_url;
          }

          if (link) {
            try {
              if (link.startsWith('http')) {
                const urlObj = new URL(link);
                link = urlObj.pathname + urlObj.search; 
              }
            } catch (e) {
              console.warn('Не удалось распарсить URL', e);
            }

            console.log(`[STORE] Ура! Готовая ссылка для Nginx:`, link);
            set({ audioUrl: link });
          } else {
            console.error('[STORE] Ссылка на аудио так и не нашлась :(');
          }
        } catch (e) {
          console.error('[STORE] Ошибка восстановления аудио:', e);
        }
      },

      loadLecture: async (id: string) => {
        set({ progressStatus: 'loading' }); 
        
        try {
          const data = await getLectureResult(id);
          

          set({
            currentLecture: data,
            activeLectureId: id,
            processedText: data.text || '',
            lectureTitle: data.name || '',
            progressStatus: 'success',
          });

          console.log(`[STORE] Lecture text loaded. Now restoring audio for: ${id}`);


          await get().restoreAudio();

          console.log(`[STORE] Audio link successfully restored.`);

        } catch (e) {
          console.error('[FRONT] Error inside loadLecture:', e);
          set({ progressStatus: 'error' });
          throw e;
        }
      },

      deleteCurrentLecture: async () => {
        const id = get().activeLectureId;
        if (!id) throw new Error("Нет активной лекции для удаления");

        set({ isSaving: true });
        try {
            await deleteLecture(id);
            set({
              activeLectureId: null,
              lectureTitle: '',
              processedText: '',
              currentLecture: null,
              audioUrl: null,
              audioFile: null,
            });
        } catch (e) {
          console.error('[FRONT] Failed to delete lecture:', e);
          throw e;
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
      },

      toggleLecturePrivacy: async () => {
        const id = get().activeLectureId;
        const current = get().currentLecture;
        if (!id || !current) throw new Error("Нет активной лекции");

        set({ isSaving: true });
        try {
          const nextPublicState = !current.public;
          const updatedLecture = await editLecture(id, { public: nextPublicState });
          
          set({ 
            currentLecture: { 
              ...current, 
              public: updatedLecture.public ?? nextPublicState 
            } 
          });
        } catch (e) {
          console.error('[FRONT] Failed to toggle lecture privacy:', e);
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