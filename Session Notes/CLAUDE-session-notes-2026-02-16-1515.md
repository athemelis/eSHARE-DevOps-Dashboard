# Session Notes - 2026-02-16

## Session Summary
Bug fixes and UI improvements for v174.

## Commits in this PR

### 1. `d145bc0` - v174: Skip estimate warning for Done/Closed Delivery Slices
**Problem:** Feature 4456 showed "1 child task missing original estimate" warning in the Progress popup. The Feature has 14 Delivery Slices — estimates are input at the DS `effort` level, not at the child Task `originalEstimate` level. The warning was triggered by a Closed DS (3557) with `effort=0` that had 1 child task.

**Fix:** In `detectStateInconsistency()` Rule 6 (missing estimates), skip Delivery Slices in terminal states (Done/Closed) when checking for missing effort. A DS with `effort=0` that's already Done or Closed is expected (cancelled/descoped). The Bug path (checks `originalEstimate` on child tasks) remains unchanged.

**Files changed:** `dashboard.js`

### 2. `3aaf93f` - v174: Always-visible resize handles with Chromium/Edge macOS hover workaround
**Problem:** Table column resize handles disappeared after the first resize in Edge on macOS. Root cause: a known Chromium engine bug (#324852539, #40124438) where CSS `:hover` state gets stuck after drag operations on macOS. The bug only affects Edge on macOS — Safari, Chrome, and Edge on Windows all work fine.

**Fix (3 parts):**
1. **Always-visible resize handles** — Changed resize handle background from `transparent` to a subtle gray (`rgba(100, 100, 100, 0.15)`) so handles are always visible regardless of hover state
2. **JS-managed hover class** — Added `mouseenter`/`mouseleave` listeners that toggle a `.hover` class as a fallback to CSS `:hover`. Both selectors are active so whichever works will highlight blue
3. **Cursor state reset** — After each resize, forces `document.body.style.cursor` reset via `requestAnimationFrame` to nudge Chromium into recalculating cursor state

**Additional improvements:**
- Removed `min-width` from inline styles during resize (caused layout rigidity; matches the customers table implementation)
- Added defensive cleanup at resize start to handle stale state from incomplete drags
- Added `overflow: visible` on `th` elements to prevent clipping of absolute-positioned handles

**Files changed:** `dashboard.css`, `dashboard.js`

## Decisions
- The Chromium hover bug workaround makes resize handles always subtly visible. When the bug is fixed in Edge Stable 133+, the `:hover` highlight will also work, providing both always-visible + hover feedback.
- Estimate warning for DSes only fires for active (non-terminal) Delivery Slices. Bug child tasks still check `originalEstimate` individually.

## Open Items
- None

## Next Steps
- Continue with next feature/fix requests
