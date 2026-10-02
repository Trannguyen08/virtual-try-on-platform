# Garment 3D standalone page

This additive entrypoint avoids changing the shared frontend router or app shell.

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://localhost:8000"
npm run dev
```

Open `http://localhost:5173/garment3d.html`.

Build only this isolated entrypoint with:

```powershell
npx vite build --config vite.garment3d.config.ts
```

When the shared router stabilizes, import `Garment3DPage` into it and keep this page as an isolated demo.
