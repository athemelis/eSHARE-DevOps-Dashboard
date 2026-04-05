# Session Notes — 2026-02-26

## Version: v192

## Commits in this PR
- `7bbe74e` v192: Fix column width persistence across page refreshes

## Changes Made

### Column Width Persistence Fix
**Problem:** After resizing table columns, the custom widths would not persist across page refreshes. Columns reverted to their CSS default widths every time.

**Root Cause:** `saveAllTableScrollPositions()` is called at the top of `switchView()` before re-rendering. It iterates ALL `.generic-table-section` elements in the DOM — including tables on hidden views (`display: none`). For hidden elements, `th.offsetWidth` returns `0`. These zero values overwrote the previously-saved column widths in the module-level objects (e.g., `roadmapColumnWidths`). When `saveStateToStorage()` then persisted to localStorage, widths were saved as `0`. On the next page load, `columnWidths[col.key]` was `0` (falsy), so no inline `style="width"` was applied, causing columns to fall back to CSS class defaults.

**Fix:** Added a visibility check (`section.offsetParent !== null`) in `saveAllTableScrollPositions()` to skip width capture for hidden tables. Only visible tables have their `offsetWidth` read from the DOM. Scroll position capture is unaffected (still works for all tables).

**File changed:** `dashboard.js` — `saveAllTableScrollPositions()` function (~line 8771)

## Decisions
- Used `offsetParent !== null` as the visibility check — this is the standard way to detect `display: none` ancestors in the DOM
- Scroll position capture intentionally NOT gated by visibility — scroll positions are simple numeric values that don't depend on layout

## Open Items
- None

## Next Steps
- Test column width persistence across view switches, auto-refresh, and manual refresh
- Verify widths persist correctly when returning to a previously-visited view
