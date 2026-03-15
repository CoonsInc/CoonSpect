// api/index.ts
import axios from 'axios';

// Используем относительный путь. Браузер сам подставит текущий IP/домен и порт.
export const apiClient = axios.create({
  baseURL: '/', 
  headers: { 'Content-Type': 'application/json' },
});

// Динамически вычисляем адрес для WebSocket на основе того, где открыт сайт
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
export const WS_BASE_URL = `${protocol}//${window.location.host}`;

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

export default apiClient;
