import React, { useState } from 'react';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { ForgotPasswordModal } from '../../components/auth/ForgotPasswordModal';
import { SocialLoginButtons } from '../../components/auth/SocialLoginButtons';
import { useAuth } from '../../hooks/useAuth';

interface LoginPageProps {
  onNavigateToRegister?: () => void;
  onLoginSuccess?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onNavigateToRegister,
  onLoginSuccess,
}) => {
  const { login, socialLogin, isLoading, error, clearError } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    try {
      await login({ email, password, rememberMe });
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng nhập không thành công');
    }
  };

  const handleGoogleLogin = async () => {
    clearError();
    setLocalError(null);
    try {
      await socialLogin('google');
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng nhập Google thất bại');
    }
  };

  const handleFacebookLogin = async () => {
    clearError();
    setLocalError(null);
    try {
      await socialLogin('facebook');
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng nhập Facebook thất bại');
    }
  };

  const displayError = localError || error;

  return (
    <AuthLayout>
      {/* Card Header */}
      <div className="vfit-auth-header">
        {/* AI Security Badge Icon */}
        <div className="vfit-security-badge-outer">
          <div className="vfit-security-badge-inner">
            <svg
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="M9 12l2 2 4-4" />
            </svg>
          </div>
        </div>

        <h1 className="vfit-auth-title">ĐĂNG NHẬP</h1>
        <p className="vfit-auth-subtitle">
          Chào mừng bạn quay trở lại với{' '}
          <span className="vfit-brand-highlight">AI TRY-ON</span>
        </p>
      </div>

      {/* Error Alert Banner */}
      {displayError && (
        <div className="vfit-alert-banner">
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{displayError}</span>
        </div>
      )}

      {/* Form Container */}
      <form className="vfit-auth-form" onSubmit={handleSubmit}>
        {/* Email Field */}
        <div className="vfit-input-group">
          <label className="vfit-input-label" htmlFor="email">
            Email
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="email"
              type="email"
              className="vfit-input-field"
              placeholder="example@gmail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <div className="vfit-input-icon">
              <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Password Field */}
        <div className="vfit-input-group">
          <label className="vfit-input-label" htmlFor="password">
            Mật khẩu
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              className="vfit-input-field"
              placeholder="•••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
            <button
              id="toggle-password"
              type="button"
              className="vfit-password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
            >
              {showPassword ? (
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"
                  />
                </svg>
              ) : (
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Checkbox & Forgot Password */}
        <div className="vfit-form-row-between">
          <label className="vfit-checkbox-label">
            <input
              type="checkbox"
              className="vfit-checkbox-input"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            <span>Ghi nhớ đăng nhập</span>
          </label>
          <button
            type="button"
            className="vfit-link"
            onClick={() => setIsForgotModalOpen(true)}
          >
            Quên mật khẩu?
          </button>
        </div>

        {/* Primary CTA Button */}
        <div>
          <button type="submit" className="vfit-btn-primary" disabled={isLoading}>
            {isLoading ? (
              <div className="vfit-spinner" />
            ) : (
              <>
                <span>ĐĂNG NHẬP</span>
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                  />
                </svg>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Minimal Divider */}
      <div className="vfit-divider-row">
        <div className="vfit-divider-line" />
        <span className="vfit-divider-text">HOẶC</span>
        <div className="vfit-divider-line" />
      </div>

      {/* Social Logins */}
      <SocialLoginButtons
        onGoogleLogin={handleGoogleLogin}
        onFacebookLogin={handleFacebookLogin}
        isLoading={isLoading}
      />

      {/* Registration Prompt */}
      <div className="vfit-switch-prompt">
        <span>Chưa có tài khoản? </span>
        <button
          type="button"
          className="vfit-link"
          onClick={onNavigateToRegister}
        >
          Đăng ký ngay
        </button>
      </div>

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={isForgotModalOpen}
        onClose={() => setIsForgotModalOpen(false)}
      />
    </AuthLayout>
  );
};
