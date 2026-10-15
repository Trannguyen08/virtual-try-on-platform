# Garment 3D standalone page

This additive entrypoint avoids changing the shared frontend router or app shell.

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_GARMENT3D_API_URL = "http://localhost:8001"
npm run dev
```

Open `http://localhost:5173/garment3d.html`.

Run the existing backend on port 8000 and the garment service on port 8001
with `python -m uvicorn backend.garment3d.app:app --port 8001`. If only the
garment service is running on port 8000, `VITE_GARMENT3D_API_URL` may be omitted.

The form asks for garment type and an optional real garment length. Supplying
the length enables centimetre measurements and marks the result as ready for
body-size integration. Completed results expose both the GLB and its body-ready
metadata JSON for download.

Build the existing application and this page together with:

```powershell
npm run build
```

When the shared router stabilizes, import `Garment3DPage` into it and keep this page as an isolated demo.
