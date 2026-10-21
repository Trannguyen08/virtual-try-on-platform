# M5 Change Impact Log — Fix external garment try-on argument shape

- Time: 2026-10-22 01:00 Asia/Saigon
- Role: M5, frontend and 3D web viewer
- Purpose: Fix the `garments.map is not a function` runtime error when applying a garment selected through “Ảnh sản phẩm ngoài”.

## Files changed

- `frontend/src/pages/tryon/OutfitTryOnPage.tsx`, `apply()`: Before, this caller passed a file object as the second argument and then passed garment type, length, and abort signal in additional positions. `imageTryOnApi.create()` expects the second argument to be `OutfitGarmentUpload[]`, so the API attempted `.map()` on the file object. After, the caller wraps one garment in a one-element array with the matching `upper`, `lower`, or `onepiece` slot, garment type, reference length, automatic fit mode, zero ease, and front/back files.

## Impact and ownership

- M5 owns the changed page. This aligns its caller with the existing `imageTryOnApi.create()` contract.
- No endpoint, request schema, response schema, database, units, or assets changed. The existing `ImageTryOnPage` caller continues to pass its array as before.
- Backend owner M3 is not affected.

## Conflicts and risks

- No confirmed conflict. External garment upload is still limited to one item per request in this UI flow; outfit application processes selected items sequentially.
- Garment type is narrowed to the non-`auto` type at the request boundary because the API requires a concrete category; the UI’s external type choices are concrete categories.

## Verification

- No build, browser run, or test was performed under the project’s common Rule 01 restrictions.
- User should verify by selecting “Ảnh sản phẩm ngoài”, uploading a front image, and applying it; test back image as an optional input.

## Handoff

- If another error appears during upload or job processing, capture the browser console and API response to distinguish client serialization from server-side validation.
