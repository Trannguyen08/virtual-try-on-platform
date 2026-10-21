# Keep completed body-builder GLBs available after backend restart

## Role and goal

M3 backend asset delivery. Fix 404s for previously completed clothing GLBs when the frontend restores outfit layers after a backend reload.

## Files changed

- `backend/services/blender_body.py`, `BlenderBodyJobs.asset`: previously every asset request required the job record to remain in the process-local `_jobs` dictionary. Now a valid 32-character hexadecimal job ID can resolve to its completed GLB on disk even when the in-memory record is gone. If a job record still exists but is pending/running/failed, the endpoint continues to reject the asset. Invalid IDs and missing files return 404.
- `tests/unit/backend/test_mpfb_refit_jobs.py`: added `test_completed_asset_survives_job_memory_restart_tc_api_03`, covering a completed output served by a fresh job manager and rejection of an invalid ID.

## Root cause

`OutfitTryOnPage` restores body IDs and outfit result URLs from browser storage. Body GLBs are registered in persistent asset storage, but clothing GLB URLs use `/api/body-builder/assets/{job_id}.glb`. That route previously called `BlenderBodyJobs.get()`, which only sees process-local job state. After Uvicorn reload the job record disappears even if `data/outputs/blender_body/{job_id}.glb` remains on disk, so the saved outfit layer receives 404.

## Impact

- API path and URL shape are unchanged. The existing asset endpoint now serves a completed output across process restarts when its file remains in the managed Blender output directory.
- M3 changes only asset lookup behavior. M5's restored outfit layer can keep using its saved URL. No schema, units, database, or asset format changed.
- Access remains limited to generated files whose names match a 32-character lowercase hex job ID; arbitrary paths are rejected.
- No generated GLB or model weight was added to source control.

## Conflicts and risks

No code conflict was encountered. Files under `data/outputs/blender_body/` are local artifacts; if a GLB has been deleted, the old URL will still return 404 and the clothing item must be generated again.

## Verification

Not run, per repository execution rules. Regression case added under `TC-API-03`; backend startup and browser viewer have not been rechecked in this turn.

## Handoff

Restart/reload the backend and reopen the outfit page. If the original GLB still exists under `data/outputs/blender_body/`, the saved layer should load. Otherwise reapply that garment to create a new GLB. The user should run `pytest tests/unit/backend/test_mpfb_refit_jobs.py` and confirm the viewer after reload.
