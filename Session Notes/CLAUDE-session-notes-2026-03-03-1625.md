# Session Notes – 2026-03-03 (v200)

## Branch
`john-dev` → PR targeting `main`

## Changes Made

### Reports Tab – Bug Aging Report Enhancements

All changes in this session are on the **Reports** tab, scoped to bugs whose direct parent is a customer Issue.

#### Features Added
- **MTTR Chart improvements:**
  - Bar counts inside bars show number of tickets (not days)
  - P1 and P2 trend lines overlaid on chart to show month-over-month progression
  - Period selector: 3, 6, or 12 months (default 6)
  - Click any bar → popup table with matching bugs

- **Open Bug Aging Chart improvements:**
  - Click any bar → popup table with matching bugs

- **Popup table:**
  - Columns: Bug # (linked to ADO), Title, Days Open, Customer, Team, Release
  - Uses standard `buildGenericTable` format with sortable headers, copy/export
  - Days Open calculated from createdDate → closedDate (or today for open bugs)

- **Customer filter:**
  - Top-level dropdown in Reports header
  - Filters both charts and summary stats cards simultaneously
  - Populated dynamically from bug data

- **Bug # column width:** Widened to 75px so full 5-digit IDs are visible

## Files Modified
- `dashboard.js` – renderReportsView, showMttrBugPopup, aging chart onClick
- `dashboard-body.html` – Customer filter dropdown in reports header
- `dashboard.css` – col-id width 55px → 75px
- `changelog.js` – Updated v200 entry
- `DASHBOARD_README.md` – Updated v200 version history
- `CLAUDE.md` / `copilot-instructions.md` – Version bump to v200

## Open Items / Next Steps
- None identified
