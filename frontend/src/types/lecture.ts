// src/types/lecture.ts
import type { User } from "./users.ts";

export interface GetLecturesParams {
    page?: number;
    limit?: number;
    sort_by?: string;
    order?: 'asc' | 'desc';
    user_id?: string;
    search_name?: string;
    scope?: string;
}

export interface LectureUpdate {
    name?: string;
    lecturer?: string;
    text?: string;
    public?: boolean;
}

export interface Lecture {
    id: string;
    user: User;
    lecturer: string;
    name: string;
    audio_url: string;
    text: string;
    public: boolean;
    created_at: string;
    updated_at: string;
}

export interface LecturesPage {
    items: Lecture[];
    total: number;
    page: number;
    pages: number;
}

export interface ExampleTaskDescription {
    filename: string;
    title: string;
    description: string;
}
