# Session Notes — 2026-03-13 (afternoon)

## Version: v229

## Commits in this PR (2 commits, tony-dev → main)

1. `c69d29c` — Include Staff team in Tasks utilization — fixes assignee→team inference for Staff members
2. `f9e11c7` — Customers Insights — relationship and consistency warnings for ERs and Customer Bugs

## Changes Made

### Staff Team Utilization Fix
- Removed "Staff" from the exclusion filter in `computeTeamUtilizationData()` (line 28903) and team summary (line 30254)
- Previously `if (team === 'eShare' || team === 'Staff') return;` skipped Staff — now only skips eShare
- Allows Staff members (e.g., Andreas Porevopoulos) to show Team Utilization Breakdown and Individual Breakdown when filtered by Assigned To

### Customers Relationship Insights
- Added 4 new clickable insight links to the Customers Dashboard Insights section:
  1. ERs with no associated Feature
  2. ERs inconsistent with their associated Feature (Release Version, Target Date, or terminal state mismatch)
  3. Customer Bugs with no associated Bug
  4. Customer Bugs inconsistent with their associated Bug (same consistency checks)
- Added `insightItemIds` field to `customersFilters` (Set of item IDs, transient — not persisted to localStorage)
- Added `filterCustomersByInsight()` function + window export
- Insight filter cleared when clicking state/category insights or Clear All
- `hasActiveCustomersFilters()` and `clearAllCustomersFilters()` updated to include new filter
- State restore resets `insightItemIds` to null (can't serialize a Set)

## Decisions
- Staff team included unconditionally (not just for inference) — it's a real team with 7 members
- Inconsistency check uses terminal state grouping (Done/Closed/Removed vs active) rather than exact state match
- Insight links only shown when count > 0 (no zero-count clutter)

## Open Items
- None

## Next Steps
- Merge PR, sync branches
