// api/authApi.ts
// import { apiClient } from './index';
import { mockApi } from './mockClient';
import type { User } from './mockClient';


export interface LoginPayload {
  username: string;
  password: string;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<User> => {
    // TODO: заменить на реальный запрос
    // return apiClient.post<User>('/auth/login', payload).then(res => res.data);
    return mockApi.login(payload.username, payload.password);
  },

  register: async (payload: LoginPayload): Promise<User> => {
    // TODO: заменить на реальный запрос
    return mockApi.register(payload.username);
  },

  logout: async (): Promise<void> => {
    return mockApi.logout();
  },

  getCurrentUser: async (): Promise<User | null> => {
    return mockApi.getCurrentUser();
  },
};
