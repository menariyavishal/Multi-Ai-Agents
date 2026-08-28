import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

interface UserData {
  userId: string;
  username?: string;
  email?: string;
}

interface AuthContextType {
  apiKey: string | null;
  user: UserData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [apiKey, setApiKey] = useState<string | null>(() => localStorage.getItem('api_key'));
  const [user, setUser] = useState<UserData | null>(() => {
    const storedUserId = localStorage.getItem('user_id');
    const storedUsername = localStorage.getItem('username');
    if (storedUserId) {
      return { userId: storedUserId, username: storedUsername || 'Operator' };
    }
    // Default guest user so queries always work out of the box!
    return { userId: 'guest_operator', username: 'Guest Operator' };
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const storedApiKey = localStorage.getItem('api_key');
    const storedUserId = localStorage.getItem('user_id');
    const storedUsername = localStorage.getItem('username');

    if (storedUserId) {
      setUser({
        userId: storedUserId,
        username: storedUsername || 'Operator',
      });
      if (storedApiKey) setApiKey(storedApiKey);
    } else {
      // Ensure guest credentials stored
      localStorage.setItem('user_id', 'guest_operator');
      localStorage.setItem('username', 'Guest Operator');
      setUser({ userId: 'guest_operator', username: 'Guest Operator' });
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      if (data.status === 'success') {
        const { api_key, user_id, username } = data;
        localStorage.setItem('api_key', api_key);
        localStorage.setItem('user_id', user_id);
        localStorage.setItem('username', username || 'Operator');

        setApiKey(api_key);
        setUser({ userId: user_id, username: username || 'Operator' });
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
      console.error('Registration error:', error);
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
    setUser({ userId: 'guest_operator', username: 'Guest Operator' });
  }, []);

  const isAuthenticated = !!(user && user.userId && user.userId !== 'guest_operator') || !!apiKey;

  return (
    <AuthContext.Provider
      value={{
        apiKey,
        user,
        isAuthenticated,
        isLoading,
        login,
        register,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}
