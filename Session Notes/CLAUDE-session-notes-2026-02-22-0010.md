# Session Notes - 2026-02-22 0010

## Commits in this PR
- `922fd91` v177: Live ADO Sync & Consistency Repair

## Changes Made

### Live ADO Sync for Cascading Lists
Changed the data source for cascading lists from SharePoint (stale manual export) to the ADO Extension Management API as the single source of truth.

**dashboard-loader.js** — `loadCascadingLists()` updated:
- Production: ADO Extension Management API (primary) → SharePoint (fallback)
- Localhost: local file (unchanged)

**dashboard.js** — Auto-refresh integration + consistency check:
- `refreshCascadingLists()` runs every 60s during auto-refresh (non-blocking, fire-and-forget)
- JSON comparison skips re-render if data unchanged
- Write-through: updates SharePoint cache in background when ADO data changes
- If modal is open with no pending edits, re-renders with fresh data

### Bidirectional Consistency Check & Repair
- `checkCascadingConsistency()` validates Version→Date and Date→Version mappings match
- ⚠️ warning badge appears on "📅 Versions" links across all 8 dashboards when issues detected
- `renderConsistencyWarning()` shows details inside modal with "Fix Inconsistencies" link
- `repairCascadingConsistency()` auto-adds missing reverse mappings, saves to ADO + SharePoint

## Decisions
- ADO is single source of truth — eliminates stale data from manual SharePoint exports
- SharePoint kept as fallback cache (updated via write-through) for resilience
- Consistency check runs on every load and every 60s refresh
- Repair is user-initiated (not automatic) to avoid silent data modifications
- Localhost blocks repair (no auth) but allows viewing

## Context
- Discovered that `202602.1.1` entry existed in ADO but not in SharePoint file
- Root cause: no automated sync from ADO → SharePoint existed
- This change eliminates the sync gap entirely

## Open Items
- Test full flow on production with MSAL authentication
- Verify ADO Extension Management API permissions work with user_impersonation scope
- Monitor SharePoint write-through for any permission issues
