// stores/catalogStore.ts
import { create } from 'zustand';
import { getLecturesList, editLecture } from '../api/lecturesApi'; 
import type { GetLecturesParams, LectureUpdate, LecturesPage, Lecture } from '../types/lecture';

interface CatalogState {
  lectures: Lecture[];
  total: number;
  currentPage: number;
  totalPages: number;
  
  isLoading: boolean;
  error: string | null;

  currentParams: GetLecturesParams;

  fetchLectures: (params?: GetLecturesParams) => Promise<void>;
  updateLecture: (id: string, updateData: LectureUpdate) => Promise<void>;
  setPage: (page: number) => void;
  setSorting: (sortBy: string, order: 'asc' | 'desc') => void;
}

export const useCatalogStore = create<CatalogState>()((set, get) => ({
  lectures: [],
  total: 0,
  currentPage: 1,
  totalPages: 1,
  isLoading: false,
  error: null,
  currentParams: {
    page: 1,
    limit: 10,
    sort_by: 'created_at',
    order: 'desc',
  },

  fetchLectures: async (params) => {
    const newParams = { ...get().currentParams, ...params };
    set({ isLoading: true, error: null, currentParams: newParams });

    try {
      const data: LecturesPage = await getLecturesList(newParams);
      set({
        lectures: data.items,
        total: data.total,
        currentPage: data.page,
        totalPages: data.pages,
        isLoading: false,
      });
    } catch (err: any) {
      console.error('[FRONT] Fetch lectures error:', err);
      set({ 
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки лекций', 
        isLoading: false 
      });
    }
  },

  updateLecture: async (id, updateData) => {
    try {
      await editLecture(id, updateData);
      
      // Самый простой способ обновить UI — перезапросить текущую страницу
      await get().fetchLectures(); 
    } catch (err: any) {
      console.error('[FRONT] Edit lecture error:', err);
      throw err;
    }
  },

  setPage: (page) => {
    get().fetchLectures({ page });
  },

  setSorting: (sort_by, order) => {
    get().fetchLectures({ sort_by, order, page: 1 });
  },
}));
