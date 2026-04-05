# Session Notes — 2026-02-28 0003

## Commits in this PR

1. **0496656** — `v197: Modal fixes — Progress by Team column order & release date display`
2. **79e9169** — `v197: Capacity planning consistency warnings with inline remediation`

## Changes Made

### Progress by Team Column Reorder
- Moved State column from position 2 to position 4 (between Actual and Progress) in all 4 "Progress by Team" tables:
  - Capacity dashboard inline table (line ~10310)
  - Bug progress modal (line ~21527)
  - Feature progress modal (line ~21868)
  - Headers and total rows updated to match

### Release Date Timezone Fix
- Fixed `renderModalMeta()` (line 9951) using `new Date(targetDt)` which parsed date-only strings as UTC midnight, causing a 1-day offset in US timezones
- Changed to use existing `parseLocalDate()` helper which appends `T00:00:00` for local-time parsing

### Capacity Planning Consistency Warnings (New Feature)
- **`computeCapacityWarnings()`** — Scans ALL Features/Bugs (unfiltered) against the selected iteration for 6 inconsistency scenarios:
  - (a) Feature committed, no Delivery Slices in iteration
  - (b) Feature committed, Delivery Slices with 0 effort
  - (c) Bug committed, no Tasks in iteration
  - (d) Bug committed, Tasks with 0 originalEstimate
  - (e) Feature has Delivery Slices in iteration but not committed
  - (f) Bug has Tasks in iteration but not committed
- **Warning badge** — Amber `⚠️ N` badge next to "Committed Work Plan" h3 header in dashboard-body.html
- **Warnings modal** — Click badge to see grouped issues with per-item remediation:
  - "Committed but No Work Items in Iteration" (a, c) → Remove from Committed button
  - "Missing Effort Estimates" (b, d) → Inline effort input per child item with Save button
  - "Work in Iteration but Not Committed" (e, f) → Add to Committed button
- **All remediation actions write directly to ADO** via existing `patchItemField()`:
  - `Custom.CommittedIterations` for add/remove committed
  - `Microsoft.VSTS.Scheduling.Effort` for Delivery Slice effort
  - `Microsoft.VSTS.Scheduling.OriginalEstimate` for Task estimates
- Runs on every board render (including auto-refresh)
- CSS styles in dashboard.css (~170 lines)

## Decisions
- All remediation stays in-dashboard (no "Open in ADO" links) per user principle
- Bug effort uses Task `originalEstimate` (not Bug-level team estimation fields — those are legacy)
- Warnings scan unfiltered items to surface hidden issues regardless of active filters

## Open Items / Testing Needed
- ⚠️ **Release date fix**: Verify 📅 shows "Apr 4, 2026" (not "Apr 3") for 202604.0.0 release in production
- ⚠️ **Warnings modal**: User saw ADO_BASE error on first attempt (fixed in commit 2), needs end-to-end verification
- ⚠️ **Remediation actions**: Not yet tested (add/remove committed, save effort inline)

## Next Steps
- Test all 6 warning scenarios and remediation actions
- Consider additional UX polish based on testing feedback
