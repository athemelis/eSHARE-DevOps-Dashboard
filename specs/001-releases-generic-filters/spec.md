# Feature Specification: Releases Dashboard Generic Filter Migration

**Feature Branch**: `001-releases-generic-filters`  
**Created**: 2026-04-01  
**Status**: Draft  
**Constitution**: v1.1.0  
**Input**: User description: "Migrate Releases Dashboard from legacy inline filter code to generic filter infrastructure (populateGenericFilterDropdowns, applyGenericSecondaryFilters, DASHBOARD_FILTER_REGISTRY). The Teams2 dashboard is the gold standard for a fully-migrated dashboard."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter Dropdowns Show Correct Cross-Filtered Counts (Priority: P1)

A dashboard user opens the Releases Dashboard and clicks on any filter dropdown (Customer, Priority, State, Tag, Team, Assignee, Bug Owner). The dropdown options display accurate item counts that reflect all OTHER currently active filters, exactly as they do on the Teams, Bugs, and Customers dashboards.

**Why this priority**: Cross-filtered counts are the core user-facing value of the generic infrastructure. Without accurate counts, users make filtering decisions based on stale or incorrect numbers.

**Independent Test**: Open Releases Dashboard. Select a Customer filter (e.g., "Acme Corp"). Open the State dropdown and verify counts reflect only Acme Corp items. Open the Priority dropdown and verify counts reflect only Acme Corp items. Counts should match the actual number of items visible in the tables.

**Acceptance Scenarios**:

1. **Given** the Releases Dashboard is loaded with no active filters, **When** the user opens any filter dropdown, **Then** each option shows the total count of items matching that option value across all release items.
2. **Given** a Customer filter is active, **When** the user opens the State dropdown, **Then** the counts beside each state option reflect only items belonging to the selected customer.
3. **Given** multiple filters are active (Customer + Priority), **When** the user opens the Tag dropdown, **Then** the counts reflect items matching BOTH the Customer AND Priority filters.
4. **Given** any filter combination is active, **When** the user opens that same filter's dropdown, **Then** the counts are NOT affected by the current filter's own selection (cross-filter exclusion).

---

### User Story 2 - Clear All Filters Resets Everything (Priority: P1)

A dashboard user has multiple filters active and clicks "Clear Filters". All filter selections reset, all dropdown display texts return to their default labels, and the tables show unfiltered data.

**Why this priority**: Clear Filters is the primary escape mechanism when users get lost in complex filter combinations. If it doesn't fully reset state, users must manually clear each filter or reload the page.

**Independent Test**: Apply 3+ different filters. Click "Clear Filters". Verify all dropdown labels show defaults, all tables show unfiltered data, and the Clear button is hidden.

**Acceptance Scenarios**:

1. **Given** multiple filters are active (Search, Customer, State, Tag), **When** the user clicks "Clear Filters", **Then** all filter selections are cleared, all dropdown display texts show default labels, and tables show all items.
2. **Given** the user clears filters, **When** they refresh the page, **Then** filters remain cleared (state persistence captures the cleared state).
3. **Given** text is in the search box and filters are active, **When** the user clicks "Clear Filters", **Then** the search box is also cleared.

---

### User Story 3 - Individual Filter Operations Work Correctly (Priority: P1)

A dashboard user can select/deselect individual options, use "Select All", and use "Clear" within each filter dropdown. The tables update immediately and the dropdown collapsed text updates to reflect the current selection.

**Why this priority**: Individual filter manipulation is the most frequent user interaction with the filter system. Broken select/deselect or stale collapsed text undermines daily usability.

**Independent Test**: Open the State dropdown. Select "Active" only. Verify collapsed text shows "Active" and tables filter to active items only. Click "Select All". Verify all states are selected. Click "Clear". Verify no states selected.

**Acceptance Scenarios**:

1. **Given** a filter dropdown is open, **When** the user checks a single option, **Then** the tables re-render showing only matching items, and the collapsed dropdown text updates to show the selected value.
2. **Given** a filter dropdown is open with some options checked, **When** the user clicks "Select All", **Then** all options are checked, tables show all items (for that filter), and collapsed text returns to the default label.
3. **Given** a filter dropdown has selections, **When** the user clicks "Clear", **Then** all options are unchecked, tables re-render, and collapsed text updates accordingly.

---

### User Story 4 - State Persistence Across Refresh and Auto-Refresh (Priority: P2)

A dashboard user's filter selections survive page refresh, manual refresh (↻ button), and the 60-second auto-refresh cycle without visual disruption.

**Why this priority**: The dashboard auto-refreshes every 60 seconds. If filter state is lost, users are forced to re-apply their filters repeatedly.

**Independent Test**: Apply Customer + Priority filters. Wait for an auto-refresh cycle (60 seconds). Verify the same filters are still active. Hard-refresh the page. Verify filters are restored from localStorage.

**Acceptance Scenarios**:

1. **Given** the user has active filters, **When** an auto-refresh cycle triggers, **Then** all filter selections are preserved and the tables re-render with the same filters applied.
2. **Given** the user has active filters, **When** they hard-refresh the page, **Then** filter selections are restored from localStorage.
3. **Given** the user switches away from Releases to another dashboard tab and back, **Then** filter selections are preserved.

---

### User Story 5 - Releases-Specific Filters Continue Working (Priority: P2)

The Releases Dashboard has filters not shared with other dashboards: Type (Feature/Issue/Bug), Bug Type (Customer Bug/Internal Bug), and Progress Status. These continue to function correctly after migration, coexisting with the generic filters.

**Why this priority**: These are Releases-specific filters that form part of the daily workflow for release managers who filter by work item type or progress status.

**Independent Test**: Select Type = "Bug". Verify only bugs appear. Select Bug Type = "Customer Bug". Verify only customer bugs. Select Progress Status = "Slightly Over". Verify only 100-120% progress items appear.

**Acceptance Scenarios**:

1. **Given** the Releases Dashboard is loaded, **When** the user selects Type = "Feature", **Then** only Features appear in release tables.
2. **Given** Type = "Bug" is selected, **When** the user selects Bug Type = "Customer Bug", **Then** only Customer Bugs appear.
3. **Given** Progress Status = "On Track" is selected alongside a Customer filter, **Then** both filters combine (AND logic) to show only on-track items for that customer.
4. **Given** all Releases-specific filters plus generic filters are active, **When** the user clicks "Clear Filters", **Then** all filters including Releases-specific ones are cleared.

---

### User Story 6 - No Behavioral Regression (Priority: P2)

Everything that worked before the migration continues to work identically. The Items by Release chart, release period filter, search with deep search popup, tag exclusion mode, tag logic mode (AND/OR), and all table interactions remain functional.

**Why this priority**: This is a pure refactoring migration — the user should notice zero behavioral differences.

**Independent Test**: Compare behavior of every filter and interaction before and after migration. Pay special attention to: tag exclusion toggle, tag AND/OR toggle, search with deep search popup, chart filter highlighting, and table sort persistence.

**Acceptance Scenarios**:

1. **Given** a tag filter is active, **When** the user toggles tag exclusion mode, **Then** items WITH that tag are hidden instead of shown.
2. **Given** multiple tags are selected, **When** the user toggles tag logic to AND, **Then** only items with ALL selected tags appear.
3. **Given** the user types in the search box, **When** the search term matches items in collapsed release sections, **Then** the deep search popup appears.
4. **Given** filters are active, **When** the Items by Release chart renders, **Then** bars matching active filters are highlighted.

---

### Edge Cases

- What happens when zero items match all active filters? Tables should show an empty state message and filter counts should reflect zero.
- What happens when a filter dropdown has only one option? It should render correctly with the single option checkable.
- What happens when auto-refresh brings new data that changes available filter options? New options appear; removed options disappear; existing selections for still-valid options are preserved.
- What happens when a user has stale localStorage with old singular key names (pre-migration)? On first load, old singular keys are read, written to new plural keys, and deleted. After this one-time migration, only plural keys exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `releaseHeaderFilters` object MUST use plural key names matching the generic convention: `customers`, `priorities`, `tags`, `states`, `teams`, `assignees`, `bugOwners`, `bugTypes`, `types` (replacing singular keys). Additionally, new keys `search: ''`, `releases: []`, and `bugOwners: []` MUST be added to the filter object to match the generic convention used by fully-migrated dashboards.
- **FR-002**: The `DASHBOARD_FILTER_REGISTRY` entry for `'releases'` MUST include `filters: () => releaseHeaderFilters` so generic handlers access filter state directly.
- **FR-003**: The `DASHBOARD_FILTER_REGISTRY` entry for `'releases'` MUST include `getFilteredItems` returning the currently filtered release items.
- **FR-004**: The inline `getItemsExcludingFilter()` calls inside `renderReleasesView()` MUST be replaced by a single `populateGenericFilterDropdowns()` call.
- **FR-005**: ALL filter dropdowns MUST use generic components: Assignee via `buildAssigneeFilterDropdown()`, Bug Type via modified `buildBugTypeFilterDropdown()` (consolidated from 3 raw ADO values to 2 derived categories: "Customer Bug" and "Internal Bug"), Bug Owner via existing `buildBugOwnerFilterDropdown()` (new to Releases), Type via new `buildTypeFilterDropdown()` (4 composite categories: Feature, Issue, Customer Bug, Internal Bug), Progress Status via new `buildProgressStatusFilterDropdown()`.
- **FR-006**: The `getHeaderFilteredReleaseItems()` function MUST delegate to `applyGenericSecondaryFilters()` for ALL filters. The generic function MUST be extended to handle `types`, `bugTypes`, and `progressStatus` filter keys.
- **FR-007**: All cross-filter counts MUST be accurate: each dropdown's option counts reflect items filtered by all OTHER active filters, excluding the dropdown's own filter.
- **FR-008**: "Clear Filters" MUST reset all filter state including Type, Bug Type, Bug Owner, Progress Status and persist the cleared state to localStorage.
- **FR-009**: Filter state MUST persist to localStorage and survive page refresh, auto-refresh, and dashboard tab switches.
- **FR-010**: Tag exclusion mode and tag logic mode (AND/OR) MUST continue to function correctly after migration.
- **FR-011**: The Items by Release chart MUST continue to highlight bars when filters are active.
- **FR-012**: Search filter including deep search popup MUST continue functioning through the generic `onSearchChange` handler.
- **FR-013**: Legacy localStorage state with old singular key names MUST be handled via a one-time migration on first load: read old singular keys, write values to new plural keys, delete old keys. No dual-format fallback logic is retained after migration.
- **FR-014**: Approximately 450 lines of legacy inline filter code MUST be removed, replaced by the generic infrastructure.
- **FR-015**: A Bug Owner filter dropdown MUST be added to the Releases Dashboard HTML (principle: dashboards with Bug tables must have both Bug Owner AND Bug Type filters).
- **FR-016**: A new generic `buildTypeFilterDropdown()` function MUST be created for work-item-type filtering (Feature/Issue/Bug variants). This is reusable by future dashboards (e.g., Executive).
- **FR-017**: A new generic `buildProgressStatusFilterDropdown()` function MUST be created for progress status filtering. This is reusable by Roadmap, Bugs, and Teams dashboards.
- **FR-018**: `applyGenericSecondaryFilters()` MUST be extended to handle `types`, `bugTypes`, `progressStatus`, and `teams` filter keys, so all registered dashboards can use them without custom post-processing.
- **FR-019**: `populateGenericFilterDropdowns()` MUST be extended to build `type`, `bugtype`, and `progressStatus` dropdowns when the corresponding `${dashboardId}-${type}-menu` elements exist in HTML.

### Key Entities

- **releaseHeaderFilters**: The filter state object for the Releases Dashboard, holding arrays of selected values for each filter type plus boolean/string flags for tag modes and progress status.
- **DASHBOARD_FILTER_REGISTRY**: Central registry mapping dashboard IDs to their filter configuration (filter accessor, render function, clear button handler, item accessors).
- **populateGenericFilterDropdowns**: Generic function that builds all filter dropdown HTML with cross-filtered counts for any registered dashboard. Extended to support `type`, `bugtype`, and `progressStatus` types.
- **applyGenericSecondaryFilters**: Generic function that applies the full set of filters (search, release, customer, priority, state, tag, team, bugOwner, assignee, bugType, type, progressStatus) to an item array.
- **buildTypeFilterDropdown**: New generic dropdown builder for composite work-item-type filtering. 4 options: Feature (`System.WorkItemType=Feature`), Issue (`System.WorkItemType=Issue`), Customer Bug (`System.WorkItemType=Bug AND Custom.BugType='Customer Related'`), Internal Bug (`System.WorkItemType=Bug AND (Custom.BugType='Product Quality' OR Custom.BugType='Technical & Infrastructure')`). Reusable by Executive Dashboard.
- **buildBugTypeFilterDropdown** (modified): Existing generic dropdown builder, changed from 3 raw ADO `Custom.BugType` values to 2 derived categories: "Customer Bug" (`Custom.BugType='Customer Related'`) and "Internal Bug" (`Custom.BugType='Product Quality' OR Custom.BugType='Technical & Infrastructure'`). Used by Bugs, Validation, Capacity, Reports, and Releases dashboards.
- **buildProgressStatusFilterDropdown**: New generic dropdown builder for progress status filtering. Reusable by Roadmap, Bugs, Teams dashboards.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cross-filter counts in every Releases Dashboard dropdown match the actual number of visible items when that filter value is the only active selection for its type.
- **SC-002**: Lines of inline filter code in `renderReleasesView()` related to dropdown building and `getItemsExcludingFilter()` are reduced by approximately 450 lines (±50 lines).
- **SC-003**: Releases Dashboard filter behavior is indistinguishable from the Teams Dashboard (teams2) for all shared filter types (Customer, Priority, State, Tag, Team, Assignee, Bug Owner).
- **SC-004**: All filter selections persist across auto-refresh cycles (60 seconds) without visual disruption or state loss.
- **SC-005**: Clearing filters resets all dropdown display texts to default labels and removes all filter selections within 1 user action.
- **SC-006**: No JavaScript console errors appear during any filter interaction on the Releases Dashboard.
- **SC-007**: The migration introduces zero behavioral regressions — every interaction that worked before continues to work identically after.

## Assumptions

- The existing generic infrastructure (`populateGenericFilterDropdowns`, `applyGenericSecondaryFilters`, `DASHBOARD_FILTER_REGISTRY`) is stable and fully functional, as validated by Teams2, Bugs, Customers, and other migrated dashboards.
- Type filter is made generic via new `buildTypeFilterDropdown()` — it will be reused by the Executive Dashboard in a future feature.
- Bug Type filter requires modification of the existing generic `buildBugTypeFilterDropdown()`. Currently shows 3 raw ADO picklist values ("Customer Related", "Product Quality", "Technical & Infrastructure"); must be consolidated to 2 derived categories ("Customer Bug", "Internal Bug"). This is a cross-dashboard change affecting Bugs, Validation, Capacity, and Reports dashboards.
- Bug Owner filter is already generic via `buildBugOwnerFilterDropdown()` (used by Bugs Dashboard). Added to Releases per principle: any dashboard with Bug tables must have both Bug Owner AND Bug Type filters.
- Progress Status filter is made generic via new `buildProgressStatusFilterDropdown()` — it will be reused by Roadmap, Bugs, and Teams dashboards in future features.
- `applyGenericSecondaryFilters()` is extended to handle `types`, `bugTypes`, and `progressStatus` filter keys so no dashboard needs custom post-processing for these filters.
- `populateGenericFilterDropdowns()` is extended to build `type`, `bugtype`, and `progressStatus` dropdown menus when the corresponding DOM elements exist.
- The `teamItemsBuilder` callback pattern (used by Teams2 for Feature→slice team mapping) can be reused for Releases, which also needs to map Features to Delivery Slice teams.
- Old singular key names in localStorage will be encountered by users who haven't cleared their browser storage; a one-time migration on first load reads old keys, writes to new plural keys, and deletes old keys.
- The Items by Release chart's filter highlighting logic will need to reference the new plural key names but otherwise remains unchanged.
- Search filter behavior (including deep search popup) is already handled by the `onSearchChange` handler in the registry and does not need additional migration work beyond key name updates.

## Clarifications

### Session 2026-04-01

- Q: How should legacy localStorage keys (old singular names) be handled when a user loads the migrated Releases Dashboard for the first time? → A: One-time migration — read old singular keys, write values to new plural keys, delete old keys on first load.

## Regression Test Plan *(mandatory per Constitution Principle VII)*

### 1. Direct Feature Tests
1. Open Releases Dashboard. Select Customer filter → verify dropdown counts update in State, Priority, Tag dropdowns (cross-filtering).
2. Select State = "Active" → verify only active items in tables, verify collapsed text shows "Active".
3. Click "Select All" in State dropdown → verify all states selected, tables show all items.
4. Click "Clear" in State dropdown → verify no states selected.
5. Apply Customer + Priority + State filters → click "Clear Filters" → verify all dropdowns reset to defaults, tables show all items, Clear button hidden.
6. Select Type = "Bug" → verify only bugs shown. Then select Bug Type = "Customer Bug" → verify only customer bugs. Then select Bug Owner → verify further filtering.
7. Select Progress Status = "Slightly Over" → verify only 100-120% progress items shown.
8. Type in search box → verify items filter, deep search popup appears for matches in collapsed sections.
9. Toggle tag exclusion mode → verify items WITH that tag are hidden. Toggle tag logic to AND → verify only items with ALL selected tags appear.
10. Verify Items by Release chart highlights bars when filters are active.

### 2. Cross-Dashboard Impact
This migration extends 3 generic functions (`populateGenericFilterDropdowns`, `applyGenericSecondaryFilters`, `buildTypeFilterDropdown`/`buildProgressStatusFilterDropdown`) and modifies 1 existing generic function (`buildBugTypeFilterDropdown` — 3→2 bucket consolidation). Verify on ALL dashboards that use them:
- **Teams2**: Open → apply Customer filter → verify counts correct. Clear filters → verify reset.
- **Bugs**: Open → apply Priority filter → verify counts correct. Verify Bug Owner dropdown still works. **Verify Bug Type dropdown shows 2 options ("Customer Bug", "Internal Bug") instead of old 3 values.** Select "Internal Bug" → verify both "Product Quality" and "Technical & Infrastructure" bugs appear.
- **Validation**: Open → verify Bug Type dropdown shows 2 options. Select "Customer Bug" → verify only Customer Related bugs shown.
- **Capacity**: Open → verify Bug Type dropdown shows 2 options. Verify filters function normally.
- **Reports**: Open → verify Bug Type dropdown shows 2 options if present.
- **Customers**: Open → apply State filter → verify counts correct.
- **Roadmap**: Open → apply Tag filter → verify counts correct.

### 3. Auto-Refresh Test
1. Open Releases Dashboard.
2. Apply Customer + Priority filters.
3. Wait 60 seconds for auto-refresh cycle.
4. Verify: same filters are active, dropdown texts unchanged, tables show same filtered data, no flash or layout jump.

### 4. State Persistence Test
1. Apply Customer + State + Tag filters on Releases Dashboard.
2. Hard-refresh the page (Cmd+Shift+R).
3. Verify: all 3 filters are restored from localStorage with correct selections.
4. Switch to another dashboard tab (e.g., Bugs) and back to Releases.
5. Verify: filters are preserved.
6. Clear localStorage, reload page. Verify: no errors, filters default to empty.

### 5. Theme Test
1. With Releases Dashboard open and filters applied, toggle from dark mode to light mode.
2. Verify: all filter dropdowns, collapsed text, Clear button, and table styling render correctly in both modes.
3. No hardcoded colors, all uses CSS custom properties.

### 6. Performance Check
1. Open Releases Dashboard with no filters.
2. Click "Clear Filters" — should be near-instant (< 1 second).
3. Apply 3+ filters, then click "Clear Filters" — should be near-instant.
4. Wait for auto-refresh — should complete without perceptible delay (< 2 seconds).
5. Open a filter dropdown with many options (e.g., Tag) — dropdown should render and display counts without lag.

### 7. Console Check
1. Open browser console (F12) before loading Releases Dashboard.
2. Load the dashboard. Verify: no JavaScript errors.
3. Apply and clear each filter type. Verify: no errors after each interaction.
4. Wait for an auto-refresh cycle. Verify: no errors.
5. Hard-refresh the page. Verify: no errors during state restoration.
