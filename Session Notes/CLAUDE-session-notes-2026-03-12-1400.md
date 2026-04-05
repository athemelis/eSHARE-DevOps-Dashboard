# Session Notes — 2026-03-12 14:00

## Version: v227

## Commits in this PR

1. **968cd21** — v227: Utilization fixes, multi-team support, Period filter in sticky header
2. **47ed4ef** — v227: Fix mugshots in Roadmap, Bugs, Releases, and Capacity dashboards
3. **402c424** — v227: Unified Modal enhancements — Cmd+K links, resizable desc/conv, priority badge, DS owner, Team column, scroll preservation
4. *(this commit)* — Session notes, updated changelog and version history

## Changes Made

### Commit 1: Utilization Fixes & Period Filter
- **Individual utilization formula fix**: Changed from `ownTeamDays / totalDaysLogged` (always 100% for single-team) to `daysLogged / businessDaysInPeriod`
- **Team utilization denominator fix**: Uses org chart roster size × business days (was double-counting leads)
- **External contributor detection**: Badge "↗ external (not included in util)" for cross-team contributors
- **Multi-team membership support**: Changed `memberToTeam` (single) to `memberToTeams` (array). `getEngineerTeams()` returns all teams. Handles leads managing multiple teams (e.g., Andreas Davros → UX Design + Frontend)
- **Task team detection**: Derives team from `areaPath.split('\\').pop()` instead of `task.team` (always 'None')
- **Task pill consistency**: Changed from separate #ID link + title to `📝 #ID: Title` as single clickable pill
- **Team filter dropdown display fix**: Now calls `updateGenericTeamDisplay('tasks')` when selection changes
- **Period selector moved to sticky header**: New `populatePeriodDropdown()` and `updatePeriodDisplay()` functions
- **Removed non-functional Aging filter**: Removed HTML + all JS references
- **Fixed Work Log Summary scroll cutoff**: Changed max-height from 3000px to 50000px

### Commit 2: Mugshot Fix
- **Root cause**: Custom `renderCell` handlers in Roadmap, Bugs, Releases, and Capacity returned plain text `<td>` for person columns, bypassing `buildAvatarHtml()` in the default renderer
- **Fix**: Removed 6 custom person column handlers, replaced with `return null` to fall through to default renderer. Added `bugOwner` to `singleEditMap` with `item.deliverySliceOwner` value mapping. Kept `team` handlers (they set `data-value` to `areaPath` for inline edit)

### Commit 3: Unified Modal Enhancements
- **Cmd/Ctrl+K link insertion**: `showInsertLinkDialog()` saves selection, shows inline popover with URL input. If text selected: uses selection as display text. Added to all 3 keydown listeners + 4 toolbar HTML locations + 4 toolbar click handlers
- **Resizable desc/conv divider**: Added `unified-modal-desc-resize-handle` element. `initDescResizeHandle()` adjusts description flex-basis dynamically
- **Effort badge**: Shows `⏱ X.Xd` purple badge for Delivery Slices with effort value in modal header subtitle
- **Priority badge**: Color-coded P1 (red), P2 (orange), P3 (yellow), P4 (gray) in modal header subtitle
- **DS Owner in header**: Added `Delivery Slice` case to owner section showing DS Owner + Assigned To with mugshots
- **Team column in relationships**: Added to `buildProgressRelationshipsSection()` (progress popup path), reordered Team before Iteration in all 3 table variants (delivery slices, relationships, progress popup relationships)
- **Relationships above Progress for Tasks**: Swapped render order in right pane
- **Set Release dropdown fix**: Removed `overflow: hidden` from `.unified-modal-title-section` (was clipping the absolutely-positioned dropdown). `overflow: hidden` already exists on `.unified-modal-title-left` for long title truncation
- **Scroll preservation on auto-refresh**: Save `window.scrollY` before `switchView(currentView)`, restore via `requestAnimationFrame` after re-render

## Technical Decisions

- **Multi-team approach**: Array-based `memberToTeams` rather than primary/secondary team model. Simple and extensible. Work counted for ALL teams the engineer belongs to
- **Task team from areaPath**: All Tasks have `task.team === 'None'` (string literal). AreaPath is the reliable source of team assignment
- **Mugshot fall-through pattern**: Custom `renderCell` returning `null` for person columns lets `buildGenericTable`'s default renderer handle them with `buildAvatarHtml()`. This DRY pattern avoids duplicating avatar logic in every dashboard
- **Scroll preservation**: Applied globally in `performAutoRefresh()` rather than per-view, since all views benefit. Validation view's existing specific handling still works (saves before, restores after)
- **Title section overflow**: Changed from `overflow: hidden` to no overflow on `.unified-modal-title-section`. Long title truncation still works via `.unified-modal-title-left` which retains `overflow: hidden`

## Files Changed
- `dashboard.js` — All JS changes across 3 commits
- `dashboard.css` — External badge, task pill, period dropdown, insert link dialog, desc resize handle, effort badge, priority badge styles
- `dashboard-body.html` — Version v227, period dropdown, desc-resize-handle element
- `dashboard.html` — Version bump (5 cache-busting params)
- `changelog.js` — v227 entry updated with full feature list
- `DASHBOARD_README.md` — Version bump, version history updated
- `CLAUDE.md` — Version bump
- `.github/copilot-instructions.md` — Version bump

## Open Items
- None

## Next Steps
- User to test and validate all changes
- Create PR for merge to main
