import { apiClient } from './index';

export interface LoginPayload {
  username: string;
  password: string;
}

export interface User {
  id: string;
  username: string;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<void> => {
    await apiClient.post('/auth/login', payload);
  },

  register: async (payload: LoginPayload): Promise<void> => {
    await apiClient.post('/auth/register', payload);
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User | null> => {
    try {
      const res = await apiClient.get<User>('/user/me');
      return res.data;
    } catch (error) {
      return null;
    }
  },
};
