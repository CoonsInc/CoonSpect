// api/index.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  headers: { 'Content-Type': 'application/json' },
});

export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:3000/ws';

// Добавим interceptor для авторизации (например, если токен будет храниться в localStorage)
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); // позже можно заменить на zustand
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
