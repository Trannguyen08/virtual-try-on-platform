import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { UploadPage } from './pages/UploadPage';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Missing application root element');
}

createRoot(rootElement).render(
  <StrictMode>
    <UploadPage />
  </StrictMode>,
);
