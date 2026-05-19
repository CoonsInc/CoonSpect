import { create } from 'zustand';
import { searchInLecture, type SearchResult } from '../api/searchApi';

interface SearchState {
  results: SearchResult[];
  isLoading: boolean;
  error: string | null;
  lastQuery: string;

  search: (lectureId: string, query: string) => Promise<void>;
  clearResults: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  results: [],
  isLoading: false,
  error: null,
  lastQuery: '',

  search: async (lectureId: string, query: string) => {
    set({ isLoading: true, error: null, lastQuery: query });
    try {
      const results = await searchInLecture(lectureId, query);
      set({ results, error: results.length === 0 ? 'Ничего не найдено.' : null });
    } catch (e) {
      console.error('[FRONT] Search error:', e);
      set({ error: 'Произошла ошибка при поиске.' });
    } finally {
      set({ isLoading: false });
    }
  },

  clearResults: () => set({ results: [], error: null, lastQuery: '' }),
}));