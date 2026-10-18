export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  provider?: 'local' | 'google' | 'facebook';
  createdAt?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterCredentials {
  name: string;
  email: string;
  password: string;
  confirmPassword?: string;
  agreeTerms?: boolean;
}

export interface AuthResponse {
  user: User;
  token: string;
  expiresIn?: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
