import React, { useState } from 'react';
import { authService } from '../../api/authService';

interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const res = await authService.requestPasswordReset(email);
      setSuccessMessage(res.message);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Có lỗi xảy ra, vui lòng thử lại');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setSuccessMessage(null);
    setErrorMessage(null);
    onClose();
  };

  return (
    <div className="vfit-modal-overlay" onClick={handleClose}>
      <div className="vfit-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="vfit-modal-close" onClick={handleClose} aria-label="Đóng">
          ✕
        </button>

        <h2 className="vfit-auth-title" style={{ fontSize: '1.45rem', marginBottom: '0.5rem' }}>
          Khôi phục mật khẩu
        </h2>
        <p className="vfit-auth-subtitle" style={{ marginBottom: '1.25rem' }}>
          Nhập email đăng ký của bạn để nhận liên kết đặt lại mật khẩu.
        </p>

        {errorMessage && (
          <div className="vfit-alert-banner" style={{ marginBottom: '1rem' }}>
            <span>⚠️ {errorMessage}</span>
          </div>
        )}

        {successMessage ? (
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>✉️</div>
            <p style={{ color: 'var(--vfit-success-emerald)', fontWeight: 600, fontSize: '0.95rem' }}>
              {successMessage}
            </p>
            <button
              type="button"
              className="vfit-btn-primary"
              style={{ marginTop: '1.25rem' }}
              onClick={handleClose}
            >
              ĐÃ HIỂU
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="vfit-auth-form" style={{ marginTop: '0.5rem' }}>
            <div className="vfit-input-group">
              <label className="vfit-input-label" htmlFor="reset-email">
                Email
              </label>
              <div className="vfit-input-wrapper">
                <input
                  id="reset-email"
                  type="email"
                  className="vfit-input-field"
                  placeholder="example@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                />
              </div>
            </div>

            <button type="submit" className="vfit-btn-primary" disabled={isLoading}>
              {isLoading ? <div className="vfit-spinner" /> : <span>GỬI YÊU CẦU</span>}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
