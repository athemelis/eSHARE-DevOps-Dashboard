# Session Notes - 2026-02-10 07:04 UTC

## Commits in this PR
- `14a7267` v159: Auto-update detection on auto-refresh, capacity deep linking fix, iteration crash fix

## Changes Made

### 1. Auto-Update Detection on Auto-Refresh
- During each 60-second auto-refresh cycle, the dashboard now fetches `dashboard-body.html` to check if a new version has been deployed
- If a newer version is detected, it silently updates the version badge in the header, re-fetches `changelog.js` for new entries, and shows the What's New popup
- No page reload, no flash, no loss of scroll position or navigation context
- Added `sinceVersion` parameter to `showWhatsNew()` to correctly filter changelog entries when triggered by auto-refresh (bypasses localStorage which may already have the current version stored)
- Exported `performAutoRefresh` to `window` for console testing

### 2. Capacity Planning Deep Linking Fix
- Added `updateUrlHash()` call at the end of `renderCapacityPlanningBoard()` so filter changes (Priority, Team, etc.) are reflected in the browser URL hash
- Previously, capacity filter changes did not update the URL, breaking deep linking for this dashboard

### 3. Capacity Planning Iteration Crash Fix (Pre-existing v158 Bug)
- Fixed `TypeError: iteration.match is not a function` crash when loading the Capacity dashboard with a URL hash containing an iteration parameter
- **Root cause:** `parseHashToState()` parses `iteration` as an array (it's in `arrayFields`), but `capacityFilters.iteration` expects a string
- **Fix:** Extract first element when applying hash state: `Array.isArray(hashState.iteration) ? hashState.iteration[0] : hashState.iteration`
- **Defensive:** Added `typeof iteration !== 'string'` guard in `parseIterationToDates()` in `capacity-planning-data.js`

### 4. Changelog Entry
- Added v159 entry to `changelog.js` with user-facing bullet points for the auto-update detection and capacity deep linking features

## Files Modified
| File | Changes |
|------|---------|
| `dashboard.js` | Auto-refresh version check, showWhatsNew sinceVersion param, capacity deep linking, iteration hash fix, performAutoRefresh export |
| `capacity-planning-data.js` | Defensive type check in parseIterationToDates |
| `changelog.js` | Added v159 entry |
| `dashboard.html` | Version bump to v159 |
| `dashboard-body.html` | Version bump to v159 |
| `CLAUDE.md` | Version bump to v159 |
| `DASHBOARD_README.md` | Version bump to v159 |

## Decisions
- Used silent in-place update (DOM manipulation + dynamic changelog fetch) instead of `location.reload()` to preserve the non-jarring auto-refresh behavior
- Version check fetches `dashboard-body.html` with cache-busting timestamp to detect deployed version
- Changelog is re-fetched via `new Function()` execution to update `window.DASHBOARD_CHANGELOG` without page reload

## Open Items
- None

## Next Steps
- Update DASHBOARD_README.md version history table entry for v159 (currently only has version bump, no history row)
- Update CLAUDE.md with v159 version summary
