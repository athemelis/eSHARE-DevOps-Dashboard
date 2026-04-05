# Session Notes - 2026-02-11 07:33

## Commits in this PR
- `77188ff` v163: Progress popup iteration & team scoping, child bug effort in capacity calculations

## Changes Made

### Progress Popup - Iteration & Team Scoping
- **Iteration-scoped popup**: When opened from the Capacity dashboard, the progress popup now scopes all data (progress bar, team breakdown, Delivery Slices, Child Bugs) to the selected iteration
- **Team filter applied**: When a Team filter is active in the Capacity dashboard, the popup filters to show only that team's effort, estimates, and child tasks
- **Iteration summary table**: New "📍 Summary Estimates Across ALL Iterations" table at the top of the Feature progress popup, with the current iteration column highlighted in cyan
- **Scope badge**: Clear visual indicator "📍 ALL items below are showing progress for: CY2026Q1-Feb | Team: Backend" showing active filters

### Child Bug Effort in Capacity Calculations
- **`getTeamEffortBreakdown()`**: Now includes child Bugs' team estimation fields (backendEstimation, qaEstimation, etc.) for Features, filtered to the selected iteration. Previously only counted Delivery Slice effort.
- This fixes the discrepancy where the capacity header bars and row displays showed different numbers than the progress popup

### Progress Popup Visual Enhancements
- **Emoji indicators**: 📋 for Delivery Slices, 🐛 for Bugs — consistent across both types
- **Team name**: Now shown for both Delivery Slices and Child Bugs (previously Bugs showed "Bug · State" instead of team)
- **State**: Now shown for both types (previously only Bugs showed state)
- **Assigned To column**: Added to child task tables in both Feature and Bug popups (shows display name only, email stripped)
- **State column**: Added to child task tables
- **Wider popup**: Default width increased from 900px to 1200px (max 90vw)
- **Resizable**: Popup can be resized by dragging the bottom-right corner (min 500px × 300px)

### Data Model Changes
- Added `state` field to Delivery Slice detail objects in `calculateFeatureProgress()`
- Added `team` field to child Bug detail objects in `calculateFeatureProgress()`
- Added `assignedTo` and `state` fields to task detail objects in both `calculateFeatureProgress()` and `calculateBugProgress()`

## Decisions
- Progress popup from Capacity dashboard shows iteration-scoped data; from Releases dashboard shows all data (no iteration context)
- Team filter applies to popup content (user chose this over "show all teams but highlight filtered one")
- The iteration summary table always shows ALL iterations regardless of filters, serving as context for the scoped data below

## Open Items
- None

## Next Steps
- Continue Capacity dashboard improvements as needed
