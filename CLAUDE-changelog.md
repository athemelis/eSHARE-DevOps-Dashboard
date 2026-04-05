# Version History

Historical version summaries for the eShare DevOps Dashboard. Reference for understanding past changes.

## v85 (December 2024)
**Generic Priority, State, and Team Filter Components**

Created shared filter components in part2.html:
- **Priority:** P1-P4 with counts, "(No Priority)" last, 200px dropdown
- **State:** Semantic order (STATE_ORDER constant), "(No State)" last
- **Team:** Alphabetical, "(No Team)" last

Functions added for each: `compute*Info()`, `build*FilterDropdown()`, `handle*Change()`, `selectAll*()`, `clear*()`, `update*Display()`, `sync*Filter()`

Cross-filter behavior implemented for all generic filters. Filter order standardized across dashboards.

---

## v84 (December 2024)
**Generic Search and Customer Filter Components**

- **Search:** Title (case-insensitive) + ID matching, pipe-separated ID support for Roadmap
- **Customer:** "(No Customer)" first, item counts, 280px dropdown, alphabetical

Refactored Releases, Roadmap, and Customers to use generic components.

---

## v83 (December 2024)
**Generic Release Filter Component**

- Shared across Releases, Roadmap, Customers dashboards
- Shows release version + target date (280px wide)
- "⚠️ Needs Release" warning category for items with date but no release
- Release filter moved to position 2 (after Search)

---

## v79 (December 2024)
**State Persistence for ALL Dashboard Views**

Extended localStorage persistence to all views (24-hour expiration):
- Executive: Team/Type dropdowns, chart filters
- Customers: Team filter, chart filters
- Bugs: Date range, State/Type/Priority filters
- Teams: Time period, team details, engineer selection
- Tasks/Details/Validation: Type, team, state filters

Key pattern: Sync UI → Re-render with filters (not just sync alone).

---

## v78 (December 2024)
**Roadmap Dashboard - Priority Filter & Collapsible Sections**

- Priority filter (P1-P4 format) between Iteration and Release filters
- Priority column in table (sortable)
- Team Summary section collapsible (collapsed by default)
- Collapse state persisted via localStorage

---

## v77 (December 2024)
**Roadmap Dashboard - OKR Summary Effort Percentage**

- Effort row shows percentage as primary value, days as secondary
- Filter-aware: percentages recalculate based on filtered data
- Display: "45% 12.5d"

---

## v76 (December 2024)
**Roadmap Dashboard - Three-Section Restructure**

1. **OKR Summary:** 4 columns for strategy categories (1:, 2:, 3:, 4: tag prefixes)
2. **Team Summary:** Team effort cards
3. **Feature Details:** Table with ADO backlog link

OKR features:
- Clickable feature counts filter by category tags
- Footer shows untagged feature count
- Error for features in multiple categories

---

## v75 (December 2024)
**Roadmap Dashboard - Tags & State Persistence**

- Tags column (sortable, 150px, ellipsis overflow)
- localStorage state persistence (24-hour expiration)
- Default filters removed (Release, Tag start empty)
- AND/OR toggle for Tag filter

---

## v74 (December 2024)
**Roadmap Dashboard - Release Version Filter**

- Release filter dropdown (was hardcoded)
- Dual-mode: inclusion for manual, exclusion after Select All
- Release column in table (sortable, 120px)
- Bug fix: Team + Iteration now require matching SAME slice
- Bug fix: Effort column sorting uses effortMap

---

## v73 (December 2024)
**Roadmap Dashboard - Team-Centric UX**

- ADO Feature Backlog link
- Clickable team cards (filter by team)
- Effort column (sum of child slices)
- Filtered effort calculations
- Total row at table bottom
- Popup improvements: matching slices at top, non-matching grayed

---

## v72 (December 2024)
**Releases & Roadmap - UX Improvements**

- Search filter on Releases (title + ID)
- Label elements for clickable checkbox rows
- Scroll position preserved in dropdowns
- Tag filter AND logic
- Flex: 1 for filter dropdowns
- Standardized info popups

---

## v71 (December 2024)
**Roadmap View - Tag Filter Refactor**

- Base filter: Features with no Release Version
- "Candidate" tag default (user-controllable)
- Dual-mode tag filter
- Clear All preserves defaults
- Compact sticky header
- 140px dropdown width

---

## v70 (December 2024)
**Infrastructure & Validation**

- `-p/--publish` flag for output destination
- DEV output: local directory
- PROD output: SharePoint
- Retry logic (5 attempts, exponential backoff)
- Data Source Validation section
- Dropdown search for releases
- Scroll-to-close for dropdowns
