# Session Notes - 2026-02-12 12:58

## Commits in this PR
- `afbf562` v170: Fix DS estimate handling - check DS effort not task originalEstimate, remove misleading per-task estimate column

## Changes Made

### DS Estimate Fixes (v170)
Two fixes for how Delivery Slice child tasks handle estimates in the progress popup and warning system:

1. **Warning Rule 6 — DS estimate source fix:**
   - Previously checked `task.originalEstimate` on individual DS child tasks, but for Delivery Slices the estimate lives on the DS itself (`slice.effort`), not on individual tasks
   - Now checks `s.effort` on the DS level — only flags missing estimate if the DS has no effort value
   - Bug child tasks still correctly check `task.originalEstimate` (estimate lives on the task for bugs)

2. **Removed per-task Estimate column from DS task tables:**
   - Showing the DS-level effort on every task row was misleading (e.g., 3 tasks each showing "5.00d" looked like 15d total when it was actually 5d)
   - Removed the Estimate column from DS child task tables entirely
   - The DS effort is already shown once in the DS header line ("Est: 5.00d")
   - Bug child task tables retain their "Orig. Est." column since estimates are per-task

### Key Design Principle
- **Delivery Slice child tasks**: Estimate at DS level (`slice.effort`)
- **Bug child tasks**: Estimate at task level (`task.originalEstimate`)

## Decisions
- Removing the column entirely is cleaner than showing a shared DS estimate per row, which created confusion about totals

## Open Items
None

## Next Steps
- Continue iterating on dashboard features as needed
