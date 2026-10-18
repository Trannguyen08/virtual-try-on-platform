import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../api/authService';
import { AuthState, LoginCredentials, RegisterCredentials, User } from '../api/authTypes';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterCredentials) => Promise<void>;
  socialLogin: (provider: 'google' | 'facebook') => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Khởi tạo phiên làm việc từ storage khi reload trang
  useEffect(() => {
    const { user: storedUser, token: storedToken } = authService.getStoredSession();
    if (storedUser && storedToken) {
      setUser(storedUser);
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      setToken(response.token);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Đăng nhập thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.register(data);
      setUser(response.user);
      setToken(response.token);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Đăng ký thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const socialLogin = async (provider: 'google' | 'facebook') => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.socialLogin(provider);
      setUser(response.user);
      setToken(response.token);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Đăng nhập mạng xã hội thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        error,
        login,
        register,
        socialLogin,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
