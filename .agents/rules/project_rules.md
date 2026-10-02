# V-Fit 3D Virtual Try-On Platform — Project & Coding Rules

## Rule 1: Dual-Engine Architecture Hierarchy
- **Frontend (`/frontend`) is the primary driver.** The React TypeScript application controls UI state, user sessions, garment catalog, try-on history, and WebGL rendering.
- **Body Engine (`/body`) is an asynchronous worker.** Blender MPFB generates biometric human meshes on demand via FastAPI `POST /api/generate`.
- Never tightly couple the frontend to require a running Blender instance; always provide client-side fallback with static meshes in `frontend/public/models/`.

## Rule 2: Three.js & Asset Management
- Store all static `.glb` models inside `frontend/public/models/`.
- Access models via root-relative path (e.g., `/models/body_default.glb`).
- When loading models in Three.js, use `GLTFLoader` with automatic normalization:
  - Center bounding box around origin (0, 0).
  - Place bottom of bounding box at y = 0.
  - Scale model to standard avatar height (~1.95m in Three.js coordinates).
- Maintain an immediate procedural avatar fallback so the canvas never displays a blank or broken state during loading.

## Rule 3: Design Tokens & Luxury Haute Couture Aesthetic
- Use existing CSS variables defined in `frontend/src/styles/tokens.css` or `:root`:
  - `--vfit-primary`: Deep Royal Indigo (`#080a61`)
  - `--vfit-focus-ring`: Electric Blue (`#3d7eff`)
  - `--vfit-surface-card`: Clean elevated card (`#ffffff`)
  - `--vfit-surface-container-low`: Soft ivory/lavender (`#fbf8ff`)
  - `--vfit-radius-xl`: 1.25rem - 1.5rem
- Preserve the 13 designed screens and luxury boutique feel.

## Rule 4: API Client & Mocking Strategy
- All API methods in `frontend/src/api/` must handle network errors gracefully by falling back to high-fidelity client-side mocks with realistic delays (`setTimeout(..., 600)`).
- When the local FastAPI backend is active (`http://localhost:8000`), endpoints automatically consume live data.

## Rule 5: Testing & Production Build Check
- Prior to committing any code:
  - Run `cmd.exe /c "npm run build"` inside `frontend/`.
  - Confirm TypeScript compilation passes with zero errors.
  - Ensure `dist/` bundle generates cleanly.
