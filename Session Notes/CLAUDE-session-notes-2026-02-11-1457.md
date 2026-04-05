# Session Notes - 2026-02-11-1457

## Commits in this PR
- `7068f99` Add ADO audit and tag sync scripts
- `2939685` v164: Show unestimated teams in Progress by Team table

## Changes Made

### v164: Show unestimated teams in Progress by Team table
**Problem:** When a Bug's child tasks log work under a team (e.g., DevOps) but the bug has no estimation field set for that team (`devopsEstimation: None`), the team was missing from the "Progress by Team" table in the progress popup. The work WAS counted in the overall total but the team row didn't appear — making overall progress percentage wrong (e.g., Bug #4221 showed 81% instead of 131%).

**Root Cause:** `calculateBugProgress()` and `calculateFeatureProgress()` only included teams in `estimationByTeam` that had estimation values > 0. Teams with actual work logged (via child tasks) but no estimation were excluded from the team breakdown.

**Fix (4 locations in dashboard.js):**
1. `calculateBugProgress()` — merge teams from `actualByTeam` into `estimationByTeam` with value 0
2. `calculateFeatureProgress()` — same merge
3. Bug progress popup (`buildBugProgressPopupHTML`) — team rows show red bar with "No estimate" label for 0-estimate teams with actual work
4. Feature/capacity progress popup — same team row treatment + scoped data merge
5. Release Progress Summary "Progress by Team" table — "No estimate" in red instead of "N/A"
6. Updated `canSplitByTeam` to consider `actualByTeam` in addition to `estimationByTeam`

**Verified:** Bug #4221 now shows DevOps row (0.0d estimated / 1.0d actual / "No estimate") and correct 131% overall progress. Release dashboard Progress by Team table also correct.

### ADO audit and tag sync scripts (pre-existing commit)
- New standalone Python scripts in `ADO Python Scripts/` folder
- No dashboard code changes

## Decisions
- Show "No estimate" with red indicator (not "N/A") to clearly communicate missing estimation data
- Zero-value teams should always be visible to prevent hidden data inconsistencies

## Key Learning
Always show zero values in team breakdowns — by omitting a team's estimation (0d), we also hid their actual work, making overall progress percentages wrong.

## Open Items
- None

## Next Steps
- Update changelog.js entry for v164 with final description after PR merge
