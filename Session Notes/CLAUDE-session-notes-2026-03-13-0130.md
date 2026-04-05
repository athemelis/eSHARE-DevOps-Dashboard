# Session Notes — 2026-03-13

## Version: v228

## Commits in this PR (12 commits, tony-dev → main)

1. `2d727dc` — Fix column width persistence drift during auto-refresh
2. `af153c4` — Clickable warning banners & column width persistence fix
3. `5f2fa9b` — At-mention modal scroll fix & Releases show all tags
4. `3d12cb7` — Deep search Unified Modal, scroll fix, all tags & search re-trigger
5. `eaacc71` — Release picker search filter & legacy field fallback removal
6. `ba01c1b` — Remove legacy releaseVersion/targetDate field fallbacks
7. `8f8b739` — Release picker persists across auto-refresh
8. `026a9f0` — Customer name badges in Unified Modal header
9. `8475594` — Reorder Assigned To column in modal relationship tables
10. `1cc6ee0` — Description image fallback and click-to-zoom lightbox
11. `6cbbed4` — Active toggle default ON and button placement
12. `6fa6a7e` — Tasks dashboard utilization improvements

## Changes Made

### Column Width Persistence Fix
- Removed redundant DOM width re-capture during auto-refresh in `buildGenericTable()` and `saveAllTableScrollPositions()`
- Prevented rounding drift from pct→px→pct round-trips
- Removed dead Customers-specific resize code

### Clickable Warning Banners
- `detectStateInconsistency()` now collects `affectedItems` array
- Added `_warningItemsRegistry` for mapping warning text to items
- `buildWarningBannersHTML()` and `showWarningAffectedItems()` render clickable warnings
- Right panel click handlers navigate to affected item's Unified Modal

### At-Mention Modal Scroll Fix
- Root cause: nested scrollable containers (outer `.mention-notification-body` + inner `.generic-table-scroll-container`)
- CSS override disables inner scroll, in-place DOM class toggle for row click, save/restore scrollTop

### Releases Tags Editing
- Customer Bugs and Internal Bugs columns changed from `architecture` → `tags`
- `getInlineEditTagsForType()` returns ALL tags sorted alphabetically

### Deep Search → Unified Modal
- Replaced deep search popup with Unified Modal
- Added `options.highlightChildId` with auto-expand `<details>`, `search-highlight` pulse, scroll into view
- Fixed re-trigger by clearing `_lastDeepSearchPopupTerm`

### Legacy Field Fallback Removal
- Removed fallbacks from `getReleaseVersion()`, `hasReleaseVersion()`, `getTargetDate()`, `hasTargetDate()`
- Now exclusively reads cascading fields

### Release Picker Search & Persistence
- Search input in release picker dropdown with auto-focus and filtering
- CSS restructured as flex column with scrollable options
- Edits registered as `_pendingInlineEdits` entries to survive auto-refresh

### Customer Name Badges
- Cyan `modal-customer-badge` pills in Unified Modal subtitle for Features and Bugs

### Assigned To Column in Modal Tables
- Added to `buildRelationshipsSection`, `buildDeliverySlicesSection`, `buildProgressRelationshipsSection`
- Tightened column widths to prevent overflow

### Description Image Fallback & Lightbox
- `processDescriptionImages()` attaches `onerror` for orange-bordered placeholder with "View in ADO ↗"
- `showImageLightbox()` click handler for full-screen overlay (95vw × 95vh)
- `height: auto` prevents distortion on small screens

### Active Toggle Default ON & Button Placement
- Bugs toggle buttons moved from `.bugs-stats-row` to `filter-row-bugs` sticky header
- One-shot `_*ActiveDefaultApplied` flags for all 3 dashboards
- Clear button re-activates Active toggle; visibility based on deviation from Active-ON baseline

### Tasks Dashboard Utilization Improvements
- Assignee filter infers team via org chart for Team Utilization Breakdown
- Individual Breakdown total row with summed days and recalculated percentages
- Selected assignee row highlighted with cyan left border
- Work Log Summary utilization uses assignee count as denominator when assignee filter active
- Assignee filter takes priority over team filter for utilization denominator
- Total row uses raw totals instead of averaging rounded percentages
- Gap days counts all business days in work log entry date range (not just startDate)

## Decisions
- Targeted fix for utilization consistency (adjust denominator) rather than consolidating calculation functions — different analytical purposes and scopes
- Active toggle defaults to ON via one-shot flags rather than modifying localStorage defaults
- Gap days expanded to full date range to match Work Log Summary grid display

## Open Items
- None

## Next Steps
- Merge PR, sync branches
