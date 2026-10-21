import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface UserHeaderProfileProps {
  onStartTryOn?: () => void;
}

export const UserHeaderProfile: React.FC<UserHeaderProfileProps> = ({ onStartTryOn }) => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.85rem 1.5rem',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #ecdeed',
        boxShadow: '0 2px 8px rgba(8, 10, 97, 0.03)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <img
          src={user.avatarUrl}
          alt={user.name}
          style={{
            width: '2.5rem',
            height: '2.5rem',
            borderRadius: '50%',
            backgroundColor: '#dae3f5',
            border: '2px solid #3d7eff',
          }}
        />
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#080a61' }}>
            {user.name}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#565f6e' }}>{user.email}</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {onStartTryOn && (
          <button
            type="button"
            className="vfit-btn-primary"
            style={{ height: '2.5rem', padding: '0 1rem', fontSize: '0.85rem', marginTop: 0 }}
            onClick={onStartTryOn}
          >
            PHÒNG THỬ ĐỒ 3D
          </button>
        )}
        <button
          type="button"
          onClick={logout}
          style={{
            background: 'none',
            border: '1px solid #c7c5d3',
            borderRadius: '0.75rem',
            padding: '0.5rem 0.85rem',
            color: '#e11d48',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          Đăng xuất
        </button>
      </div>
    </div>
  );
};
