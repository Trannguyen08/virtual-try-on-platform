# Change impact — Allow body update through CORS

- **Date:** 2026-10-21 22:51 +07
- **Role:** M3 backend/API
- **Symptom:** Browser preflight `OPTIONS /api/body-builder/bodies/{body_id}` returned 400, so the frontend's `PUT` body update was blocked before reaching the endpoint.
- **Cause:** `CORSMiddleware` allowed `GET` and `POST` only.
- **Change:** Added `PUT` to the explicit CORS method allowlist in `backend/main.py`. Updated the run guide. The origin allowlist remains configured through `CORS_ORIGINS`.
- **Contract impact:** No payload, schema, database, unit, or coordinate changes. Existing explicit origin policy remains in force.
- **Verification:** No server restart or tests run. Restart the backend and retry body update from `http://localhost:5173`; expected preflight is HTTP 200 and the subsequent PUT reaches the API.

## Files changed

- `backend/main.py`
- `docs/development/run-backend-frontend.md`
- `.agents/memory/ACTIVE_CONTEXT.md`
