import React from 'react';
import ReactDOM from 'react-dom/client';
import { Garment3DPage } from './pages/Garment3DPage';
import './styles/garment3d.css';

const root = document.getElementById('garment3d-root');
if (!root) throw new Error('Missing #garment3d-root');

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <Garment3DPage />
  </React.StrictMode>,
);
