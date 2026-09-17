import axios from 'axios';

const API_BASE = '/api/v1';

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
