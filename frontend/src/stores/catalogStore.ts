import { create } from 'zustand';
import { getLecturesList } from '../api/lecturesApi';
import type { GetLecturesParams, Lecture } from '../types/lecture';

export type SortByOption = 'created_at' | 'name' | 'updated_at';
export type OrderOption = 'asc' | 'desc';

const STORAGE_KEYS = {
  SORT_BY: 'catalog_sort_by',
  ORDER: 'catalog_order',
} as const;

const getStored = <T>(key: string, fallback: T): T => {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
};

const setStored = <T>(key: string, value: T): void => {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn(`[Storage] Failed to save ${key}:`, e);
  }
};

const DEFAULT_PARAMS = {
  limit: 24,
  sort_by: 'created_at',
  order: 'desc',
} as const;

interface CatalogState {
  lectures: Lecture[];
  total: number;
  currentPage: number;
  totalPages: number;
  page: number;
  sortBy: SortByOption;
  order: OrderOption;
  searchName: string;
  isLoading: boolean;
  error: string | null;
  scope: 'all' | 'my'; 

  fetchLectures: (contextParams?: GetLecturesParams) => Promise<void>;
  setPage: (page: number) => void;
  setSortBy: (sortBy: SortByOption) => void;
  toggleOrder: () => void;
  setSearchName: (name: string) => void;
  setScope: (scope: 'all' | 'my') => void;
}

export const useCatalogStore = create<CatalogState>()((set, get) => ({
  lectures: [],
  total: 0,
  currentPage: 1,
  totalPages: 1,
  page: 1,
  sortBy: getStored<SortByOption>(STORAGE_KEYS.SORT_BY, 'created_at'),
  order: getStored<OrderOption>(STORAGE_KEYS.ORDER, 'desc'),
  searchName: '',
  isLoading: false,
  error: null,
  scope: 'all',

  setScope: (scope) => set({ scope }), 

  fetchLectures: async (contextParams) => {
    const state = get();
    
    const requestParams = {
      ...DEFAULT_PARAMS,
      page: contextParams?.page ?? state.page,
      sort_by: state.sortBy,
      order: state.order,
      search_name: state.searchName || undefined,
      scope: state.scope,
      ...contextParams, 
    };

    set({ isLoading: true, error: null });

    try {
      const data = await getLecturesList(requestParams);
      
      set({
        lectures: data.items,
        total: data.total,
        currentPage: data.page,
        totalPages: data.pages,
        page: data.page,
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

  setPage: (page) => {
    set({ page });
  },

  setSortBy: (sortBy) => {
    setStored(STORAGE_KEYS.SORT_BY, sortBy);
    set({ sortBy });
  },

  toggleOrder: () => {
    const nextOrder = get().order === 'asc' ? 'desc' : 'asc';
    setStored(STORAGE_KEYS.ORDER, nextOrder);
    set({ order: nextOrder });
  },

  setSearchName: (searchName) => {
    set({ searchName });
  }
}));