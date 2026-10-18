import React, { useState } from 'react';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { SocialLoginButtons } from '../../components/auth/SocialLoginButtons';
import { useAuth } from '../../hooks/useAuth';

interface RegisterPageProps {
  onNavigateToLogin?: () => void;
  onRegisterSuccess?: () => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({
  onNavigateToLogin,
  onRegisterSuccess,
}) => {
  const { register, socialLogin, isLoading, error, clearError } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError('Mật khẩu xác nhận không khớp');
      return;
    }

    if (!agreeTerms) {
      setLocalError('Vui lòng đồng ý với Điều khoản dịch vụ');
      return;
    }

    try {
      await register({ name, email, password, confirmPassword, agreeTerms });
      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng ký không thành công');
    }
  };

  const handleGoogleLogin = async () => {
    clearError();
    setLocalError(null);
    try {
      await socialLogin('google');
      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng ký bằng Google thất bại');
    }
  };

  const handleFacebookLogin = async () => {
    clearError();
    setLocalError(null);
    try {
      await socialLogin('facebook');
      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Đăng ký bằng Facebook thất bại');
    }
  };

  const displayError = localError || error;

  return (
    <AuthLayout>
      {/* Card Header */}
      <div className="vfit-auth-header">
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
              <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
              <circle cx="8.5" cy="7" r="4" />
              <line x1="20" y1="8" x2="20" y2="14" />
              <line x1="23" y1="11" x2="17" y2="11" />
            </svg>
          </div>
        </div>

        <h1 className="vfit-auth-title">TẠO TÀI KHOẢN</h1>
        <p className="vfit-auth-subtitle">
          Khám phá trải nghiệm thử đồ 3D cùng{' '}
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
        {/* Full Name Field */}
        <div className="vfit-input-group">
          <label className="vfit-input-label" htmlFor="register-name">
            Họ và tên
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="register-name"
              type="text"
              className="vfit-input-field"
              placeholder="Nguyễn Văn A"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="name"
            />
            <div className="vfit-input-icon">
              <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Email Field */}
        <div className="vfit-input-group">
          <label className="vfit-input-label" htmlFor="register-email">
            Email
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="register-email"
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
          <label className="vfit-input-label" htmlFor="register-password">
            Mật khẩu (tối thiểu 6 ký tự)
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="register-password"
              type={showPassword ? 'text' : 'password'}
              className="vfit-input-field"
              placeholder="•••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <button
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

        {/* Confirm Password Field */}
        <div className="vfit-input-group">
          <label className="vfit-input-label" htmlFor="register-confirm-password">
            Xác nhận mật khẩu
          </label>
          <div className="vfit-input-wrapper">
            <input
              id="register-confirm-password"
              type={showPassword ? 'text' : 'password'}
              className="vfit-input-field"
              placeholder="•••••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>
        </div>

        {/* Terms Agreement Checkbox */}
        <div className="vfit-form-row-between" style={{ justifyContent: 'flex-start' }}>
          <label className="vfit-checkbox-label">
            <input
              type="checkbox"
              className="vfit-checkbox-input"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              required
            />
            <span style={{ fontSize: '0.85rem' }}>
              Tôi đồng ý với{' '}
              <a href="#terms" className="vfit-link">
                Điều khoản dịch vụ
              </a>{' '}
              &{' '}
              <a href="#privacy" className="vfit-link">
                Chính sách bảo mật
              </a>
            </span>
          </label>
        </div>

        {/* Primary CTA Button */}
        <div>
          <button type="submit" className="vfit-btn-primary" disabled={isLoading}>
            {isLoading ? (
              <div className="vfit-spinner" />
            ) : (
              <>
                <span>ĐĂNG KÝ NGAY</span>
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

      {/* Switch to Login Prompt */}
      <div className="vfit-switch-prompt">
        <span>Đã có tài khoản? </span>
        <button
          type="button"
          className="vfit-link"
          onClick={onNavigateToLogin}
        >
          Đăng nhập ngay
        </button>
      </div>
    </AuthLayout>
  );
};
