# Session Notes - March 5, 2026 (23:40)

## Commits in this PR

1. **3afd440** - v214: Fix capacity bug effort to use Task iteration instead of Bug iteration
2. **7e9bddf** - v214: Allow filter row to wrap on narrow screens

## Changes Made

### Capacity Dashboard - Bug Effort Calculation Fix
- **Problem:** `getTeamEffortBreakdown()` for Feature→Bug path used Bug-level estimation fields (e.g., `backendEstimation`) filtered by the Bug's own iteration. Since these fields are flat (not per-iteration), bugs in one iteration with tasks in another were invisible to capacity planning.
- **Root Cause:** A Bug in February with `backendEstimation: 3.0` and a Backend task in March would not contribute to March capacity — the Bug was excluded by its own iteration path.
- **Fix:** Changed the Feature→Bug path to use the same Task-based approach as standalone Bugs — finds grandchild Tasks filtered by Task iteration, sums `originalEstimate` grouped by team (from Task's `areaPath`).
- **Impact:** 6 Features affected in March alone. Net shift: +18d Backend, +20.8d QA, -6.6d Frontend (task estimates differ from bug-level estimates).

### Filter Row Responsive Wrap
- **Problem:** The sticky filter header with generic filter dropdowns overflowed on narrow screens.
- **Fix:** Changed `.filter-row` from `flex-wrap: nowrap` to `flex-wrap: wrap` so filters flow to a second line instead of overflowing.

## Decisions
- Bug-level estimation fields (`backendEstimation`, `qaEstimation`, etc.) are still loaded and used as fallbacks in the Progress Detail Popup and as diagnostic indicators ("No tasks" warning), but are no longer used for iteration-level capacity calculations.

## Files Modified
- `dashboard.js` — `getTeamEffortBreakdown()` Feature→Bug path rewritten
- `dashboard.css` — `.filter-row` flex-wrap changed to wrap
- `dashboard.html` — Version bump to v214
- `dashboard-body.html` — Version display v214
- `changelog.js` — Added v214 entry
- `CLAUDE.md` — Version v214
- `.github/copilot-instructions.md` — Version v214
- `DASHBOARD_README.md` — Version v214, added version history entry

## Open Items / Next Steps
- Table-Columns.md not yet updated for combined Release column (from v212)
- Notification sort state not persisted across refreshes
- `capacity-planning-data.js` still has `getBugEffort()` using bug-level estimation fields — may want to align with new Task-based approach
