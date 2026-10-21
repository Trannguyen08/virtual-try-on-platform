# Change impact — Full-width layout and UI cleanup

## Role and purpose

- **Role:** M5 frontend
- **Purpose:** Use the available viewport on every main page, improve consistent spacing, and remove technical/demo claims that distract or overstate current capabilities.

## Files and changes

- `frontend/src/App.tsx`: imports shared `layout.css` after route styles so page-frame rules are consistent.
- `frontend/src/styles/layout.css` (new): provides full-width route roots, responsive gutters, and consistent footer layout. Authentication forms and modal dialogs keep their usable content widths.
- `frontend/src/pages/catalog/CatalogPage.tsx`: adds full-width heading styles and keeps catalog status only when present; revises the product description to say it is a 3D preview.
- `frontend/src/pages/home/HomePage.tsx`: makes the closing call-to-action section full width and removes claims about avoiding wrong sizes or instant results.
- `frontend/src/components/home/HeroSection.tsx`: removes unsupported AI accuracy, usage, rating, and cloth-simulation overlays; replaces them with accurate workflow copy and an illustration label.
- `frontend/src/components/home/HowItWorksSection.tsx`: updates steps to match manual body setup, garment image upload, and static 3D preview.
- `frontend/src/components/common/Footer.tsx`: replaces unavailable feature/policy links and technical claims with a short product description and copyright.
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`: removes raw warning codes and internal penetration/simulation metrics from the result view; retains a short static-preview notice and a back-view estimate note when relevant.
- `frontend/src/pages/tryon/TryOnPage.tsx` and `frontend/src/components/tryon/InteractiveViewer3DStep.tsx`: identify legacy try-on roots for the shared full-width frame.

## Impact review

- **API/schema:** No changes.
- **Units and coordinate system:** No changes.
- **Database/assets:** No changes.
- **Modules:** M5 presentation only; no M1–M4 computation or contract changed.
- **Confirmed conflicts:** None found during source inspection.
- **Risks:** Existing feature implementation still uses a static preview. The UI now says so without exposing internal warning identifiers. Browser layout has not been visually checked at multiple breakpoints in this change.

## Tests and handoff

- **Tests/build:** Not run.
- **Next owner:** User to review routes at desktop and mobile widths in browser and share any visual issues for iteration.
- **Remaining:** Browser visual QA is pending; no automated visual evidence is available.

## Impacted files

- `frontend/src/App.tsx`
- `frontend/src/components/common/Footer.tsx`
- `frontend/src/components/home/HeroSection.tsx`
- `frontend/src/components/home/HowItWorksSection.tsx`
- `frontend/src/components/tryon/InteractiveViewer3DStep.tsx`
- `frontend/src/pages/catalog/CatalogPage.tsx`
- `frontend/src/pages/home/HomePage.tsx`
- `frontend/src/pages/tryon/ImageTryOnPage.tsx`
- `frontend/src/pages/tryon/TryOnPage.tsx`
- `frontend/src/styles/layout.css`
- `.agents/memory/ACTIVE_CONTEXT.md`
