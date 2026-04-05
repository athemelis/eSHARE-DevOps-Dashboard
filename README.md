# eShare DevOps Dashboard

**Current Version: v249**

A real-time dashboard for visualizing Azure DevOps work items, providing executive summaries, roadmap views, and team analytics.

**Live URL:** https://devops-dashboard.e-share.io

---

## Quick Start (Local Development)

```bash
# 1. Copy data files from SharePoint
./copy-data-files.sh

# 2. Start local HTTP server
./serve-dashboard.sh

# Or manually:
python3 -m http.server 8000
```

Then open http://localhost:8000/dashboard.html in your browser.

### How It Works
- `dashboard.html` loads `dashboard-body.html` dynamically via fetch()
- `dashboard-loader.js` fetches JSON data files from SharePoint (or local copies)
- `dashboard.js` renders all views and handles user interactions
- Data auto-refreshes every 60 seconds in the background

---

## Production Deployment

The dashboard is automatically deployed to **Cloudflare Pages** when changes are pushed to the `main` branch. The Cloudflare Pages project is managed via Terraform in the `eshare-k8s` repository.

**Access Control:** Protected by Cloudflare Zero Trust — requires eShare Azure AD authentication.

---

## Documentation Guide

New to this project? Read in this order:

| # | File | Purpose |
|---|------|--------|
| 1 | [README.md](README.md) | Project overview, quick start, architecture, data schema |
| 2 | [DASHBOARD-REFERENCE.md](DASHBOARD-REFERENCE.md) | Code reference — algorithms, data flow diagrams, key features |
| 3 | [.github/copilot-instructions.md](.github/copilot-instructions.md) | Session workflow, git ops, commit/PR checklists, version management |
| 4 | [.specify/memory/constitution.md](.specify/memory/constitution.md) | Project principles — 9 rules governing all code decisions |
| 5 | [Table-Columns.md](Table-Columns.md) | Lookup: column spec matrix for all 7 generic tables |
| 6 | [Bug-Mapping.md](Bug-Mapping.md) | Lookup: architecture component → bug tag mappings |
| 7 | [Feature-Mapping.md](Feature-Mapping.md) | Lookup: OKR → feature tag mappings |
| 8 | [README_PowerAutomate.md](README_PowerAutomate.md) | Infrastructure: Power Automate flows (both), version control, reconstitution |

Files 5–8 are standalone lookup references with no outbound links. The `ADO Python Scripts/` subdirectory has its own self-contained documentation.

---

## Project Structure

```
├── .github/
│   ├── copilot-instructions.md  # Copilot session workflow
│   └── workflows/deploy.yml    # Cloudflare Pages deployment
├── dashboard.html               # Shell/loader (entry point)
├── dashboard-body.html          # HTML structure
├── dashboard.css                # Styles
├── dashboard.js                 # Main application logic (~19,500 lines)
├── dashboard-loader.js          # Data loader with MSAL auth
├── capacity-planning-data.js    # Capacity planning helpers
├── changelog.js                 # Version changelog data
├── copy-data-files.sh           # Helper to copy JSON from SharePoint
├── copy-flows.sh                # Helper to copy & import flow exports
├── import-flow.sh               # Import a single flow ZIP (redacts secrets)
├── serve-dashboard.sh           # Helper to start local HTTP server
├── dev-status.sh                # Branch state and version checker
├── flows/                       # Power Automate flow definitions (version-controlled)
│   ├── ADO-ALL-Items/           #   ALL Items export flow
│   └── Export-ADO-WorkItemLinks/ #   WorkItemLinks export flow
├── _headers                     # Cloudflare Pages headers config
├── _redirects                   # Cloudflare Pages redirects
├── wrangler.toml                # Cloudflare Wrangler config
├── package.json                 # Node.js project config (Wrangler CLI)
├── DASHBOARD-REFERENCE.md       # Feature-specific code reference
└── README.md                    # This file
```

**Data files (not in repo, fetched at runtime):**
- `ALL Items.json` — Work items (Features, Bugs, Tasks, Issues, Delivery Slices)
- `WorkItemLinks.json` — Parent/child/related relationships
- `Org Chart.json` — Team structure and members
- `cascading_lists.json` — Picklist values for cascading fields

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:

1. **On Push to `main`**: Deploys to production
2. **On Pull Request**: Deploys a preview environment
3. **Manual Trigger**: Can be triggered manually from GitHub Actions tab

Uses Cloudflare's official `wrangler-action` for zero-config static site deployment with automatic HTTPS and CDN.

### Required GitHub Secrets

| Secret | Purpose |
|--------|---------|
| `CLOUDFLARE_API_TOKEN` | API token with `Account > Cloudflare Pages > Edit` permission |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID (from dashboard URL or account settings) |

---

## Architecture

The dashboard is a static single-page application (SPA) that:

1. Loads from Cloudflare Pages
2. Authenticates via Microsoft MSAL for SharePoint data access
3. Fetches JSON data from SharePoint Document Library
4. Renders interactive charts and tables

See [DASHBOARD-REFERENCE.md](DASHBOARD-REFERENCE.md) for detailed architecture diagrams and data flow.

## Data Sources

| File | Description | Update Frequency |
|------|-------------|-----------------|
| `ALL Items.json` | Work items (Features, Bugs, Tasks, Issues, Delivery Slices) | Every 3 minutes |
| `WorkItemLinks.json` | Parent/child/related relationships | Every 5 minutes |
| `Org Chart.json` | Team structure, members, capacity | Manual |
| `cascading_lists.json` | Release version ↔ target date mappings | On edit via Versions modal |

Data is exported from Azure DevOps to SharePoint via Power Automate flows. Flow definitions are version-controlled in the `flows/` directory. See [README_PowerAutomate.md](README_PowerAutomate.md) for the flow setup guide and flow version control instructions.

## Authentication

The dashboard uses Microsoft MSAL (Microsoft Authentication Library):

- **Client ID**: `bf683b68-0dc3-4205-a5b7-676f54a958c0`
- **Scopes**: `Sites.Selected` for SharePoint access
- **Local development**: MSAL bypassed, JSON files loaded directly from `./`

---

## Data Schema Reference

The dashboard JavaScript expects these exact field names from the JSON data:

```javascript
{
  id: number,              // Work item ID
  type: string,            // "Feature", "Bug", "Task", etc.
  title: string,
  state: string,
  assignedTo: string|null,
  areaPath: string,
  team: string,            // Extracted from areaPath
  iterationPath: string,
  iteration: string,       // Extracted from iterationPath
  createdDate: string,     // ISO datetime: "2025-08-01T18:50:47"
  stateChangeDate: string, // ISO datetime
  closedDate: string|null, // ISO datetime
  targetDate: string|null, // DATE-ONLY: "2025-12-31" (no time component!)
  priority: number|null,
  severity: string|null,
  tags: string|null,
  parentId: number|null,
  effort: number|null,
  effortRollup: number,
  backlogPriority: number|null,
  customers: string|null,
  teamsAffected: string|null,
  releaseVersion: string|null,
  bugType: string|null,
  component: string|null,
  feature: string|null,
  ticketCategory: string|null,
  deliverySliceOwner: string|null,
  url: string
}
```

### Date Handling

| Field | Format | Notes |
|-------|--------|-------|
| `targetDate` | Date only (`2025-12-31`) | Parsed as local date to avoid timezone shift |
| `createdDate`, `stateChangeDate`, `closedDate` | ISO datetime | `2025-09-11T22:18:10` |

---

## Development

### Adding New Features

New features follow the **Spec Kit pipeline** — a structured specification → planning → implementation workflow driven by VS Code Copilot agents:

1. `speckit.specify` — Write the feature specification from a natural language description
2. `speckit.clarify` — Identify and resolve underspecified areas
3. `speckit.plan` — Generate the implementation plan with design artifacts
4. `speckit.tasks` — Break the plan into dependency-ordered tasks
5. `speckit.analyze` — Cross-check consistency across spec, plan, and tasks
6. `speckit.checklist` — Generate a custom verification checklist
7. `speckit.implement` — Execute tasks with browser testing at phase boundaries

Spec artifacts are stored in `specs/{feature-name}/`. The project constitution (`.specify/memory/constitution.md`) defines the 9 principles that govern all code decisions. See [.github/copilot-instructions.md](.github/copilot-instructions.md) for the full session workflow.

For small bug fixes, skip Spec Kit and work directly on a `fix/` branch.

**Starting a session** — paste one of these into VS Code Copilot Chat:

> **New feature:** *"I want to start a new session for a new feature"*
>
> **Bug fix:** *"I want to start a new session for bug fixes"*

Copilot will set up the branch, bump the version, start the local server, and guide you through the appropriate workflow.

### Code Style

- JavaScript: ES6+ (vanilla, no build step)
- CSS: Custom properties for theming, class-based selectors
- HTML: Semantic markup

### Troubleshooting

**Charts show zeros / data not loading:**
1. Open browser console (F12)
2. Look for JavaScript errors
3. Hard refresh: Cmd+Shift+R

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v249 | 04/03/2026 | **Power Automate Flow Fix & Version Control:** Fixed WorkItemLinks data truncation (10,000→15,400 links) by replacing Foreach+Append with Compose+union() pattern (runtime 270 min→13 sec). Added flow version control tooling (import-flow.sh, copy-flows.sh) with automatic PAT redaction. Both flow definitions tracked in flows/ directory. Updated intervals to 3 min/5 min (88% of Office 365 action budget). Renamed README_ExportWorkItemLinks.md→README_PowerAutomate.md covering both flows, action budgets, content throughput limits, and reconstitution guide. |
| v248 | 04/01/2026 | **Releases Dashboard Generic Filter Migration:** Migrated all 11 Releases filter types from inline code to generic infrastructure (populateGenericFilterDropdowns, applyGenericSecondaryFilters). New generic builders for Type, Progress Status, Bug Owner. Cross-filter aware dropdowns with accurate counts. Bug Type consolidated from 3→2 categories across all dashboards. State persistence with automatic key migration. Removed ~500 lines of dead inline code. Fixed assignee filter format mismatch. Fixed chart-click-to-filter dropdown sync. |
| v247 | 03/27/2026 | **Spec Kit Onboarding & GitHub Flow Migration:** Onboarded GitHub Spec Kit with 9-principle project constitution. Migrated from tony-dev branch to Standard GitHub Flow (per-feature branches from main, PRs to main). Rewrote dev-status.sh to be branch-agnostic. Updated all workflow docs. Pre-migration state archived at git tag `pre-speckit`. |
| v246 | 03/26/2026 | **Unified Modal Resize Fix & Customer Editing:** Fixed resize handle regression (horizontal/vertical splits stopped responding to drag). Added inline customer editing in modal header — click customer badges to add/remove via multi-select picker. Items without customers show a "+ Customer" button. |
| v245 | 03/22/2026 | **Releases Dashboard Performance Fix:** Fixed Clear Filters taking up to a minute — eliminated redundant renders (3-4 → 1), cached org chart map (728× → 1 build per render), added cross-filter short-circuit when no filters active, fixed uncaught TypeError in generic filter handlers. |
| v244 | 03/20/2026 | **Customers Dashboard: Quarterly Flow & Aging Improvements:** Quarterly Flow Summary table showing issue flow by priority (P1–P4) with clickable cells. Unique Customers column with popup breakdown. Aging histogram limited to past quarter for closed items, average age display, click-to-filter toggle with cyan highlight. Issue Trend aligned to rolling quarter. Fixed Capacity Dashboard crash (isCustomerBug shadowing). Corrected hosting docs. |
| v243 | 03/19/2026 | **@Mention Scanning Optimization:** Incremental comment scanning using batch comment count comparison — reduces API calls from ~6,500 to ~66 on subsequent loads (99% reduction). Fixed 403 Forbidden error by removing SharePoint mention cache write. |
| v242 | 03/19/2026 | **Comparison Modal & Customer Pills:** Comparison modal always shows Issue in left pane. Customer name pill in Unified Modal and Comparison Modal for all work item types. Added generic infrastructure guidelines to project instructions. |
| v241 | 03/18/2026 | **Generic Filter & Matching Infrastructure:** Shared secondary filter function, dashboard filter registry with handler helpers, Feature-Team utilities (via Delivery Slice area paths), Bug-Team utilities (via child Task area paths + Org Chart), bug type utilities replacing 42 inline comparisons. Teams dashboard: added Customer/Release/Tags columns, fixed bug categorization. Removed deprecated estimation fields. Consolidated column width persistence (~100 lines of boilerplate removed). |
| v240 | 03/17/2026 | **New Teams Dashboard:** Team lead unified view with six tables (Features/Customer Bugs/Internal Bugs × Owned/Contributing). Feature ownership by Assigned To matching Org Chart. Cut line, progress, drag-to-reorder, full generic filter bar. Generic table auto-persistence for sort state and column widths. Previous Teams view moved to Reports → Teams (archive). |
| v239 | 03/16/2026 | **Universal Cross-Dashboard Search:** Search box now finds work items across all dashboards. Dropdown groups results by scope: current view, hidden by filters, related items (parent/child/Related links), other dashboards, and hierarchy (Epics/Key Results/Objectives). Click results to scroll-to, open Unified Modal, or auto-switch dashboards. |
| v238 | 03/16/2026 | **CS Owner & Assignee Filters, OKR Click-to-Filter:** Added CS Owner and Assigned To filter dropdowns to the Customers dashboard sticky header. ER Prioritization OKR column headers are now clickable to filter by tag prefix (toggle on/off with visual highlight). Fixed cross-filter dropdown counts to respect Insight card and heatmap cell filters. |
| v237 | 03/16/2026 | **OKR Reordering, Mugshots, Comparison Modal Fixes:** Drag-and-drop OKR tag reordering with localStorage persistence. Added mugshots for 5 new Customer Success team members. Fixed comparison modal field row misalignment when panels have different header heights. Removed debug console output. |
| v236 | 03/15/2026 | **Comparison Modal: Sync Arrow Realignment:** Fixed sync arrows drifting after tag edits. Arrow row heights recalculate after any field edit. |
| v235 | 03/15/2026 | **Comparison Modal: Editable Tags Row:** New Tags row between Priority and Release with pill display. Searchable multi-select dropdown for adding/removing tags, saved to ADO. Sync arrows merge tags additively — adds other side's tags without removing existing ones. |
| v234 | 03/15/2026 | **Customers: No OKR Filter Fixes:** "No OKR" filter shows only Enhancement Requests. Toggle highlights when active and toggles on/off. No OKR × CS tag intersections filter correctly. |
| v233 | 03/15/2026 | **Comparison Modal: Light Mode & Arrow Alignment Fixes:** Compare button darker teal in light mode. Sync arrows aligned with field rows, no scrollbar. |
| v232 | 03/14/2026 | **Comparison Modal: Discussion Copy & Sticky Headers:** Copy discussion comments between sides (single or all with attribution). Sticky headers keep title, badges, owner, and field rows pinned while scrolling. Synchronized scroll across all three columns. Inline field editing for State, Priority, Release/Target Date. State sync guardrails block incompatible states with disabled arrows. |
| v231 | 03/14/2026 | **Comparison Modal Editing & State Guardrails:** Inline editing for State, Priority, Release/Target Date fields in Comparison Modal. Release & Target Date edited as paired values. State sync guardrails block incompatible states between work item types. Copy description and discussion comments between sides (single or all). Full description/discussion editing matching Unified Modal. Fixed duplicate relationship rows from ADO dual-link entries. Generic comment editor refactored to container-scoped. |
| v230 | 03/13/2026 | **Relationship Fixes & Comparison Modal:** New side-by-side Comparison Modal for related Issue↔Feature and Issue↔Bug pairs. One-click field sync (State, Priority, Release, Target Date) with immediate ADO save. Full panel headers with badges, mugshots, pills matching Unified Modal. Breadcrumb navigation back to source modal. Insight-filtered rows open comparison directly. Fixed Parent link type handling in relationship editing. Relationship changes persist across auto-refresh. |
| v229 | 03/13/2026 | **Staff Team Utilization & Customers Relationship Insights:** Staff team included in Tasks utilization for correct assignee→team inference. Customers Insights section shows relationship warnings: ERs with no Feature, ERs inconsistent with Feature (release/date/state), Customer Bugs with no Bug, Customer Bugs inconsistent with Bug. Clicking insights filters the Issue Details table. |
| v228 | 03/12/2026 | **Toggle Defaults, Tasks Utilization & Modal Enhancements:** Active toggle defaults to ON across Roadmap/Customers/Bugs dashboards. Bugs toggle buttons moved to sticky header. Tasks assignee filter infers team for utilization breakdown with total row, highlighting, and consistent utilization calculation. Gap days counts full entry date range. Description image fallback and click-to-zoom lightbox. Assigned To column in all modal relationship tables. Deep search opens Unified Modal with child highlighted. Clickable warning banners. Fixed column width drift, scroll bouncing, deep search re-trigger. Releases all-tags editing, legacy field removal, release picker search/persistence, customer badges. |
| v227 | 03/12/2026 | **Utilization Fixes, Modal Enhancements & Mugshot Fix:** Fixed utilization formula (days logged ÷ business days), multi-team member support, Period selector in sticky header. Fixed mugshots in Roadmap/Bugs/Releases/Capacity tables. Unified Modal: Cmd/Ctrl+K link insertion, resizable desc/discussion divider, priority badge, effort badge for DS, DS Owner in header, Team column in relationships, Set Release dropdown fix. Scroll position preserved during auto-refresh. |
| v226 | 03/11/2026 | **Tasks Dashboard Enhancements:** Team Utilization Breakdown with own/cross/external effort categories, individual member breakdown table, period-scoped stat cards, performance-optimized work log parsing, standardized table modals with shared resize, mugshots in all person-name table columns, editable Task fields in Unified Modal (State, Assigned To, Iteration, Team, Task Type, Priority), Area Path shown in modal header. |
| v225 | 03/10/2026 | **Updated Mugshots:** Added profile photos for Mark Cassetta, Konstantinos Gkofas, Sangeet Saha, Athina Kalampogia, Vasiliki Tzanaki, and Sai Kishore Punagani. |
| v224 | 03/09/2026 | **Add Relationship & Modal Category Pills:** New "+" button in Relationships section to add links by searching work items. Issues show Ticket Category pill (Enhancement Request, Bug, Task). Bugs show Bug Type pill (Customer Related, Internal) in modal header. |
| v223 | 03/09/2026 | **Fix Duplicate @Mention Entries for Team Leads:** Team leads managing multiple teams no longer appear twice in @mention dropdown. All leads show "Team Lead" indicator with team name(s). Fixed isLead detection for formal vs common name mismatches. |
| v222 | 03/09/2026 | **Modal Contextual Tags & Pill Breadcrumbs:** Unified Modal header shows contextual tags per type: OKR + CS tags for Features, CS tags for Enhancement Requests, Architecture tags for Bugs, Iteration Path for Tasks. Pill clicks in modal header now navigate with breadcrumb trail for back navigation. |
| v221 | 03/08/2026 | **Clickable Relationship Pills:** Fixed relationship pills (Feature↔Issue, Bug↔Issue) in table Title columns not opening the Unified Modal when clicked. Root cause was a variable scoping issue where inline click handlers couldn't access work item data. |
| v220 | 03/08/2026 | **Modal Mugshots, Iteration Column & Release Mismatch Warnings:** Mugshot photos replace initials for Bug Owner and Assigned To in the Unified Modal header. Iteration Path column added to Relationships section. Release mismatch warnings with alignment buttons when a Bug↔Issue or Feature↔ER pair have different Release Version or Target Date. |
| v219 | 03/08/2026 | **Relationship Type Editing & Bug Type Badges:** Bug type badges (Customer/Internal/Infra) shown in Relationships tables. Click any Relationship type cell (Parent/Child/Related) to change the link type directly in Azure DevOps via API. |
| v218 | 03/08/2026 | **Relationship Pills & Modal Improvements:** Pills now open Unified Modal instead of ADO. Warning pills for missing relationships (no Bug, no Feature, no Issue). Issue pill in Bugs Dashboard, Bug pill in Releases Issues table. Modal header shows Bug Owner/CS Owner + Assigned To. Progress panel always shows when opening from Capacity Dashboard. |
| v217 | 03/07/2026 | **Inline Edit Fixes:** Multi-select picker click target fix (text clicks now toggle checkbox). Inline edits persist across auto-refresh with 5-minute sync timeout. Picker z-index fix for modal tables (@mention panel, Reports popups). |
| v216 | 03/07/2026 | **Inline Field Editing & Notification Modal Fixes:** Generic inline editing for 10 work item fields (State, Assigned To, Team, Tags, Customers, Release, Category, CS Owner, Bug Type, Bug Owner) with single-select, multi-select, and paired pickers. Tags filtered by work item type. Editable across all dashboards and modal tables. Roadmap Team Summary expanded by default. Notification modal resize handle with persistent sizing. Row click opens Unified Modal with return-to-panel. |
| v215 | 03/06/2026 | **Reports Popup Tables, Responsive Columns & Breadcrumbs:** Reports chart popup now uses full generic table with 14 columns, resizable modal, and row click to open Unified Modal. Column widths stored as percentages for responsive scaling across monitors. Full filter suite added to Reports Dashboard (11 filters with sticky header). Clickable relationship rows and breadcrumb navigation in Unified Modal. Title text wraps instead of truncating. Offline notification cache for localhost dev. |
| v214 | 03/05/2026 | **Capacity Bug Effort Fix:** Fixed Feature→Bug effort calculation to use child Task iterations instead of Bug-level estimation fields, correctly accounting for cross-iteration bug work in capacity planning. |
| v213 | 03/05/2026 | **Notification Cache & Persistence:** @mention scan results cached in localStorage for instant badge display on page load. Auto-refresh skips re-scan when cache is complete. Partial scan progress saved every 10 items to survive page reloads. |
| v212 | 03/05/2026 | **Combined Release Column:** Merged Release Version and Target Date into a single "Release" column across all generic tables — version on top, date below in muted text. Positioned after Progress column (after Priority in Customers). Fixed generic table sort bug with undefined stateOrder variable. |
| v211 | 03/05/2026 | **@Mention Notification Fix:** Fixed notification scan finding 0 results — detection now matches the native ADO mention format (data-vss-mention attribute) in descriptions and discussions. |
| v210 | 03/04/2026 | **Task Detail Modal:** Click any Task row in the Unified Modal progress section to open a stacked Task detail view. Left panel: description + discussion. Right panel: progress bar, key fields grid (estimate, completed, remaining, state, assignee, iteration, team, priority), and worklog entries table. |
| v209 | 03/04/2026 | **@Mention Notification Bell:** 🔔 bell icon in header with red badge shows unread @mention count. Scans descriptions and discussions for your name. Click bell to open notification table; click row to open Unified Modal with mention highlighted. Viewed items auto-clear. Rate-limit retry with exponential backoff. |
| v208 | 03/04/2026 | **Edit Discussion Messages:** Hover over any discussion message in the Unified Modal to reveal a ✏️ edit button. Click to inline-edit the message with full rich text toolbar, @mention and #mention support. Save updates the comment in ADO. |
| v207 | 03/04/2026 | **Editor List Fix & @Mention Common Names:** Fixed bullet/numbered lists rendering off-screen in editors. @mentions now display common names from Org Chart instead of formal ADO names. |
| v206 | 03/04/2026 | **Comment Editor Always Visible:** Fixed comment editor text box sometimes not appearing in the Unified Modal. Restructured conversation layout so editor is always visible below discussion bubbles regardless of content height. |
| v205 | 03/04/2026 | **Comment Editor Sticky Toolbar:** Toolbar (Bold, Italic, lists, Save) stays visible at bottom of discussion panel as you type. Editor auto-expands with more room before scrolling. |
| v204 | 03/04/2026 | **Mention Dropdown Enter Key:** Press Enter to select the first match in @mention and #mention dropdowns without needing to arrow-key or click. |
| v203 | 03/04/2026 | **CSP Fix for @Mention Identity Resolution:** Fixed Content Security Policy blocking identity GUID lookups to vssps.dev.azure.com. @mentions now properly trigger ADO notifications. |
| v202 | 03/04/2026 | **Unified Modal – Edit Description & Discussion:** Edit descriptions with rich text toolbar, add discussion comments saved to ADO, @mention with identity resolution, #mention with clickable work item links, draggable resize handle between modal panels. |
| v201 | 03/03/2026 | **Nav Tab Responsive Layout:** Fixed nav tabs overflowing the page. Tabs shrink to fit on one line and wrap to a second row on narrower screens, keeping all dashboard tabs visible at every viewport width. |
| v200 | 03/03/2026 | **Reports Tab – Bug Aging Report Enhancements:** New Reports tab with Bug Aging Report scoped to bugs with Issue parents. MTTR chart (avg days to resolution by priority, month-over-month) with 3/6/12-month period selector and P1/P2 trend lines. Open Bug Aging chart (age buckets × priority stacked bar). Customer filter applies to both charts. Click any bar to open a popup showing matching bugs (Bug #, Title, Days Open, Customer, Team, Release). |
| v199 | 03/01/2026 | **Capacity Warnings Search Fix:** Fixed warnings badge disappearing when using search filter — items not on the board (e.g. committed but no work items in iteration) now found via simple title/ID match instead of deep search. |
| v198 | 03/01/2026 | **Capacity Warnings Improvements:** Warnings modal respects all sticky header filters (Bug Owner, Assignee, Customer, Priority, State, Tag, Team). Redesigned with sortable table columns and 3 collapsible sections for easier triage. Modal enlarged (85vw × 80vh) and user-resizable. |
| v197 | 02/28/2026 | **Modal Fixes & Capacity Warnings:** Progress by Team table column order changed to Team/Estimated/Actual/State/Progress. Fixed release date in Unified Modal header showing one day earlier than expected. Capacity Dashboard warning badge detects 6 types of inconsistencies (committed without work items, missing effort estimates, work items not committed). Warnings modal with per-item remediation actions — all via ADO API. |
| v196 | 02/27/2026 | **Tasks Dashboard & Unified Modal Editing:** Assigned To filter now updates all sections (Work Log, Team Summary, Insights, Charts, Table). Assignee dropdown shows names without emails. Utilization % in Work Log Summary stats and Team Summary cards. Work Log item links and parent badges open the Unified Modal. Committed Iterations shown in modal header with add/remove and live ADO sync. Release Version & Target Date editable via paired cascading list picker with ADO save. Priority column editable in all tables — click to change P1–P4 with ADO sync. |
| v195 | 02/26/2026 | **Unified Modal Enhancements:** Owner initials avatar + name in header. OKR/CS tag pills for Features, Architecture tag pills for Bugs. Work item ID is now a clickable ADO hyperlink (removed Open in ADO button). Release version and target date in subtitle. State badge in subtitle. Worst-case state per team in Progress by Team tables. Modal consistent across Capacity and generic table dashboards. |
| v194 | 02/26/2026 | **Capacity Dashboard Bulk Commit by Release:** New "Commit by Release" button in the Backlog Work Candidates column header. Dropdown shows release versions with item counts. Select one or more releases to bulk-commit all matching items to the Committed Work Plan. |
| v193 | 02/26/2026 | **Capacity Dashboard Drag-to-Reorder:** Drag planning items to reorder Backlog Priority in both Backlog Candidates and Committed Plan panels. Section-scoped — items stay within their group (Customer Bugs, P1-P4 Features, Internal Bugs). Reuses ADO write-back, pending sync indicators, and 5-minute timeout with Revert. |
| v192 | 02/26/2026 | **Column Width Persistence Fix:** Fixed column widths not persisting across page refreshes. Root cause: switching views caused hidden table headers to report 0px width via `offsetWidth`, which overwrote saved values with 0 (falsy). Fix skips width capture for hidden tables (`display: none`). |
| v191 | 02/25/2026 | **Drag-Reorder Pending Sync:** Dragged rows show pending sync indicator (orange border) until ADO confirms the priority change. Priority persists across auto-refresh and manual refresh. Sync errors after 5 minutes show Revert button. Hard refresh clears pending state. |
| v190 | 02/25/2026 | **Drag-to-Reorder Priority:** Drag table rows to reorder Backlog Priority with automatic ADO write-back. Available on all dashboards when sorted by default order. Visual feedback with drop indicators and success/failure animations. Bugs dashboard now defaults to Backlog Priority sort. Improved markdown rendering in work item modal description and conversation tabs. |
| v188 | 02/25/2026 | **Unified Work Item Modal:** Consolidated 3 separate modals (row click details, 💬 conversation, progress bar) into a single two-panel modal. Left panel shows description + conversation; right panel shows relationships, progress, team breakdown, and collapsible child items. Removed ID hyperlinks and progress bar hover for unified click-anywhere UX. |
| v187 | 02/25/2026 | **Multi-Value Column Separators:** Customer and Architecture columns now display dotted line separators between entries, consistent with Tags column styling. Added Table-Columns.md reference to instruction docs. |
| v186 | 02/25/2026 | **Standardized Table Columns:** Aligned columns across all 7 generic tables (Releases, Roadmap, Customers, Bugs) to a consistent spec. Added Priority to all Releases tables, Tags to Releases Features/Issues, Assigned To to Releases Issues and Customers, Team to Roadmap and Bugs, Architecture to Bugs. Tags/Customer/Architecture columns now show each value on a separate line. New Table-Columns.md reference document. |
| v185 | 02/24/2026 | **Version Merge Feature:** New 🔀 merge button in Versions modal moves all work items from one version/date pair to another. Inline merge UI with target dropdown, optional source pair deletion after merge, bulk ADO work item updates, and picklist sync. |
| v184 | 02/24/2026 | **Persistent Column Widths:** Removed 24-hour expiration on dashboard state. Column widths, sort orders, filters, and scroll positions now persist indefinitely in localStorage instead of being silently cleared after 24 hours of inactivity. |
| v183 | 02/24/2026 | **Picklist Consistency Fix Actions:** All consistency issues now listed individually instead of showing only the first. "Fix Inconsistencies" presents per-issue choices — "Add to picklist" or "Remove from config" for values in config but not picklist, and vice versa. JSON internal repairs and picklist fixes handled as separate workflows. |
| v182 | 02/24/2026 | **Picklist Consistency Detection:** Versions modal now detects when cascade config values are missing from ADO picklist fields or when stale values exist in picklists but not in config. Check runs automatically on modal open (requires auth). Issues shown in consistency warning banner with existing "Fix Inconsistencies" repair action. |
| v181 | 02/24/2026 | **Versions Modal: Picklist Cleanup & Sort Fix:** Deleting or editing version-date pairs now properly removes stale values from ADO picklist fields (previously only added new values). Edited entries appear in sorted order in cascading lists instead of appended at end. Work item bulk updates run before picklist sync to avoid validation issues. |
| v180 | 02/23/2026 | **Bulk Work Item Updates on Version Edit/Delete:** Editing a version-date pair in the Versions modal now bulk-updates all assigned work items in ADO with the new values. Deleting a pair clears version/date fields from all assigned items. Confirmation dialog shows affected counts by type before proceeding. Live progress indicator during updates. Only changed fields are patched. In-memory data updates immediately. |
| v179 | 02/22/2026 | **Picklist Sync & Conversation Modal:** Adding or repairing version/date pairs now automatically syncs new values to the ADO Custom.CascadingVersion and Custom.CascadingDate picklist field definitions. New 💬 icon next to every Work Item ID in all tables — click to view the full ADO discussion thread in a modal popup. Fixed CSP blocking ADO Extension Management API (`extmgmt.dev.azure.com`) in production. Fixed ADO data envelope parsing so Versions modal displays and saves correctly. |
| v178 | 02/22/2026 | **Table Column Width Persistence:** Column widths now persist across auto-refresh, tab switches, and page reloads. Resizing any column captures all column widths to keep the entire table layout stable. Applies to all generic tables (Releases, Roadmap, Customers, Bugs, Tasks, Validation, Capacity). |
| v177 | 02/22/2026 | **Live ADO Sync & Consistency Repair:** Cascading lists now load directly from ADO Extension Management API as single source of truth, with SharePoint as fallback. Auto-refreshes every 60s alongside work item data. Bidirectional consistency check detects partial edits with ⚠️ warning badge on Versions link. One-click repair fixes missing reverse mappings. |
| v176 | 02/21/2026 | **Cascading Lists Phase 3 — Edit & Write-Back:** Versions modal Edit Mode for adding, editing, and deleting version-date pairs. Changes write back to both ADO Cascading Picklists extension and SharePoint in one save operation. Concurrency control via __etag. Inline editing with YYYYMM.X.X validation, duplicate prevention. Visual row indicators (added/modified/deleted) with undo support. |
| v175 | 02/16/2026 | **ADO API Integration & Commit to ADO:** Browser-based Azure DevOps API access via MSAL authentication. Capacity Dashboard "Commit to ADO" button writes changes directly to ADO instead of requiring manual CLI commands. Read-merge-write pattern prevents overwriting concurrent edits. Per-item error tracking with partial failure support. |
| v174 | 02/16/2026 | **Estimate Warnings & Resize Handles:** Fixed false "missing original estimate" warning on Features with Done/Closed Delivery Slices. Table column resize handles now always visible with subtle gray indicator. Workaround for Chromium/Edge macOS bug where hover state gets stuck after drag operations. |
| v173 | 02/13/2026 | **Clickable Date Issues Insight:** Clickable "items with date issues" insight in Releases Dashboard filters to affected items. |
| v172 | 02/13/2026 | **Deep Search (Releases Dashboard):** Search box now finds child and related items. Search for a Delivery Slice, child Bug, or Task ID → parent Feature/Bug appears in table with auto-opening progress popup highlighting the matched child. Search for an Issue → both the Issue and related Feature appear. Search for a Feature → related Issues also shown. Badges ("Contains: #ID" / "Related: #ID") on table rows indicate deep search matches. Issues table auto-expands when search returns Issues, re-collapses when cleared. Minimum 3-character threshold and exact-ID popup trigger prevent false matches while typing. |
| v171 | 02/12/2026 | **Releases Dashboard Insights Interactivity:** Clickable "Next" release insight filters to next upcoming release. Clickable "needs release version" insight filters to items missing release. Next release column highlighted in Items by Release chart with "Next" arrow label and theme-aware border (yellow dark mode, blue light mode). Theme toggle now re-renders charts for instant color updates. |
| v170 | 02/12/2026 | **DS Estimate Fixes:** Warning count for missing estimates now correctly checks DS-level effort instead of task-level originalEstimate for Delivery Slice child tasks. Removed misleading per-task Estimate column from DS task tables in progress popup — estimate shown once at DS header level. |
| v169 | 02/12/2026 | **Warning Count Fix:** Fixed child estimate warning count to include all tasks with missing original estimate, not just those with work logged. Warning count now matches what users see in the progress popup. |
| v168 | 02/12/2026 | **Estimate Missing Display Consistency:** Changed "Estimate missing" progress cell to show `?% (Xd / ?d)` format matching normal progress display pattern, with `?` for unknown values. |
| v167 | 02/12/2026 | **Enhanced Warning Detection:** Items with "Estimate missing" now included in warnings filter with ⚠️ icon. New warning rules: child tasks with work but no original estimate bubble up to parent; deadline risk when within 7 days of target date and <75% progress. Multiple warnings shown as separate banners in progress popup. |
| v166 | 02/12/2026 | **Progress Popup Estimation Fix & Total Row:** Fixed estimation source mismatch in Feature progress popup — Progress section now uses same source (task originalEstimate) as Summary Estimates table. Added Total row to Progress by Team table. Fixed Warnings "Clear Filter" button not working in Releases dashboard. |
| v165 | 02/12/2026 | **Validation Drilldown Tables Refactored + Bugs Under Delivery Slices Check:** New "Bugs Under Delivery Slices" validation check in Hierarchy group. Refactored 15 of 16 data quality drilldown tables to use generic table format with pills, relationships, progress bars, sortable columns, and row-click detail modals. |
| v164 | 02/11/2026 | **Show Unestimated Teams in Progress Popup:** Teams with actual work logged but no estimation now appear in Progress by Team table with "No estimate" indicator. Fixes incorrect overall progress percentage when child tasks belong to unestimated teams. |
| v163 | 02/11/2026 | **Progress Popup Iteration & Team Scoping:** Progress popup now scopes to selected iteration and team filter. New iteration summary table with highlighted current column. Child Bug effort included in capacity calculations. Added emoji indicators, team, state, Assigned To columns. Popup wider and resizable. |
| v162 | 02/10/2026 | **What's New Popup Fix:** Fixed What's New popup not appearing when a new version is detected during auto-refresh. Root cause: CSP blocked `new Function()` (eval) used to reload changelog.js. Replaced with CSP-safe dynamic `<script>` tag injection. |
| v161 | 02/10/2026 | **Composite Feature Progress (Child Bugs Roll-Up):** Internal bugs that are children of a Feature now roll up into the Feature's progress bar in the Releases dashboard, instead of appearing separately in the Internal Bugs table. |
| v160 | 02/10/2026 | **Team Mapping Fixes & Clickable Progress by Team:** Fixed team mapping inconsistencies — added UX Design to area path mapping, changed Govern mapping to match area path name. Added `formatTeamDisplayName()` for proper casing. Made Progress by Team rows clickable — click a team to filter release tables. |
| v158 | 02/10/2026 | **URL Hash State (Shareable Links):** Browser URL reflects current dashboard state in real-time. Hash parameters for view, filters, sort, scrollTo. Right-click context menu for "Copy link to item". What's New popup on version upgrade. Changelog stored in separate `changelog.js` file. |
| v157 | 02/08/2026 | **Cascading Lists Integration (Phases 1-2):** Versions modal accessible from all dashboards via "📅 Versions" link. Searchable table of release versions with target dates. Auto-scrolls to current date. |
| v156 | 02/05/2026 | **Issue Cascading Fields Migration & Bug Effort from Tasks:** Migration scripts for Issue release versions and target dates. Bug effort calculated from child Tasks (iteration-aware). Added Progress and Bug Owner columns to Releases. |
| v155 | 02/04/2026 | **Bug Estimation to Task Migration:** Python script to migrate 204 Bug team estimation fields to child Task `originalEstimate` fields. Dashboard migrated to cascading fields with fallback logic. |
| v154 | 02/02/2026 | **Capacity Planning Board Pills & Code Cleanup:** Relationship pills on Capacity Planning Board items. Removed ~637 lines of deprecated capacity table code. |
| v153 | 02/02/2026 | **Executive Dashboard Prep & Dead Code Removal:** Removed stale capacity table functions. |
| v152 | 01/30/2026 | **Capacity Dashboard - Sticky Headers & Clickable Rows:** Sticky headers with independent scrolling for planning board columns. Clickable rows and progress cells. |
| v151 | 01/28/2026 | **Roadmap Dashboard Bug Fixes:** Fixed "Untagged" click filter, Tag dropdown Clear button, sticky header Clear button for Untagged filter. Fixed Assignee/Iteration "Select All". |
| v150 | 01/27/2026 | **Releases Dashboard - Team Filter Progress Fix:** Fixed team filter progress calculations. |
| v149 | 01/26/2026 | **Release Progress Tracking:** Comprehensive progress tracking for Features and Bugs in Releases Dashboard. Progress Summary Section, Progress Column, Progress Detail Popup, Progress Status Filter, Warning Detection. |
| v148 | 01/25/2026 | **Org Chart Capacity Field Support:** Capacity field (0.0-1.0), isLead flag, three-tier capacity glow system. Team capacity calculated from individual availability. |
| v147 | 01/24/2026 | **Capacity Dashboard - Stacked Team Capacity Bars:** Breakdown by work item type. Over-capacity visual indicators. Fixed localStorage quota exceeded error. |
| v146 | 01/22/2026 | **Capacity Dashboard - Effort Calculation Fixes:** Fixed floating-point precision. Critical iteration filtering fix — effort scoped to selected iteration only. |
| v145 | 01/21/2026 | **Capacity Dashboard - Layout Fixes:** Fixed two-column planning board overflow and sticky positioning. |
| v144 | 01/21/2026 | **Capacity Dashboard - Filter UI Improvements & Auto-Expand:** Refactored filters to generic components. Auto-expand filtered sections. |
| v143 | 01/21/2026 | **Capacity Planning Dashboard - Interactive Planning Board:** Two-column layout, real-time capacity visualization, interactive planning with ADO sync. |
| v142 | 01/20/2026 | **Capacity Dashboard - Clear Filters State Persistence:** Fixed stale values restored on page reload after clearing. |
| v141 | 01/20/2026 | **Capacity Dashboard - Auto-Refresh Priority Detection:** Priority reordering now triggers re-render. |
| v140 | 01/20/2026 | **Capacity Planning Dashboard (WIP):** New dashboard for iteration-based capacity planning with summary cards, team capacity chart, tables, filters, and state persistence. |
| v139 | 01/19/2026 | **Releases Dashboard - All Time Period Filter:** Added "All Time" option to Items by Release chart. |
| v138 | 01/16/2026 | **Customers Dashboard - Issue Trend Section:** Stats cards, Issue Trend by Week combo chart, filter integration. |
| v137 | 01/16/2026 | **Customers Dashboard - Default Sort by Backlog Priority:** ER Prioritization stacked bar chart replacing summary table. |
| v136 | 01/16/2026 | **Active/Unreleased Toggle Buttons (Customers & Bugs):** Quick toggle buttons with state sync and persistence. |
| v135 | 01/16/2026 | **Releases Dashboard - Period Filter & Architecture Column:** Period dropdown for Items by Release chart. Architecture column in Bug tables. Fixed renderCell fallback. |
| v134 | 01/14/2026 | **Bugs Dashboard - Bug Owner Column & Filter:** Bug Owner column mapped to deliverySliceOwner. Bug Owner filter dropdown. Identity display fix. |
| v133 | 01/14/2026 | **Releases Dashboard - Stacked Bar Chart:** Items by Release stacked by type. Bug↔Issue relationship pills. Untagged filter consistency. OKR category filter fix. |
| v132 | 01/13/2026 | **Enhancement Request → Feature Link Pills:** Relationship pills linking ERs to Features and vice versa. |
| v131 | 01/13/2026 | **Roadmap OKR Tag Pills:** Color-coded OKR pills. Generic filter "(No X)" options. Releases bar chart Assignee filter fix. |
| v130 | 01/13/2026 | **Tag & Release Filter Bug Fix:** Fixed OR logic bug. OKR Summary sorted by feature count. |
| v129 | 01/13/2026 | **Table Scroll Position Preservation:** Built into buildGenericTable(). Column resize persistence. Clickable work item ID in modal. Roadmap OKR Summary redesign. |
| v128 | 01/12/2026 | **Bugs Dashboard - VTTS Architecture Component:** Added VTTS to CWP section. |
| v127 | 01/09/2026 | **Roadmap Header Space Optimization:** Bug Trend chart fixes. Bug Closed Date Algorithm documented. Aging calculation fix. |
| v126 | 01/08/2025 | **Releases Dashboard - Team & Assignee Filter Improvements:** Team filter checks Delivery Slice area paths. Assigned To filter. Roadmap fixes. Quick toggle buttons. |
| v125 | 01/07/2025 | **Bugs Dashboard - Tag Visualization & UX:** Tags on separate lines. Architecture tag pills. Auto-refresh scroll preservation. Related links duplicate fix. |
| v124 | 01/06/2025 | **Bugs Dashboard - Architecture Diagram Restructure:** Analytics and Utilities sections. Security & Regression filters. |
| v123 | 01/05/2025 | **Validation Dashboard Cleanup:** Removed redundant Data Quality Insights section. |
| v122 | 12/31/2025 | **Releases Filter Fixes & Tasks Search:** Fixed Release/Type/Bug Type filters. Blocked pill. Tasks search filters Work Log. Light/Dark mode toggle. |
| v121 | 12/30/2025 | **Tasks Work Log Calendar Week Selector:** Calendar-based Monday-Sunday weeks. Period multi-select. |
| v120 | 12/28/2025 | **Details Dashboard Removed & Validation UI:** 8 views instead of 9. Data Quality Cards with inline category labels. |
| v119 | 12/28/2025 | **Validation Dashboard Auto-Refresh Fix:** Preserves specialized card table during auto-refresh. |
| v118 | 12/27/2025 | **Validation Dashboard Sticky Header & Filters:** 8 common filters. Generic table with 14 columns. |
| v117 | 12/26/2025 | **Dev Status Script Improvements:** Prod/dev version display, box-drawing characters. |
| v116 | 12/23/2025 | **Roadmap OKR Clickable Filter:** Clickable "features without OKR tags". "(No Tags)" option. |
| v115 | 12/22/2025 | **Chart Animation Fix:** Eliminated visual flash during auto-refresh. |
| v114 | 12/22/2025 | **Branding:** Favicon and eSHARE logo in header. |
| v112 | 12/21/2025 | **New 4-File Architecture:** Modular architecture. Auto-refresh. Bug fixes. |
| v111 | 12/21/2025 | **Chart Animation Control:** `isAutoRefresh` flag for chart animations. |
| v110 | 12/21/2025 | **Customers Dashboard Fix:** Fixed Category filter. |
| v109 | 12/21/2025 | **Executive Dashboard Fix:** Fixed chart filters. |
| v108 | 12/21/2025 | **Repository Cleanup:** Deleted Templates/, generate_dashboard.py, old architecture files. |
| v107 | 12/21/2025 | **Auto-Refresh Feature:** 60-second background data refresh. |
| v106 | 12/21/2025 | **Engineer Filter Fix.** |
| v105 | 12/21/2025 | **Team Column Fix.** |
| v104 | 12/21/2025 | **Chart.js Fix:** Prevented double initialization. |
| v103 | 12/20/2025 | **ASCII Filename.** |
| v102 | 12/20/2025 | **Team Column Fix** (Org Chart mappings). |
| v101 | 12/20/2025 | **4-File Architecture Migration** (initial). |
| v100 | 12/20/2025 | **Infrastructure Updates:** Repository path and filename changes. |
| v99 | 12/19/2025 | **Tasks Dashboard - Combined Work Log Timeline.** |
| v98 | 12/18/2025 | **Tasks Dashboard - Team Summary & Work Log Enhancements.** |
| v97 | 12/17/2025 | **Tasks Dashboard - Sticky Header & Filters.** |
| v96 | 12/17/2025 | **Tasks Dashboard - Work Log Summary & Gantt Timeline.** |
| v95 | 12/17/2025 | **Bugs Dashboard - Architecture Diagram Readability.** |
| v94 | 12/17/2025 | **Bugs Dashboard - Architecture Diagram.** |
| v93 | 12/17/2025 | **Bugs Dashboard Enhancements:** Stat cards, Bug Type column, column resize persistence. |
| v92 | 12/17/2025 | **Date Timezone Fix:** `parseLocalDate()` for correct date display. |
| v91 | 12/16/2025 | **Bugs Dashboard Redesign:** Generic relationship pills in all tables. |
| v90 | 12/16/2025 | **Generic Tag Filter.** ER Prioritization Summary. Pipe-separated ID search. |
| v89 | 12/16/2025 | **Consistent Filter Display:** `formatFilterDisplay()` helper. State persistence fix. |
| v88 | 12/16/2025 | **Refresh Experience & Column Width Persistence.** Chart cross-filtering fix. |
| v87 | 12/16/2025 | **Generic Table Component:** `buildGenericTable()`. Release filter fix. |
| v86 | 12/15/2025 | **Filter Standardization:** Wider dropdowns, search boxes, cross-filtering. |
| v85 | 12/15/2025 | **Generic Priority/State/Team Filters.** Filter order standardized. |
| v84 | 12/14/2025 | **Generic Search & Customer Filters.** |
| v83 | 12/14/2025 | **Generic Release Filter.** |
| v82 | 12/14/2025 | **Customers Dashboard - Work Item Relationships.** |
| v81 | 12/13/2025 | **Customers Dashboard Enhancements:** Dates, resizable columns, DEV/PROD localStorage. |
| v80 | 12/13/2025 | **Customers Dashboard Redesign.** |
| v79 | 12/12/2025 | **State persistence for all views.** |
| v78 | 12/11/2025 | **Roadmap Priority Filter & Column.** Collapsible Team Summary. |
| v77 | 12/11/2025 | **Roadmap OKR Summary** effort percentages. |
| v76 | 12/10/2025 | **Roadmap view restructure** with OKR Summary. |
| v75 | 12/10/2025 | **Roadmap Tags column.** State persistence via localStorage. |
| v74 | 12/9/2025 | **Roadmap Release Version filter.** |
| v73 | 12/9/2025 | **Roadmap Effort column.** Team cards clickable. |
| v72 | 12/9/2025 | **Releases search filter.** Chart highlighting. |
| v71 | 12/9/2025 | **Roadmap tag filtering** refactor. |
| v70 | 12/8/2025 | **Releases searchable dropdowns.** Validation Data Source section. |

---

## License

Proprietary - eShare Inc. All rights reserved.
