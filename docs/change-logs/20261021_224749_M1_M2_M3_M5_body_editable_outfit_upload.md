# Change impact — Editable body and multi-garment image try-on

- **Date:** 2026-10-21 22:47 +07
- **Roles:** M1 body measurements, M2 garment composition, M3 API/worker/storage, M5 try-on UI
- **Request:** Edit an existing generated body; enter physical dimensions in centimeters; upload required front and optional back garment images; compose an upper and lower garment in one outfit.

## Changes

- Added `measurements_cm` to body-builder parameters and mapped shoulder width, chest, waist, hip, and inseam values to approximate MPFB proportions. Added `PUT /api/body-builder/bodies/{body_id}` to rebuild the existing body asset and native scene under the same body ID. `GET` returns saved parameters for editing.
- Extended image try-on requests with up to two typed garment slots and per-garment front/back image inputs. The front view is required for each item; back is optional. The prior single-garment request path remains supported for existing clients and stored jobs.
- Updated the worker and Blender composer to reconstruct garments separately and publish one combined static scene. Updated the frontend to edit a body in place and configure an optional lower garment alongside an upper garment. The try-on upload UI shows front/back only.
- Updated the API contract and TypeScript result type for per-garment reconstruction metadata.

## Contracts and compatibility

- Measurements remain external centimeters; GLB geometry remains meters, right-handed Y-up, +Z forward.
- Body measurements are manual inputs used as approximate MPFB morph controls. They are not measurements estimated or verified from a person image.
- Image try-on accepts `garments_json` and indexed `garment_{index}_front/back` fields. At most two items are accepted; duplicate slots and one-piece combinations are rejected.
- Legacy single-garment multipart clients remain accepted. No database migration is required; job request and result JSON gain fields while retaining legacy single-garment fields.

## Limitations and verification

- Garment placement is static. Cloth simulation, fit scoring, and verified physical fit are not provided.
- No automated tests or Blender execution were run in this change; repository guidance reserves test execution for the user. Source references and request/result shapes were inspected with read-only searches.
- End-to-end acceptance still requires a configured Blender/MPFB environment and a body update plus a two-garment job.

## Files changed

- `backend/api/body_builder.py`
- `backend/api/image_tryon.py`
- `backend/db/repository.py`
- `backend/schemas/image_tryon.py`
- `backend/services/blender_body.py`
- `backend/services/image_tryon.py`
- `backend/services/storage.py`
- `backend/workers/image_tryon.py`
- `body/estimation/blender_body.py`
- `garment/simulation/blender/compose_tryon.py`
- `frontend/src/api/bodyBuilderApi.ts`
- `frontend/src/api/imageTryOnApi.ts`
- `frontend/src/components/GarmentImageInputs.tsx`
- `frontend/src/components/tryon/BodyBuilderStep.tsx`
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`
- `docs/api/api-contract.md`
- `.agents/memory/ACTIVE_CONTEXT.md`
