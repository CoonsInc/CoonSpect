import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/', 
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true
});

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
export const WS_BASE_URL = `${protocol}//${window.location.host}`;

export default apiClient;
