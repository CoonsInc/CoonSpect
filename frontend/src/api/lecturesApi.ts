import { apiClient } from './index';
import type { GetLecturesParams, LectureUpdate, LecturesPage, Lecture } from '../types/lecture';

export async function getLecturesList(params: GetLecturesParams = {}): Promise<LecturesPage> {
    console.log(`[FRONT] Fetching lectures list`, params);
    const response = await apiClient.get('/lecture/list', { params });
    return response.data;
}

export async function editLecture(lectureId: string, updateData: LectureUpdate): Promise<Lecture> {
    console.log(`[FRONT] Editing lecture ${lectureId}`);
    const response = await apiClient.patch(`/lecture/edit/${lectureId}`, updateData);
    return response.data;
}
