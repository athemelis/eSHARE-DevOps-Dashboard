# Session Notes — 2026-02-10 1140

## Commits in this PR
- `a62c326` v161: Composite Feature Progress — roll up child bugs into Feature progress

## Summary
Internal bugs that are children of a Feature now roll up into the Feature's composite progress bar in the Releases dashboard, instead of appearing separately in the Internal Bugs table. This eliminates double-counting and gives accurate progress for "bug bash" Features.

## Changes Made

### New Helper Function
- `getInternalChildBugIdsOfFeatures()` — returns cached Set of internal bug IDs that are children of Features. Uses a Map-based lookup for performance. Cache invalidated on data refresh.

### Modified `calculateFeatureProgress()`
- After processing Delivery Slices, now also finds child Bugs via WorkItemLinks
- Runs `calculateBugProgress()` on each internal child Bug and merges estimates/actuals into Feature totals
- Returns new `childBugs` array in the result object (parallel to `deliverySlices`)

### Updated Progress Display
- `renderProgressCell()` tooltip now mentions child bug count when present
- `buildFeatureProgressPopupHTML()` includes a new "Child Bugs" section showing each bug with state, progress bar, and child tasks (styled with red "Bug · State" label)

### Internal Bug Filtering (4 locations)
- Releases table split — excluded from `internalBugs` array
- Releases chart data (`renderReleasesView`) — excluded from `releaseItems`
- Release Progress Summary (`renderReleaseProgressSummary`) — excluded from `baseItems`
- Capacity Planning dashboard — excluded from internal bugs list

## Decisions
- **Only internal bugs** (Product Quality, Technical & Infrastructure) are rolled into Feature progress. Customer Related child bugs remain in the Customer Bugs table.
- **Only Child relationships** count — Related bugs are discovered bugs linked for traceability, not planned work.
- Scope: 18 Features affected, 112 internal child bugs moved, 12 Customer Related child bugs unchanged.

## Analysis Performed
- Feature 4143 (Bug Fixes v1): 12 child bugs, 1 delivery slice — progress went from misleading 100% to accurate ~82%
- Feature 428 (PDF Editing v1): 4 child bugs, 23 delivery slices, 22 related bugs — related bugs correctly excluded
- Full dataset scan: 18 Features with child Bugs across 329 total Features

## Open Items
- None

## Next Steps
- Merge PR and sync branches
