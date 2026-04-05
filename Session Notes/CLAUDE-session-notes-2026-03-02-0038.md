# Session Notes - March 2, 2026

## Commits in this PR

- `cba9b26` — v198: Capacity warnings modal improvements - filter integration, sortable tables, collapsible sections, resizable

## Changes Made

### Capacity Warnings Modal - Filter Integration
- `computeCapacityWarnings()` now passes items through `applyCapacityFilters()` before scanning for inconsistencies
- Warnings badge count and modal contents respect all sticky header filters: Bug Owner, Assignee, Customer, Priority, State, Tag, Team

### Capacity Warnings Modal - Sortable Table Redesign
- Rewrote `showCapacityWarningsModal()` with 3 collapsible `<details>` sections:
  1. Committed but No Work Items in Iteration
  2. Missing Effort Estimates
  3. Work in Iteration but Not Committed
- Each section has a count badge and is collapsed by default
- Each section contains a sortable table with columns: ID, Type, Title, Priority, State, Owner, Assignee, Details, Action
- Sort state tracked per section via `cwSortSection()` handler

### Capacity Warnings Modal - Size & Resize
- Modal enlarged from 700px to 85vw wide × 80vh tall
- Modal is now user-resizable via CSS `resize: both`
- Body section uses `flex: 1; min-height: 0` for proper scroll behavior when resized

### CSS Updates
- Replaced card-based warning styles with table styles
- Added collapsible summary styles with count badges
- Updated modal dimensions and added resize support

## Decisions
- v198 is a separate version from v197 (which was already merged via PR #122)
- All remediation actions stay in-dashboard (no "Open in ADO" links) per user preference

## Open Items
- Continue testing remediation actions (add/remove committed iterations, set effort estimates)
- Consider additional warning scenarios beyond the current 6 (a-f)

## Next Steps
- User to test v198 changes in production after merge
- Potential future improvements: batch remediation actions, warning auto-dismiss after fix
