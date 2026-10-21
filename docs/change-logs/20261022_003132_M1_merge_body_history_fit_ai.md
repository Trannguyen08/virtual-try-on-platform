# Merge body, try-on history, and fit AI into integration

## Role and goal

Integration coordination, with `feature/body` given highest priority as requested. Merge the three source branches into `integration/tryon-body-garment-fit`, resolve conflicts, and restore try-on edits temporarily stashed when the user requested a branch switch.

## Merges

- `origin/feature/body` -> merge commit `c78f6dc` (`merge(body): integrate body feature into try-on integration`), merged first to preserve its highest priority.
- `origin/feature/frontend-tryon-history` -> merge commit `8ffb7c1` (`merge(frontend): integrate try-on history feature`). Conflicts in `frontend/src/api/bodyBuilderApi.ts`, `frontend/src/components/GarmentImageInputs.tsx`, and `frontend/src/pages/tryon/ImageTryOnPage.tsx` were resolved by keeping the body API contract, history/outfit upload flow, and distinct IDs for multiple image inputs.
- `origin/feature/fit-ai` -> merge commit `2798680` (`merge(fit-ai): integrate fit and AI features`), with no content conflicts.
- Merge order: body -> history -> fit-ai. The branch has not been pushed.

## Restored changes

The following edits were restored from stash `Codex WIP before switching to feature/body 2026-10-22`. The stash remains as a backup.

- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: changing an upper or lower garment image clears the old job/error and local job ID so stale results are not associated with the new image.
- `garment/reconstruction/mesh_builder.py`: detect cuff openings near sleeve ends using edge direction to reduce false openings along vertical seams.
- `garment/simulation/blender/compose_tryon.py`: preserve multi-garment composition; add shoulder lift, sleeve edge conformance to arm silhouette, and measurement-based width fitting before body projection. The scene report aggregates penetration/projection for the outfit and records maximum shoulder/sleeve adjustments.
- Restored three earlier logs in `docs/change-logs/` and `tests/unit/garment/test_mesh_openings.py` (two `TC-GAR-02` cases). Tests were not run in this turn.

## Contract and module impact

- M1: changes from `feature/body` are integrated; body-builder create/update behavior from the prioritized branch is retained.
- M2: composer accepts ordered garment metadata/meshes; internal measurements remain meters in Blender Y-up coordinates. The stash restoration did not change API schema.
- M3: history branch includes API/job/storage updates; body API keeps the prioritized create/update contract. Runtime compatibility has not been checked.
- M4: fit AI API, schemas, and UI from `feature/fit-ai` are integrated; model accuracy on real data was not evaluated.
- M5: outfit upload remains available with separate upper/lower garment types, and old jobs are cleared when images change. Display units are unchanged.
- The stash added no model weights or caches; the body merge includes product image assets in source commits.

## Conflicts and handling

- The history merge conflicted in body API, image inputs, and the try-on page; these were resolved in merge commit `8ffb7c1`.
- Stash restoration conflicted in `ImageTryOnPage.tsx` and `compose_tryon.py`; the outfit flow was combined with job reset, shoulder/sleeve conformance, and fit profile. `mesh_builder.py` applied cleanly.
- Potential integration risk: upstream body/API, garment metadata, and Blender report changes still need validation with builds and a real job.

## Verification

- `python -m py_compile garment/simulation/blender/compose_tryon.py`: passed.
- `git diff --cached --check`: passed with no whitespace errors.
- Pytest, frontend build, Blender job, and browser checks were not run in this turn.

## Handoff

Handoff branch: `integration/tryon-body-garment-fit`. Run backend/frontend checks and create upper-only, lower-only, and outfit jobs to validate the merged contracts. The restored edits are staged; three restored logs, this impact log, and one restored unit test are untracked. The backup stash remains available.
