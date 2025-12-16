# eShare DevOps Dashboard

## Current Version: v88

---

## Quick Start (Local Execution)

### Prerequisites
- Python 3.9+ installed
- pandas library (`pip3 install pandas`)

### Folder Structure
After extracting the package, your folder should look like:
```
Your SharePoint Folder/
├── Templates/
│   ├── dashboard_v3_part1.html
│   ├── dashboard_v3_part2.html
│   ├── dashboard_v3_part3.html
│   ├── dashboard_v3_part4.html
│   └── dashboard_v3_template.html
├── generate_dashboard.py
├── DASHBOARD_README.md
├── ALL_Items.csv              ← Your data (managed by Power Automate)
├── Org_Chart.csv              ← Your org chart data
└── ᵉShare DevOps Dashboard.html  ← Generated output
```

### Running the Script

**Simple run** (all files in current directory):
```bash
cd "/path/to/your/folder"
python3 generate_dashboard.py
```

**With custom CSV location:**
```bash
python3 generate_dashboard.py -c "../ALL Items.csv"
```

**Full run with all paths specified:**
```bash
python3 generate_dashboard.py \
    -c "/path/to/ALL Items.csv" \
    -g "/path/to/Org_Chart.csv" \
    -t "./Templates" \
    -o "./ᵉShare DevOps Dashboard.html"
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --csv` | Path to ALL_Items.csv | SharePoint `ALL Items.csv` |
| `-g, --org` | Path to Org_Chart.csv | SharePoint `Org Chart.csv` |
| `-t, --templates` | Folder containing template files | `./Templates` |
| `-o, --output` | Output HTML file path (for local testing) | Local repo directory |
| `-p, --publish` | Publish to SharePoint instead of local | Off (local mode) |
| `-h, --help` | Show help message | |

### Refresh Timestamp
The refresh timestamp in the dashboard header is **automatically read from the CSV file's last modified date**. No manual editing required!

---

## Version vs. Refresh Timestamp

| Indicator | Meaning | When to Update |
|-----------|---------|----------------|
| **Version** (e.g., v64) | Code/template changes | Only when JavaScript, CSS, or HTML structure changes |
| **Refresh** timestamp | Data freshness | Automatic - reads from CSV file's modified date |

---

## Workflows

### Data Refresh (Automated via Power Automate)
1. Power Automate updates `ALL_Items.csv` every minute
2. Run `python3 generate_dashboard.py`
3. Dashboard HTML is regenerated with fresh data and timestamp
4. SharePoint versions the HTML file automatically

### Code Changes (Via Claude)
1. Work with Claude to make template/script changes
2. Download new `eShare_DevOps_Dashboard.zip` from Claude
3. Extract to your SharePoint folder (overwrites `Templates/` and `generate_dashboard.py`)
4. Run `python3 generate_dashboard.py` to regenerate with your current data
5. SharePoint versions all files automatically

---

## Continuing Development with Claude

### Standard Prompt (code changes, questions):
```
I'm continuing development on the eShare DevOps Dashboard.

**Uploaded Files:**
1. eShare_DevOps_Dashboard.zip (current version)

Please:
1. Extract the package to /mnt/user-data/outputs/
2. Check /mnt/transcripts/journal.txt for recent session history
3. [Your request here]
```

### Debugging Prompt (when data validation needed):
```
I'm continuing development on the eShare DevOps Dashboard.

**Uploaded Files:**
1. eShare_DevOps_Dashboard.zip (current version)
2. ALL_Items.csv (for debugging)
3. Org_Chart.csv (if relevant)

Please:
1. Extract the package to /mnt/user-data/outputs/
2. Copy CSV files to /mnt/user-data/outputs/
3. Check /mnt/transcripts/journal.txt for recent session history
4. [Your request here - e.g., "Work item 631 shows wrong date, please investigate"]
```

---

## Package Contents

The zip package contains **code files only** (no data):

```
eShare_DevOps_Dashboard.zip
├── Templates/
│   ├── dashboard_v3_part1.html    # HTML + CSS + header
│   ├── dashboard_v3_part2.html    # Core JS + data placeholder
│   ├── dashboard_v3_part3.html    # Releases, Customers, Bugs views
│   ├── dashboard_v3_part4.html    # Teams, Org Chart, Validation views
│   └── dashboard_v3_template.html # Concatenated template
├── generate_dashboard.py          # Generation script
└── DASHBOARD_README.md            # This file
```

**NOT included in package:**
- `ALL_Items.csv` - Managed by Power Automate
- `Org_Chart.csv` - Managed separately  
- `ᵉShare DevOps Dashboard.html` - Regenerated locally

---

## Data Schema Reference (CRITICAL)

The dashboard JavaScript expects these exact field names. **Do not change these:**

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

### CSV Column Formats Supported

The script auto-detects and supports both formats:

| Format | Example Column | Source |
|--------|---------------|--------|
| **ADO Field Names** | `System.WorkItemType` | Power Automate exports |
| **Friendly Names** | `Work Item Type` | Analytics View exports |

### Date Handling

| Field | Format | Notes |
|-------|--------|-------|
| `targetDate` | Date only (`2025-12-31`) | Converted from UTC to Athens timezone |
| `createdDate`, `stateChangeDate`, `closedDate` | ISO datetime | `2025-09-11T22:18:10` |

---

## Validation Checks

The generation script includes:

1. **Column format detection** - Auto-detects ADO field names vs friendly names
2. **Placeholder validation** - Fails if placeholders remain in output
3. **Schema validation** - Warns if expected fields are missing
4. **Size check** - Warns if output < 3MB (expected ~5MB with data)

---

## Troubleshooting

### "Data isn't populating" / Charts show zeros

1. Open browser console (F12)
2. Look for JavaScript errors
3. Check that generation script reports "Validation passed"
4. Verify file size is ~5MB (not ~350KB)

### Script can't find files

Check your paths:
```bash
# See what's in current directory
ls -la

# See what's in Templates folder
ls -la Templates/

# Run with explicit paths
python3 generate_dashboard.py -c "./ALL_Items.csv" -t "./Templates"
```

### Missing pandas

```bash
pip3 install pandas
```

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v88 | 12/16/2025 | **Refresh Experience Improvements:** Fixed momentary Executive dashboard flash on page refresh (removed hardcoded `active` class from HTML, now set by JavaScript from localStorage). Added automatic background refresh every 60 seconds to keep data current without manual refresh. **Column Width Persistence:** Added column width persistence for Roadmap table (Releases and Customers already had this). All three dashboards now persist column widths across refreshes and sessions via localStorage. **Releases Dashboard Chart Fix:** Fixed cross-filtering bug where selecting a release AND another filter (e.g., Team) caused all releases with matching items to highlight instead of just the selected release. Now only selected releases are highlighted; filter-match highlighting only applies when no releases are selected. |
| v87 | 12/16/2025 | **Generic Table Component:** Created `buildGenericTable()` function providing reusable table rendering with resizable columns, sorting, copy/export functionality, and row click handling. Used by Releases, Roadmap, and Customers dashboards. **Releases Dashboard:** Feature table rows now clickable (shows related items). Column widths persist across refresh via localStorage. All 4 tables (Features, Issues, Customer Bugs, Internal Bugs) use generic table component. **Roadmap Dashboard:** Section 3 header shows "⭐ Feature Details (X of Y)" with dynamic count. ADO link moved to section header. Table uses generic component with `hideTitleBar` option. **Customers Dashboard:** Uses generic table component with relationship display. **Release Filter Fix:** "(No Release)" and "(Needs Release)" options now always visible in dropdown (even with 0 count), appearing at top below search box. Works consistently across all dashboards. |
| v86 | 12/15/2025 | **Filter Standardization:** Updated dashboard-specific filters to match generic filter component pattern (wider dropdowns, search boxes, item counts, cross-filtering). **Releases Dashboard:** Type filter (200px) and Bug Type filter (260px) now have search boxes, item counts, and full cross-filter support. **Roadmap Dashboard:** Iteration filter (220px), Tag filter (280px), and Assigned To filter (250px) now have item counts and full cross-filter support. Removed `dataset.populated` caching so dropdowns rebuild dynamically for cross-filtering. **Customers Dashboard:** Category filter (220px) and Aging filter (180px) now have item counts and full cross-filter support. **Removed Team filter** from Customers dashboard (single team represented). |
| v85 | 12/15/2025 | **Generic Priority Filter Component:** Created shared Priority filter in part2.html for Releases, Roadmap, and Customers dashboards. Shows P1, P2, P3, P4 with item counts (sorted numerically), "(No Priority)" option last with count. Includes search box at top, 200px wide dropdown. Cross-filter aware. **Generic State Filter Component:** Created shared State filter in part2.html for same dashboards. States sorted semantically (New → Triaged → To Do → In Progress → Ready For Review → Done → Closed → Removed). Shows "(No State)" option last with count. 200px wide dropdown with search box. Full cross-filter support. **Generic Team Filter Component:** Created shared Team filter in part2.html for same dashboards. Teams sorted alphabetically, "(No Team)" option last with count. 200px wide dropdown with search box. Full cross-filter support. Roadmap extracts teams from delivery slices' areaPath. **Filter Order Standardized:** All 3 dashboards now follow consistent order: Search → Release → Customer → Priority → State → Team → dashboard-specific filters. **All Dashboards:** All generic filter dropdowns now rebuild dynamically each render for cross-filter behavior. |
| v84 | 12/14/2025 | **Generic Search Filter Component:** Created shared Search filter in part2.html for Releases, Roadmap, and Customers dashboards. Searches Title (case-insensitive) and ID (exact match). Roadmap supports pipe-separated IDs (`123\|456\|789`). **Generic Customer Filter Component:** Created shared Customer filter in part2.html for same dashboards. Shows "(No Customer)" first with count, item counts next to each customer, 280px wide dropdown with search box, alphabetically sorted. **Functions added:** Search: `applyGenericSearchFilter()`, `handleGenericSearchChange()`, `clearGenericSearch()`, `getGenericSearchValue()`, `syncGenericSearchFilter()`, `hasGenericSearchFilter()`. Customer: `computeCustomerInfo()`, `buildCustomerFilterDropdown()`, `filterGenericCustomerOptions()`, `handleGenericCustomerChange()`, `selectAllGenericCustomer()`, `clearGenericCustomer()`, `updateGenericCustomerDisplay()`, `syncGenericCustomerFilter()`. |
| v83 | 12/14/2025 | **Generic Release Filter Component:** Created shared Release filter component used by Releases, Roadmap, and Customers dashboards. Shows release version + target date in dropdown (280px wide). Includes "⚠️ Needs Release" warning category for items with target date but no release version. **(No Release)** category for items with neither. **Filter order standardized:** Release filter now appears immediately after Search filter on Roadmap and Customers dashboards for consistency. **Infrastructure:** Added Generic Filter Components documentation to CLAUDE.md with step-by-step guide for adding filters to new dashboards and creating new generic components. |
| v82 | 12/14/2025 | **Customers Dashboard - Work Item Relationships:** Integrated WorkItemLinks.csv (from Azure DevOps Analytics OData API) to display comprehensive relationship data. Clicking any row opens a modal showing all relationships grouped by Parent, Children, and Related items. Added visual relationship pills in table showing "has parent" (orange), "X children" (cyan), "X related" (purple), or "no links" (gray). **Column changes:** Removed Created Date and Closed Date columns, added Ticket Category column with color-coded badges. **Bug fixes:** Fixed Issue 617 not clickable (double quotes in title), fixed 14 issues showing TBD aging (ISO dates with fractional seconds). **Infrastructure:** Added WorkItemLinks.csv processing to generate_dashboard.py with `-l/--links` argument. |
| v81 | 12/13/2025 | **Customers Dashboard Enhancements:** Added Created and Closed date columns (with Athens timezone fix for accurate dates). Added resizable columns with persistent widths via localStorage. Default sort by Aging (ascending) with Reset Sort button. Sticky column headers when scrolling. **Infrastructure:** Separated DEV/PROD localStorage keys to prevent state leakage between environments. |
| v80 | 12/13/2025 | **Customers Dashboard Redesign:** Complete redesign focused on Issues only. **New sticky header filters:** Search, Customer, Category, State, Priority, Release, and Aging filters with searchable dropdowns. **Aging feature:** Added aging calculation based on DAX logic (buckets: 1 day, 1 week, 2 weeks, 4 weeks, Older, TBD). Added Aging column to table (between Priority and Tags) with color-coded badges. Added Aging histogram with Y-axis showing distribution. Histogram bars are clickable to filter. **Clickable Insights:** "Open issues", "New", "Triaged", and "In Progress" counts now clickable to filter by state. **UI improvements:** Moved "Showing X issues" to top of table, auto-adjusting table height (scroll mode for >20 items), clickable stat cards filter by Ticket Category. **Infrastructure:** Separated DEV and PROD template directories to prevent accidental production updates during development. |
| v79 | 12/12/2025 | **State persistence for all views:** Extended localStorage state persistence (originally from v75 Roadmap) to ALL dashboard views. **Executive:** Team/Type header dropdowns and chart filters now persist. **Customers:** Team filter and chart filters persist. **Bugs:** Date range selection, custom date inputs, trend filters (State/Type/Priority), and categorization chart filters all persist. **Teams:** Time period, team details selection, and engineer filter selection persist. **Tasks:** Parent type, team, and state filters persist. **Details:** Type, team, and state filters persist. **Validation:** Type, team, and state filters persist. **Releases:** Already working in v78. Filter state survives page refresh, uses 24-hour expiration. |
| v78 | 12/11/2025 | **Roadmap Priority Filter & Column:** Added Priority filter dropdown to sticky header (between Iteration and Release). Added Priority column to Feature Details table (after Customers). Values displayed as P1, P2, etc. **Collapsible Team Summary:** Section 2 is now collapsible and collapsed by default. Click header to expand/collapse. Collapse state persisted via localStorage. |
| v77 | 12/11/2025 | **Roadmap OKR Summary:** Effort row now shows percentage as primary value (proportion of total effort across all 4 OKR categories), with days shown as secondary value in smaller muted text. Percentages are filter-aware - if filters result in all effort in one category, that category shows 100%. |
| v76 | 12/10/2025 | **Roadmap view restructure:** Reorganized into 3 sections: (1) OKR Summary - strategy alignment table with 4 columns for OKR categories (tags starting with 1:, 2:, 3:, 4:), showing feature counts and effort sums. Feature counts are clickable to filter by that OKR category. Footer shows count of features without OKR tags. Error message for features in multiple categories. (2) Team Summary - existing team effort cards. (3) Feature Details - feature table with ADO backlog link. All sections respond to header filters. Clicking OKR counts preserves existing filters (only updates Tag filter). |
| v75 | 12/10/2025 | **Roadmap view:** Added Tags column (after Customers). **State persistence:** View and filter selections now preserved across page refreshes via localStorage. **Filter changes:** Removed default values for Release and Tag filters (all start empty). Added AND/OR toggle to Tag filter dropdown for flexible multi-tag filtering. |
| v74 | 12/9/2025 | **Roadmap view:** Added Release Version filter dropdown (between Iteration and Tag filters). Default filter is "(No Release)" to show Features with no release version assigned. Dual-mode filter behavior. Added Release column to table (between Assigned To and Effort). **Bug fixes:** Team + Iteration filters now correctly require slices to match BOTH filters; Effort column sorting now works correctly. |
| v73 | 12/9/2025 | **Roadmap view:** Added "Link to ADO Feature Backlog" hyperlink. Team cards now clickable (filters by team, syncs with dropdown). Added Effort column to table (sum of child delivery slice efforts). Added total row with effort sum. Team AND Iteration filters now combine to show filtered effort (e.g., Analytics + CY2025Q4-Dec). Delivery Slices popup: matching slices at top, others grayed out, effort summary shows filtered vs total. |
| v72 | 12/9/2025 | **Releases view:** Added search filter (title/ID), chart highlighting for filtered results, Release Version column in tables, Bug Type filter now excludes Features/Issues. **Roadmap view:** Search placeholder updated, Tag filter AND logic. **Both dashboards:** Label-based checkbox filters (full row clickable), scroll position preserved on dropdown re-render, flexible filter widths (`flex: 1`), standardized "ℹ️ Info" popups. **Patterns:** Documented UI patterns in CLAUDE.md for reuse. |
| v71 | 12/9/2025 | **Roadmap view:** Refactored tag filtering - "Candidate" now selected by default in Tag dropdown (user-controllable), dual-mode filter (inclusion/exclusion), Clear All preserves Candidate default, Clear button hidden in default state. Compact sticky header, wider filter dropdowns (140px). **Pattern:** Documented dual-mode filter and default filter state patterns for future use. |
| v70 | 12/8/2025 | **Releases view:** Added searchable dropdowns for Release, Team, and Customer filters (type to filter long lists), scroll-to-close for filter dropdowns, fixed sticky header Clear button wrapping, fixed stat cards hover effect (now non-clickable). **Validation view:** Added Data Source Validation section comparing CSV source counts vs dashboard counts. **Infrastructure:** Added `-p/--publish` flag for local vs production workflow, added retry logic for OneDrive file locks, added `reload-launchd-agent.sh` helper script. |
| v69 | 12/6/2025 | Bug fixes: Added null checks to updateSelectionInfo, renderDrilldown, and closeDrilldown functions to prevent errors when drilldown panel element doesn't exist (removed in v68). |
| v68 | 12/6/2025 | Releases view: (1) Stat cards now update dynamically based on active filters. (2) Removed stat card drilldown feature. (3) Added Customer filter to header. (4) Filters update view immediately while dropdown stays open. (5) Cross-filter aware dropdowns show only options available in current filtered context. |
| v67 | 12/6/2025 | Releases view: Replaced doughnut charts with header filters (Type, Bug Type, State, Team). Full bar chart when no filters, mini-bar when any filter active. Added "Clear All" button. Chart header pattern: title + subtitle on same line. Fixed dropdown behavior for Select All/Clear. |
| v66 | 12/6/2025 | Releases view: Implemented sticky two-row header with view navigation and filter row. Moved "How is release progress calculated?" to expandable info panel in header. |
| v65 | 12/6/2025 | Restructured package: Templates in subfolder, code-only zip (no CSVs/HTML), removed -p package option from script, auto-refresh timestamp from CSV modified date, simplified command-line args. |
| v64 | 12/5/2025 | Support for ADO field names (System.*, Microsoft.VSTS.*, Custom.*) from Power Automate exports. Legacy friendly names still supported. Target dates now converted from UTC to Athens timezone to match ADO display. Local execution with command-line arguments. |
| v63 | 12/5/2025 | Org chart data now dynamically loaded from Org_Chart.csv instead of hardcoded. |
| v62 | 12/4/2025 | Bug fix: State filter in Engineer Workload section now dynamically populated from actual work item states. |
| v61 | 12/3/2025 | Team Details: Added Work Item Type filter to Engineer Workload section. |
| v60 | 12/3/2025 | Team Details: Added team member coverage indicator. |
| v59 | 12/3/2025 | Team Details: Added State and Priority multi-select filters to Engineer Workload section. |
| v58 | 12/3/2025 | Added "All Teams" card showing aggregated totals across all teams. |
| v57 | 12/3/2025 | Teams view filtering: Time period filter now applies to all 8 visuals. Added "Last Week" time period. |
| v56 | 12/3/2025 | Teams view layout: Moved CTA and team cards below Work Item Distribution section. |
| v55 | 12/3/2025 | Engineer Workload: Replaced bar chart with matrix table (engineers × work item types). |
| v54 | 12/3/2025 | Engineer Workload: Dynamic chart height, added "Unassigned (?)" filter option. |
| v53 | 12/3/2025 | Engineer Workload: Fixed bar chart to show engineer's home team from Org Chart. |
| v52 | 12/2/2025 | Teams view redesign with Team Insights section. |
| v51 | 12/2/2025 | Multi-select chart filters across all views. |
| v50 | 12/2/2025 | Releases: Added Customers card. Bugs: Multi-select filters. |
| v48 | 12/1/2025 | Fixed targetDate to date-only format. |
| v47 | 12/1/2025 | Fixed schema (restored v45 compatibility), added validation. |

---

## Updating the Version (Code Changes)

When making code changes in Claude:

1. Increment `CURRENT_VERSION` in `generate_dashboard.py`
2. Update version in `Templates/dashboard_v3_part1.html`:
   ```html
   <span class="version">v65</span>
   ```
3. Update this README's version history
4. Download new zip package from Claude
5. Extract to your SharePoint folder
6. Run `python3 generate_dashboard.py` to regenerate
