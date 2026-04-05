# Session Notes — 2026-02-26 1810

## Commits in this PR
- `9465eda` — v194: Capacity Dashboard bulk commit by release

## Changes Made

### Capacity Dashboard — Bulk Commit by Release (v194)
Added a "Commit by Release" button in the Backlog Work Candidates column header that allows bulk-committing items based on their release version.

**Files changed:**
- `dashboard-body.html` — Added button + dropdown HTML in the Backlog Work Candidates column header
- `dashboard.css` — Styles for bulk commit button, dropdown, checkbox list, and action button
- `dashboard.js` — 5 new functions:
  - `toggleBulkCommitDropdown()` — show/hide with outside-click-to-close
  - `populateBulkCommitReleases()` — scans backlog candidates, groups by release version
  - `handleBulkCommitReleaseToggle()` — checkbox toggle handler
  - `updateBulkCommitButton()` — updates "Commit X items →" label dynamically
  - `executeBulkCommit()` — bulk-commits all matching items with single re-render
- `changelog.js` — Added v194 changelog entry
- `DASHBOARD_README.md` — Added v194 version history entry
- Version bumped in: `dashboard.html`, `dashboard-body.html`, `CLAUDE.md`, `DASHBOARD_README.md`, `.github/copilot-instructions.md`

**How it works:**
1. User clicks "Commit by Release ▾" in the Backlog column header
2. Dropdown shows release versions with item counts (only releases present in current backlog candidates)
3. User checks one or more releases
4. Clicks "Commit X items →" to bulk-move them to Committed Work Plan
5. Reuses existing local change tracking + ADO sync workflow (no new sync path)

## Decisions
- Items with no release version are excluded from the dropdown (only versioned items can be bulk-committed)
- Bulk commit updates all items in memory first, then re-renders once (not per-item) for performance
- Dropdown auto-closes on outside click and resets selection state on reopen

## Open Items
- None

## Next Steps
- User to validate in production after merge
