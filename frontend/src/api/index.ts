import axios, { AxiosError } from 'axios';

export const apiClient = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (error.response) {
      if (error.response.status === 401 && originalRequest && !(originalRequest as any)._isRetry) {
        (originalRequest as any)._isRetry = true;
        
        try {
          await axios.post('/auth/refresh', {}, { withCredentials: true });
          
          return apiClient.request(originalRequest);
        } catch (refreshError) {
          console.log('The session has expired or the user is not logged in.');
        }
      }
      const data = error.response.data as any;
      if (data && data.detail) {
        error.message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    }
    return Promise.reject(error);  
  }
);

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
export const WS_BASE_URL = `${protocol}//${window.location.host}`;

export default apiClient;
