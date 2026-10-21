# M5 Change Impact Log — Frontend typography, width, and user-facing copy

- Time: 2026-10-22 00:52 Asia/Saigon
- Role: M5, frontend and 3D web viewer
- Purpose: Improve readability with Inter and larger small text, make page shells fill the viewport, and reduce implementation terminology shown to users while preserving capability limits.

## Files changed

- `frontend/src/styles/layout.css`: Applied Inter to the global page and form controls, set a 16px base size, removed width caps from the outfit shell, body setup, and try-on stepper, added responsive gutters, and increased small outfit labels/buttons/notes.
- `frontend/src/styles/auth.css`: Changed the shared auth font token from Bricolage Grotesque-first to Inter-first.
- `frontend/src/pages/tryon/OutfitTryOnPage.tsx`: Replaced user-facing “backend”, “worker”, “model”, “Blender”, “job”, and “server” language with plain status text while retaining progress/resume actions.
- `frontend/src/pages/tryon/TryOnPage.tsx`: Replaced Blender/MPFB progress and step labels with user-facing body-model and preview wording.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: Rewrote image try-on error messages to remove mesh, GLB, MPFB, Blender, and body-processing jargon while keeping recovery guidance.
- `frontend/src/components/tryon/BodyBuilderStep.tsx`: Removed Blender/MPFB product terminology from visible preset, explanation, and CTA text; retained the explanation that body proportions are not verified from a photo.
- `frontend/src/components/tryon/GeneratedBodyViewer.tsx`: Replaced exposed Blender/MPFB/GLB/MHCLO terms in visible title, status, and explanatory text. Kept accurate caveats that the uploaded photo is not used to build the body and that the preview does not verify fit.
- `frontend/src/components/GarmentGenerationProgress.tsx`: Replaced visible mesh/GLB/texture status terms with plain progress descriptions.
- `frontend/src/viewer/Garment360Viewer.tsx`: Replaced “body mesh” in user-facing copy with “mẫu cơ thể”.

## Impact and ownership

- M5 owns the affected frontend components and styles. No API, schema, units, database, or asset contracts changed.
- No cross-module dependency change was made. Backend/worker status values remain internal inputs; only displayed labels changed.
- Width expansion affects route-level layout and responsive gutters. The authentication card and focused dialogs remain purpose-sized components inside full-width pages.

## Conflicts and risks

- No confirmed conflict. Risk: other components may still show technical wording or locally override font sizes; a visual review of every route is still needed.
- Fonts are already loaded by the frontend entry HTML; no font dependency or network behavior changed.

## Verification

- No build, test, or browser run was performed under the project’s common Rule 01 restrictions.
- Visual checks remain: home, catalog, try-on, garment creation, history, login/register, plus narrow mobile widths.

## Handoff

- Review all main routes in the browser, especially the outfit viewer and narrow screens. Search remaining visible copy for internal terms if any still appear.
