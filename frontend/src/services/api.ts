import axios from 'axios';

// Resolve normalized Base API URL (supports both relative /api/v1 and full backend origins)
export const getBaseUrl = (): string => {
  const raw = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const trimmed = raw.trim().replace(/\/+$/, '');
  if (trimmed.startsWith('http') && !trimmed.endsWith('/api/v1')) {
    return `${trimmed}/api/v1`;
  }
  return trimmed;
};

export const API_BASE_URL = getBaseUrl();

// Base API instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Ensure cookies are sent if ever required
  withCredentials: true,
});

// Interceptor to attach the API key to every request if it exists
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // We can add global error toast logic here if we add a toast library
    console.error('API Error:', error.response?.data?.error || error.message);
    return Promise.reject(error);
  }
);