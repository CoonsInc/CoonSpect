import { apiClient } from './index';
import type { LoginPayload, User } from '../types/users';

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
