import axios from 'axios';

const isDesktopOrFile =
  typeof window !== 'undefined' &&
  (window.location.protocol === 'file:' ||
    window.navigator.userAgent.includes('Electron') ||
    window.location.hostname === '');

const API_BASE = isDesktopOrFile
  ? ((import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000/api/v1')
  : '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('assistiq_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear token and notify if not already on login
      const currentPath = window.location.pathname;
      if (currentPath !== '/login') {
        localStorage.removeItem('assistiq_token');
        localStorage.removeItem('assistiq_user');
      }
    }
    return Promise.reject(error);
  }
);
