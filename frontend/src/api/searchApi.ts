import { apiClient } from './index';

export interface SearchResult {
  score: number;
  start: number;
  end: number;
  text: string;
}

export async function searchInLecture(
  lectureId: string, 
  query: string
): Promise<SearchResult[]> {
  console.log(`[FRONT] Searching in lecture ${lectureId}: "${query}"`);
  const response = await apiClient.get(`/search/${lectureId}`, { 
    params: { query } 
  });
  return response.data.results;
}