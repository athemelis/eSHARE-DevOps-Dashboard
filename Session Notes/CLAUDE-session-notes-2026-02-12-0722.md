# Session Notes — 2026-02-12 07:22 UTC

## Commits in this PR
- `624f365` v166: Progress popup estimation fix, total row, clear filter fix

## Changes Made

### 1. Feature Progress Popup — Estimation Source Fix
**Problem:** The Feature progress popup had THREE sections using TWO different estimation sources, causing confusing discrepancies:
- **Summary Estimates table** used `b.estimatedEffort` from `calculateBugProgress()` (task `originalEstimate` as primary)
- **Progress bar / Progress by Team** re-read bug-level estimation fields directly (the OLD source)
- **Individual bug cards** used `b.estimatedEffort` from `calculateBugProgress()` (task `originalEstimate` as primary)

**Example (Feature 4143):**
- Summary table showed 15.6d total estimated
- Progress section showed 15.00d estimated (from bug-level fields)
- Two mismatched bugs: #4100 (bug=2.5 vs task=2.6) and #4232 (bug=2.0 vs task=2.5)

**Fix:** 
- Added `estimationByTeam` and `actualByTeam` to `childBugDetails` in `calculateFeatureProgress()`
- Changed `buildFeatureProgressPopupHTML()` to use pre-calculated `b.estimationByTeam` and `b.actualByTeam` instead of re-reading bug-level fields
- All three sections now use the same estimation source (task `originalEstimate` with bug-level fallback)

### 2. Total Row in Progress by Team Table
- Added a **Total** row at the bottom of the Progress by Team table in both Bug and Feature progress popups
- Bold separator line, shows total estimated, total actual, and overall progress percentage

### 3. Warnings Clear Filter Button Fix
**Problem:** In Releases dashboard, clicking "✕ Clear Filter" in the blue filter indicator bar did nothing when the Warnings filter was active.
**Root Cause:** `clearReleaseTableFilter()` reset `releaseTableData.activeFilter` but did not reset `showOnlyWarnings` flag or `progressStatus` filter.
**Fix:** Added `showOnlyWarnings = false` and `progressStatus` reset to `clearReleaseTableFilter()`.

## Decisions
- The estimation source alignment means all popup sections now consistently use task `originalEstimate` (primary) with bug-level fields as fallback — matching the `calculateBugProgress()` logic established in v165.

## Open Items
- None

## Next Steps
- Continue work on dashboard improvements as needed
