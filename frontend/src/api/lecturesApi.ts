import { apiClient } from './index';
import type { GetLecturesParams, LectureUpdate, LecturesPage, Lecture } from '../types/lecture';

export async function getLecturesList(params: GetLecturesParams = {}): Promise<LecturesPage> {
    console.log(`[FRONT] Fetching lectures list`, params);
    
    const { scope, ...restParams } = params;
    
    const endpoint = scope === 'my' ? '/user/lectures' : '/lecture/list';
    
    const response = await apiClient.get(endpoint, { params: restParams });
    return response.data;
}

export async function editLecture(lectureId: string, updateData: LectureUpdate): Promise<Lecture> {
    console.log(`[FRONT] Editing lecture ${lectureId}`);
    const response = await apiClient.patch(`/lecture/edit/${lectureId}`, updateData);
    return response.data;
}

export async function getLectureAudioLink(lectureId: string): Promise<{ status: string, data: string }> {
    console.log(`[FRONT] Fetching audio link for ${lectureId}`);
    const response = await apiClient.get(`/lecture/audiolink/${lectureId}`);
    return response.data; 
}

export async function deleteLecture(lectureId: string): Promise<{ status: string; message: string }> {
    console.log(`[FRONT] Deleting lecture ${lectureId}`);
    const response = await apiClient.delete(`/lecture/delete/${lectureId}`);
    return response.data;
}