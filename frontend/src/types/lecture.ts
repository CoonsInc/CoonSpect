// src/types/lecture.ts

export interface GetLecturesParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
  user_id?: string;
}

export interface LectureUpdate {
  name?: string;
  text?: string;
}

export interface Lecture {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface LecturesPage {
  items: Lecture[];
  total: number;
  page: number;
  pages: number;
}
