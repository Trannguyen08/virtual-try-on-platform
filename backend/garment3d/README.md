# Garment Image-to-3D vertical slice

This package is intentionally isolated from the shared backend stubs to minimize merge conflicts.

## Run locally with the free mock provider

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r backend/garment3d/requirements.txt
$env:GARMENT3D_PROVIDER = "mock"
.venv\Scripts\python -m uvicorn backend.garment3d.app:app --reload --port 8000
```

Open `http://localhost:8000/docs`. The mock provider produces a deterministic GLB and never calls a paid service.

## Enable Tripo explicitly

Create an ignored `.env` file at the workspace root (next to `.gitignore`):

```dotenv
GARMENT3D_PROVIDER=tripo
TRIPO_API_KEY=tsk_your_secret_key
TRIPO_BASE_URL=https://openapi.tripo3d.ai/v3
GARMENT3D_MODEL_REVISION=v3.1-20260211
```

The backend loads this file automatically and treats it as the source of truth
for this standalone local module, so stale terminal variables cannot shadow it.

```powershell
.venv\Scripts\python -m uvicorn backend.garment3d.app:app --port 8000
```

## Optional Blender post-processing

Blender is disabled by default. To enable the headless bridge:

```powershell
$env:GARMENT3D_POSTPROCESSOR = "blender"
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
```

The default `passthrough` postprocessor keeps local setup minimal.

## Future integration

Once shared backend files are stable, the router can be included by the main application with:

```python
from backend.garment3d.router import router as garment3d_router

app.include_router(garment3d_router)
```

The standalone entrypoint remains useful for isolated tests and development.
