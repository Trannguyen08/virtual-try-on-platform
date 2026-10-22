import { AuthResponse, LoginCredentials, RegisterCredentials, User } from './authTypes';

const STORAGE_KEY_TOKEN = 'vfit_auth_token';
const STORAGE_KEY_USER = 'vfit_auth_user';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Giả lập network latency 400ms để hiển thị loading state mượt mà
    await new Promise((resolve) => setTimeout(resolve, 400));

    if (!credentials.email || !credentials.password) {
      throw new Error('Vui lòng nhập đầy đủ email và mật khẩu');
    }

    if (!credentials.email.includes('@')) {
      throw new Error('Định dạng email không hợp lệ');
    }

    if (credentials.password.length < 6) {
      throw new Error('Mật khẩu phải có ít nhất 6 ký tự');
    }

    // Mock response chuẩn xác
    const mockUser: User = {
      id: `usr_${Date.now()}`,
      email: credentials.email,
      name: credentials.email.split('@')[0],
      avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${credentials.email}`,
      provider: 'local',
      createdAt: new Date().toISOString(),
    };

    const token = `jwt_mock_${btoa(credentials.email)}_${Date.now()}`;

    if (credentials.rememberMe) {
      localStorage.setItem(STORAGE_KEY_TOKEN, token);
      localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));
    } else {
      sessionStorage.setItem(STORAGE_KEY_TOKEN, token);
      sessionStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));
    }

    return { user: mockUser, token };
  },

  async register(data: RegisterCredentials): Promise<AuthResponse> {
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (!data.name || !data.email || !data.password) {
      throw new Error('Vui lòng điền đầy đủ tất cả các trường');
    }

    if (!data.email.includes('@')) {
      throw new Error('Email không hợp lệ');
    }

    if (data.password.length < 6) {
      throw new Error('Mật khẩu phải có ít nhất 6 ký tự');
    }

    if (data.confirmPassword && data.password !== data.confirmPassword) {
      throw new Error('Mật khẩu xác nhận không khớp');
    }

    const mockUser: User = {
      id: `usr_${Date.now()}`,
      email: data.email,
      name: data.name,
      avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.email}`,
      provider: 'local',
      createdAt: new Date().toISOString(),
    };

    const token = `jwt_mock_${btoa(data.email)}_${Date.now()}`;
    sessionStorage.setItem(STORAGE_KEY_TOKEN, token);
    sessionStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));

    return { user: mockUser, token };
  },

  async socialLogin(provider: 'google' | 'facebook'): Promise<AuthResponse> {
    await new Promise((resolve) => setTimeout(resolve, 600));

    const mockEmail = provider === 'google' ? 'user.google@gmail.com' : 'user.fb@facebook.com';
    const mockUser: User = {
      id: `usr_${provider}_${Date.now()}`,
      email: mockEmail,
      name: provider === 'google' ? 'Google User' : 'Facebook User',
      avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${provider}`,
      provider: provider,
      createdAt: new Date().toISOString(),
    };

    const token = `oauth_${provider}_mock_${Date.now()}`;
    localStorage.setItem(STORAGE_KEY_TOKEN, token);
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));

    return { user: mockUser, token };
  },

  async requestPasswordReset(email: string): Promise<{ success: boolean; message: string }> {
    await new Promise((resolve) => setTimeout(resolve, 400));
    if (!email || !email.includes('@')) {
      throw new Error('Vui lòng nhập địa chỉ email hợp lệ');
    }
    return {
      success: true,
      message: `Đã gửi mã liên kết đặt lại mật khẩu tới ${email}. Vui lòng kiểm tra hộp thư.`,
    };
  },

  logout(): void {
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(STORAGE_KEY_USER);
    sessionStorage.removeItem(STORAGE_KEY_TOKEN);
    sessionStorage.removeItem(STORAGE_KEY_USER);
  },

  getStoredSession(): { user: User | null; token: string | null } {
    try {
      const token = localStorage.getItem(STORAGE_KEY_TOKEN) || sessionStorage.getItem(STORAGE_KEY_TOKEN);
      const userRaw = localStorage.getItem(STORAGE_KEY_USER) || sessionStorage.getItem(STORAGE_KEY_USER);
      if (token && userRaw) {
        return { token, user: JSON.parse(userRaw) as User };
      }
    } catch {
      // Bỏ qua lỗi parse JSON nếu storage hỏng
    }
    return { user: null, token: null };
  },
};
