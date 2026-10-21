# M3: Start and validate the local backend

- Time: 2026-10-18 16:49:42, Asia/Bangkok (UTC+7).
- User explicitly authorized running services, migrations, tests and fixing backend errors.
- Skills used: m3-backend-expert, change-impact-log.

## Changes

- `.env` (ignored local config): changed DATABASE_URL host from localhost to 127.0.0.1, retaining the remaining connection fields. Direct IPv4 connection succeeded while localhost migration stalled.
- `backend/garment3d/settings.py`: `from_environment` previously called load_dotenv with override=True, modifying process-wide environment values including DATABASE_URL. It now combines os.environ and dotenv_values in a local dictionary. Garment settings retain .env precedence without changing other modules' environment. `_integer` reads from this same dictionary.
- Started the existing PostgreSQL Docker Compose service, created its development volume and applied migration 20261018_0001. Started Uvicorn on 127.0.0.1:8000 in the background.
- Runtime logs/PID: data/outputs/backend-runtime/ (ignored).

## Impact and owners

M3 database startup and configuration isolation changed; M2 Garment 3D settings retain their prior .env precedence. No API schema, unit, mesh axis or frontend behavior was changed. PostgreSQL contains development fixture assets and a synthetic smoke-test body/job. No model weights or datasets added. The two pre-existing local M1 edits were preserved. M3 owns follow-up; M1/M2/M5 should validate real Blender/viewer behavior separately.

## Evidence

- docker compose up -d --wait --wait-timeout 60 postgres: healthy, 127.0.0.1:5432.
- pip check: No broken requirements found.
- Dependency imports: fastapi, sqlalchemy, alembic, psycopg, pytest, cv2, trimesh succeeded.
- Alembic upgrade/current with .env loaded: 20261018_0001 (head).
- Initial backend suite: 59 passed, 1 failed in test_job_state_transitions_tc_api_03. Root cause: Garment settings replaced the test database URL during application restart.
- Final suite, with .env loaded before pytest: tests/unit/backend/, tests/e2e/mock/, tests/integration/garment_3d/, excluding slow/gpu: 60 passed, 1 Starlette/httpx deprecation warning, 15.99 seconds.
- ruff check backend --select E9,F63,F7,F82: All checks passed.
- HTTP /health, /garment3d/health, /api/garments, /docs: 200.
- Live PostgreSQL-backed HTTP smoke: catalog -> analyze -> fit -> completed job -> valid GLB download: PASS. Job: job_4f6751464aa64affb3abace75af37db0. Core try-on uses mock data by design.
- Blender executable discovery succeeded; real body generation/MPFB execution and frontend viewer were not tested.

## Handoff

Backend is left running at http://127.0.0.1:8000; Swagger at /docs. PostgreSQL is left running in Docker. Code/config fixes are local and uncommitted. No push performed. A successful backend smoke test does not establish real AI inference or physical cloth simulation.
