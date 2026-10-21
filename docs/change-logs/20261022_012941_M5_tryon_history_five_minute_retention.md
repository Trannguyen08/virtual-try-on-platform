# M5 Change Impact Log — Complete recent try-on history

- Time: 2026-10-22 01:29 Asia/Saigon
- Role: M5, frontend and 3D web viewer
- Purpose: Show completed results from the current try-on flow and retain history for five minutes, as requested.

## Files changed

- `frontend/src/pages/tryon/OutfitTryOnPage.tsx`: After each selected garment finishes successfully, saves a separate history entry with product/category, source, timestamp, simulation state, preview reference image when it is a catalog product, and the real result asset URL. Does not persist user-uploaded image bytes or invent fit metrics.
- `frontend/src/services/historyStorage.ts`: Changed history storage from localStorage to sessionStorage, removes the legacy persistent history key, set a five-minute TTL, prune expired records on reads, and schedule cleanup. Empty or unreadable storage now returns an empty list instead of demo records.
- `frontend/src/data/mockHistory.ts`: Extended the history type for actual result URLs and optional fit/cart/image metadata; legacy entries remain structurally supported.
- `frontend/src/pages/history/HistoryPage.tsx`: Refreshes storage while open, filters by search/category/day/week/month/result type, distinguishes no history from no filter matches, supports deleting one or all entries, and opens saved 3D output in the existing interactive viewer.
- `frontend/src/components/history/HistoryCard.tsx`: Displays actual garment metadata, simulation/preview state, links to view or download the result asset, and honest fit limitations; omits comparison and fake score claims.
- `frontend/src/components/history/HistoryStatsBar.tsx`: Replaced unsupported average fit/cart counters with counts for total, simulated, and preview results; shows the five-minute retention period.
- `frontend/src/components/history/HistoryToolbar.tsx`: Replaced fit-score options with simulation/preview filters and corrected the month label.
- `frontend/src/components/history/CompareModal.tsx`: Kept optional legacy metadata safe to read after history fields became optional.
- `frontend/src/styles/history.css`: Added styling for clear-history action, result state badges, reference image label, and no-image placeholder.
- `frontend/src/App.tsx`: Added safe fallback values for optional historical price/image/color fields when opening older history entries.

## Impact and ownership

- M5 owns these frontend changes. They use the existing `imageTryOnApi` / body-builder result URLs and do not change any request or response contract.
- No backend, database, schema, units, or asset pipeline changed.
- History metadata is scoped to the current browser tab’s session and expires after five minutes. The backend-generated GLB files follow the backend’s existing cleanup policy; this frontend TTL does not delete those files.
- Uploaded personal images are not serialized to browser storage. Catalog image URLs may be stored as references. The displayed fit score was removed for current results because the active try-on result does not provide a fit score.

## Conflicts and risks

- No confirmed conflict. Older records from localStorage will not be imported into the new session-only history.
- Asset links may stop working if the backend removes an output earlier than the five-minute client history TTL.
- The result view is offered as a downloadable 3D file; no new embedded history viewer was added.

## Verification

- No build or tests were run under the project’s common Rule 01 restrictions.
- Manual acceptance: complete catalog and uploaded-image tries, confirm each finished item appears, check simulation/preview labels and filters, delete an item and all items, and verify entries expire after five minutes while the page remains open.
- Frontend build command for user-run verification: `cd frontend; npm run build`.

## Handoff

- History is temporary per browser tab and is not account-synced. If the user expects cross-device history or backend deletion of result files at five minutes, that requires a separate backend change and approval.
