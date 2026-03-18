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
    lecturer?: string;
    text?: string;
}

export interface UserRead {
    id: string;
}

export interface Lecture {
    id: string;
    user: UserRead;
    lecturer: string;
    name: string;
    audio_url: string;
    text: string;
    created_at: string;
    updated_at: string;
}

export interface LecturesPage {
    items: Lecture[];
    total: number;
    page: number;
    pages: number;
}