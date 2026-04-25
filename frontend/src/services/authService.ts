import { api } from './api';
import { RegisterResponse, LoginResponse } from '../types/apiResponses';

export const authService = {
  /**
   * Register a new user
   */
  register: async (username: string, email: string, password: string): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/register', {
      username,
      email,
      password
    });
    return response.data;
  },

  /**
   * Login an existing user
   */
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/login', {
      email,
      password
    });
    return response.data;
  }
};