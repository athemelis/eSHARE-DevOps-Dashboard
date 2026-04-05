# Session Notes — 2026-02-12 08:49 UTC

## Commits in this PR
- `fa8400e` v168: Estimate missing display shows ?% (Xd / ?d) format

## Changes Made

### Estimate Missing Display Consistency
**Problem:** Progress column displayed "Estimate missing" text for items with no original estimate, which was inconsistent with the normal format showing `52% (2.31d / 4.50d)`.
**Fix:** Changed to `?% (Xd / ?d)` format — shows actual logged days with `?` for unknown percentage and estimate, matching the normal progress display pattern.
- Updated both `renderProgressCell` (Releases dashboard) and `renderCapacityProgressCell` (Capacity dashboard)

## Decisions
- Used `?` character for unknown values rather than `N/A` or `—` for compactness in the progress cell

## Open Items
- None

## Next Steps
- Continue dashboard improvements as needed
