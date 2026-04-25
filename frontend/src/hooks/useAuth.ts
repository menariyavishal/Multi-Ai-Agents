import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

interface UserData {
  userId: string;
  username?: string;
  email?: string;
}

export function useAuth() {
  const [apiKey, setApiKey] = useState<string | null>(localStorage.getItem('api_key'));
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize from storage on mount
  useEffect(() => {
    const storedApiKey = localStorage.getItem('api_key');
    const storedUserId = localStorage.getItem('user_id');
    const storedUsername = localStorage.getItem('username');
    
    if (storedApiKey && storedUserId) {
      setApiKey(storedApiKey);
      setUser({
        userId: storedUserId,
        username: storedUsername || 'User',
      });
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      if (data.status === 'success') {
        const { api_key, user_id, username } = data;
        localStorage.setItem('api_key', api_key);
        localStorage.setItem('user_id', user_id);
        localStorage.setItem('username', username || 'User');
        
        setApiKey(api_key);
        setUser({ userId: user_id, username: username || 'User' });
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (username: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authService.register(username, email, password);
      if (data.status === 'success') {
        const { api_key, user_id } = data;
        localStorage.setItem('api_key', api_key);
        localStorage.setItem('user_id', user_id);
        localStorage.setItem('username', username);
        
        setApiKey(api_key);
        setUser({ userId: user_id, username });
        return true;
      }
      return false;
    } catch (error) {
      console.error(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('api_key');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    setApiKey(null);
    setUser(null);
  }, []);

  return {
    apiKey,
    user,
    isAuthenticated: !!apiKey,
    isLoading,
    login,
    register,
    logout
  };
}