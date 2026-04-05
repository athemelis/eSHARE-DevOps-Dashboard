# Research: Releases Dashboard Generic Filter Migration

## Decision 1: Filter Key Name Mapping (Singular → Plural)

**Decision**: Rename all `releaseHeaderFilters` keys to match the generic convention.

**Mapping**:

| Current (singular) | New (plural) | Used by generic infrastructure |
|--------------------|-------------|-------------------------------|
| `customer` | `customers` | `applyGenericSecondaryFilters`, `buildCustomerFilterDropdown` |
| `priority` | `priorities` | `applyGenericSecondaryFilters`, `buildPriorityFilterDropdown` |
| `state` | `states` | `applyGenericSecondaryFilters`, `buildStateFilterDropdown` |
| `tag` | `tags` | `applyGenericSecondaryFilters`, `buildTagFilterDropdown` |
| `team` | `teams` | `applyGenericSecondaryFilters`, `buildTeamFilterDropdown` |
| `assignee` | `assignees` | `applyGenericSecondaryFilters`, `buildAssigneeFilterDropdown` |
| `type` | `types` | **New generic**: `buildTypeFilterDropdown` (to be created) |
| `bugtype` | `bugTypes` | **Already generic**: `buildBugTypeFilterDropdown` (used by Bugs Dashboard) |
| *(new)* | `bugOwners` | **Already generic**: `buildBugOwnerFilterDropdown` (used by Bugs Dashboard) |
| `tagExclusionMode` | `tagExclusionMode` | **No change** — already matches generic convention |
| `tagLogicMode` | `tagLogicMode` | **No change** — already matches generic convention |
| `progressStatus` | `progressStatus` | **New generic**: `buildProgressStatusFilterDropdown` (to be created) |

**Note**: `bugOwners` key must be ADDED to `releaseHeaderFilters`. Principle: any dashboard with Bug tables must have both Bug Owner AND Bug Type filters. The Bugs Dashboard already uses both `bugTypes` and `bugOwners` keys with generic components `buildBugTypeFilterDropdown()` and `buildBugOwnerFilterDropdown()`.

**Rationale**: The generic infrastructure reads filter state using plural keys (e.g., `filters.customers`). Without this rename, `populateGenericFilterDropdowns()` and `applyGenericSecondaryFilters()` would read `undefined`.

**Alternatives considered**: Adapter layer to map keys at runtime — rejected because it adds complexity and all other dashboards use plural keys directly.

## Decision 2: HTML Element ID Mapping

**Decision**: Rename all Releases filter HTML element IDs to match the generic `${dashboardId}-${type}-menu/display/dropdown` convention, where `dashboardId = 'releases'`.

**Mapping**:

| Current ID | New ID | Type |
|------------|--------|------|
| `release-filter-dropdown` | `releases-release-dropdown` | Container |
| `release-filter-menu` | `releases-release-menu` | Menu |
| `release-filter-display` | `releases-release-display` | Display text |
| `release-customer-header-dropdown` | `releases-customer-dropdown` | Container |
| `release-customer-header-menu` | `releases-customer-menu` | Menu |
| `release-customer-header-display` | `releases-customer-display` | Display text |
| `release-priority-header-dropdown` | `releases-priority-dropdown` | Container |
| `release-priority-header-menu` | `releases-priority-menu` | Menu |
| `release-priority-display` | `releases-priority-display` | Display text (already correct) |
| `release-state-header-dropdown` | `releases-state-dropdown` | Container |
| `release-state-header-menu` | `releases-state-menu` | Menu |
| `release-state-display` | `releases-state-display` | Display text (already correct) |
| `release-tag-dropdown` | `releases-tag-dropdown` | Container |
| `release-tag-menu` | `releases-tag-menu` | Menu |
| `release-tag-display` | `releases-tag-display` | Display text (already correct) |
| `release-team-header-dropdown` | `releases-team-dropdown` | Container |
| `release-team-header-menu` | `releases-team-menu` | Menu |
| `release-team-header-display` | `releases-team-display` | Display text |
| `release-assignee-dropdown` | `releases-assignee-dropdown` | Container |
| `release-assignee-menu` | `releases-assignee-menu` | Menu |
| `release-assignee-display` | `releases-assignee-display` | Display text |
| `release-type-header-dropdown` | `releases-type-dropdown` | Container (custom, stays) |
| `release-type-header-menu` | `releases-type-menu` | Menu (custom, stays) |
| `release-type-header-display` | `releases-type-display` | Display text (custom, stays) |
| `release-bugtype-header-dropdown` | `releases-bugtype-dropdown` | Container (custom, stays) |
| `release-bugtype-header-menu` | `releases-bugtype-menu` | Menu (custom, stays) |
| `release-bugtype-header-display` | `releases-bugtype-display` | Display text (custom, stays) |
| `release-progress-status-filter` | `releases-progress-status-filter` | Select (custom, stays) |
| `release-clear-filters-btn` | `releases-clear-filters-btn` | Button |

**Rationale**: `populateGenericFilterDropdowns()` looks up elements via `document.getElementById(dashboardId + '-' + type + '-menu')`. With `dashboardId = 'releases'`, it expects `releases-customer-menu`, `releases-state-menu`, etc. The current IDs use `release-` prefix with inconsistent `-header-` infixes.

**Reference**: teams2 pattern — all IDs follow `teams2-${type}-menu` exactly.

## Decision 3: Registry Entry Completion

**Decision**: Add `filters` and `getFilteredItems` to the existing `DASHBOARD_FILTER_REGISTRY` entry for `'releases'`.

**Current entry** (dashboard.js ~line 7465):
```javascript
registerDashboardFilters('releases', {
    label: 'Releases',
    render: () => renderReleasesView(),
    clearBtn: () => updateClearFiltersButton(),
    getAllItems: () => workItems.filter(w => ['Feature', 'Issue', 'Bug'].includes(w.type)),
    onSearchChange: (v) => { releasesSearchFilter = v; _lastDeepSearchPopupTerm = ''; updateClearFiltersButton(); saveStateToStorage(); renderReleasesView(); },
});
```

**New entry**:
```javascript
registerDashboardFilters('releases', {
    label: 'Releases',
    filters: () => releaseHeaderFilters,
    render: () => renderReleasesView(),
    clearBtn: () => updateClearFiltersButton(),
    getAllItems: () => workItems.filter(w => ['Feature', 'Issue', 'Bug'].includes(w.type)),
    getFilteredItems: () => getHeaderFilteredReleaseItems(workItems.filter(w => ['Feature', 'Issue', 'Bug'].includes(w.type))),
    onSearchChange: (v) => { releaseHeaderFilters.search = v; _lastDeepSearchPopupTerm = ''; updateClearFiltersButton(); saveStateToStorage(); renderReleasesView(); },
});
```

**Changes**:
1. Add `filters: () => releaseHeaderFilters` — enables generic handlers to read/write filter state
2. Add `getFilteredItems` — enables generic infrastructure to get filtered items
3. Update `onSearchChange` to write to `releaseHeaderFilters.search` instead of separate `releasesSearchFilter` variable (matches generic convention; need to add `search` key to `releaseHeaderFilters`)

**Note**: The `releasesSearchFilter` variable should be replaced by `releaseHeaderFilters.search` to match the pattern used by teams2 (`teams2Filters.search`).

## Decision 4: populateGenericFilterDropdowns() Call Configuration

**Decision**: Replace inline dropdown builders with a single `populateGenericFilterDropdowns()` call.

**Configuration**:
```javascript
populateGenericFilterDropdowns({
    dashboardId: 'releases',
    items: relevantReleaseItems,
    filters: releaseHeaderFilters,
    teamItemsBuilder: (items) => {
        // For Features: build synthetic items from Delivery Slices' teams
        // For Bugs/Issues: use item's own team
        // Same pattern as teams2 teamItemsBuilder
    }
});
```

**What this replaces**:
- 8× `getItemsExcludingFilter()` calls (customer, priority, state, tag, team, assignee, bugOwner, release)
- 8× inline dropdown HTML builders
- ~250 lines of cross-filter logic

**What is now also handled by populateGenericFilterDropdowns** (with new generic builders):
- Bug Owner dropdown — already integrated into `populateGenericFilterDropdowns()` (line 7527, used by Bugs/Teams2). Needs HTML element added to Releases.
- Bug Type dropdown — builder exists as `buildBugTypeFilterDropdown()` but is NOT currently called by `populateGenericFilterDropdowns()`. Each dashboard (Bugs line 23174, Validation line 30876, Capacity line 38771) calls it manually. Will be integrated into the generic pipeline.
- Type dropdown — new generic builder `buildTypeFilterDropdown()` to be created
- Progress Status dropdown — new generic builder `buildProgressStatusFilterDropdown()` to be created

**Note**: `populateGenericFilterDropdowns()` will need extensions to support `type`, `bugtype`, and `progressstatus` filter types. `bugowner` is already supported. `bugtype` builder exists but must be wired into the generic pipeline.

## Decision 5: getHeaderFilteredReleaseItems() Refactoring

**Decision**: Refactor to delegate standard filters to `applyGenericSecondaryFilters()`, then apply Releases-specific filters on top.

**New pattern**:
```javascript
function getHeaderFilteredReleaseItems(items) {
    // Single call — applyGenericSecondaryFilters handles ALL filters including
    // types, bugTypes, progressStatus, and teams (all extended in this migration)
    return applyGenericSecondaryFilters(items, releaseHeaderFilters);
}
```

**Filters added to applyGenericSecondaryFilters** (currently handles: search, releases, customers, priorities, states, tags, bugOwners, assignees):
- `types` — work item type filter (Feature/Issue/Bug). Match `item.type`.
- `bugTypes` — bug subtype filter (Customer Bug/Internal Bug). Match `item.bugType`. Only applies to `type === 'Bug'`.
- `progressStatus` — single-select string, not array. Delegates to existing `applyProgressStatusFilter()`. Skipped when value is `'All'`.
- `teams` — team filter. Calls existing `featureMatchesTeams(item.id, filters.teams)` for Features/Issues and `bugMatchesTeams(item, filters.teams, {orgMembers})` for Bugs. The `orgMembers` map is built once before the filter loop.

**Note on teams filter**: `applyGenericSecondaryFilters` currently does NOT handle teams — each dashboard applies it manually (Releases line 1684, Teams2 handles it via teamItemsBuilder). Adding `teams` to the generic function centralizes this per Constitution Principle I.

## Decision 6: localStorage Migration Compatibility

**Decision**: Handle old singular key names in localStorage state gracefully during `applyLoadedState()`.

**Approach**: In `applyLoadedState()`, when restoring `releaseHeaderFilters`, check for old singular key names and map them to new plural keys:

```javascript
if (state.releaseHeaderFilters) {
    const old = state.releaseHeaderFilters;
    // Migrate singular → plural if needed
    if (old.customer && !old.customers) old.customers = old.customer;
    if (old.priority && !old.priorities) old.priorities = old.priority;
    if (old.state && !old.states) old.states = old.state;
    if (old.tag && !old.tags) old.tags = old.tag;
    if (old.team && !old.teams) old.teams = old.team;
    if (old.assignee && !old.assignees) old.assignees = old.assignee;
    // Clean up old keys
    delete old.customer; delete old.priority; delete old.state;
    delete old.tag; delete old.team; delete old.assignee;
    Object.assign(releaseHeaderFilters, old);
}
```

**Rationale**: Users with existing localStorage data from before the migration should not lose their filter selections. After one save cycle, the new plural keys will be persisted and old keys discarded.

## Decision 7: clearAllReleaseFilters() Update

**Decision**: Update to use new plural key names. Keep Releases-specific filter clearing (type, bugtype, progressStatus) as custom code.

**Pattern**: Follow the same structure but reference `releaseHeaderFilters.customers`, `.priorities`, `.states`, `.tags`, `.teams`, `.assignees` instead of singular keys.

## Decision 8: Search Filter Variable Consolidation

**Decision**: Replace standalone `releasesSearchFilter` variable with `releaseHeaderFilters.search` to match the generic convention.

**Rationale**: All fully-migrated dashboards (teams2, bugs, customers) store search state in the filter object (e.g., `teams2Filters.search`). The generic `onSearchChange` handler and `applyGenericSecondaryFilters()` both read `filters.search`. Having a separate variable is legacy.

**Impact**: All references to `releasesSearchFilter` must be updated to `releaseHeaderFilters.search`. The `saveStateToStorage()` and `applyLoadedState()` functions need corresponding updates.

## Decision 9: Progress Status Semantics and Single-Select Pattern

**Decision**: Keep `progressStatus` as a single-select string (not multi-select array). Build a new `buildProgressStatusFilterDropdown()` that renders radio-button-style options.

**Values** (from `applyProgressStatusFilter()` at line 1489-1515):

| Value | Condition |
|-------|-----------|
| `'All'` | No filtering (default) |
| `'On Track'` | `0% ≤ progressPercentage ≤ 100%` |
| `'Slightly Over'` | `100% < progressPercentage ≤ 120%` |
| `'Significantly Over'` | `progressPercentage > 120%` |
| `'No Work Logged'` | `actualLogged === 0` |
| `'Has Warnings'` | `warning.hasWarning === true` |

**Rationale**: Progress status is semantically a category selector (one context at a time), unlike customer/tag filters which are multi-select. Changing to multi-select would alter the existing UX with no identified user need.

**Integration**: In `applyGenericSecondaryFilters()`, when `filters.progressStatus` exists and is not `'All'`, delegate to the existing `applyProgressStatusFilter()` function.

## Decision 10: Cross-Dashboard Impact Safety

**Decision**: All generic function extensions are additive and opt-in. No existing dashboard behavior changes.

**Safety mechanisms**:
1. `applyGenericSecondaryFilters()` — new `types`, `bugTypes`, `progressStatus`, `teams` blocks are guarded by `filters.{key}` existence and length checks. Dashboards without these keys are unaffected.
2. `populateGenericFilterDropdowns()` — new builders for `type`, `bugtype`, `progressstatus` only execute if `document.getElementById('${dashboardId}-${type}-menu')` returns a non-null element. Existing dashboards don't have these elements.
3. `FILTER_TYPE_MAP` — new entries add event handling for new filter types. Only triggered when matching DOM elements exist.

**Verification required**: Teams2, Bugs, Customers, Roadmap, Capacity dashboards must be tested post-migration (per Regression Test Plan section 2).

## Decision 11: FILTER_TYPE_MAP Extensions

**Decision**: Add entries for new filter types to support generic event handling.

**New entries**:
```javascript
'type':           { filterKey: 'types',          displayFn: (id) => updateGenericTypeDisplay(id) },
'bugtype':        { filterKey: 'bugTypes',       displayFn: (id) => updateGenericBugTypeDisplay(id) },
'progressstatus': { filterKey: 'progressStatus', displayFn: (id) => updateGenericProgressStatusDisplay(id) },
```

**Note**: `progressStatus` in FILTER_TYPE_MAP uses `filterKey: 'progressStatus'` (not `progressStatuses`) because it is a single-select string, not an array. The display update functions will need to be created alongside the new builders.

## Decision 12: Bug Type Consolidation (3 → 2 Derived Categories)

**Decision**: Modify `computeBugTypeInfo()` and `buildBugTypeFilterDropdown()` to consolidate from 3 raw ADO `Custom.BugType` picklist values to 2 derived categories.

**Context**: The ADO field `Custom.BugType` has 3 picklist values: "Customer Related", "Product Quality", "Technical & Infrastructure". The Releases Dashboard Type dropdown already uses a 2-category derived model (Customer Bug / Internal Bug) via `isCustomerBug()` and `isInternalBug()` helpers. The Bug Type dropdown (used on all dashboards with bug tables) should match this same derived model for consistency.

**Mapping**:

| New Dropdown Option | ADO `Custom.BugType` Values Matched | Display Label |
|---------------------|--------------------------------------|---------------|
| Customer Bug | `'Customer Related'` | Customer Bug |
| Internal Bug | `'Product Quality'` OR `'Technical & Infrastructure'` | Internal Bug |

**Changes required**:
1. `computeBugTypeInfo()` (~line 5264): Change `bugTypeOrder` from `['Customer Related', 'Product Quality', 'Technical & Infrastructure']` to `['Customer Bug', 'Internal Bug']`. Aggregate counts: items with `bugType === 'Customer Related'` → "Customer Bug"; items with `bugType === 'Product Quality'` or `bugType === 'Technical & Infrastructure'` → "Internal Bug".
2. `buildBugTypeFilterDropdown()` (~line 5295): No structural changes needed — it renders whatever `computeBugTypeInfo()` returns.
3. Filter matching in `applyGenericSecondaryFilters()` (and/or `handleGenericBugTypeChange()`): When user selects "Customer Bug", match `item.bugType === 'Customer Related'`. When user selects "Internal Bug", match `item.bugType === 'Product Quality' || item.bugType === 'Technical & Infrastructure'`.
4. `colors.bugTypes` palette (~line 29894): Update keys from 3 raw values to 2 derived categories.

**Cross-dashboard impact**: Bugs, Validation, Capacity, Reports dashboards all use `buildBugTypeFilterDropdown()`. They will automatically show the new 2-option dropdown. Existing localStorage state with old raw values ("Customer Related", "Product Quality", "Technical & Infrastructure") must be migrated to new derived values ("Customer Bug", "Internal Bug") during `applyLoadedState()`.

**Relationship to Type filter**: The Type dropdown (`buildTypeFilterDropdown()`) also has "Customer Bug" and "Internal Bug" as options. Both filters coexist with AND logic — selecting Type="Customer Bug" AND Bug Type="Internal Bug" would show zero items (contradictory), which is valid behavior.

**Rationale**: Aligns the Bug Type dropdown with the existing Releases Type dropdown semantics. Users think in terms of "Customer Bug" vs "Internal Bug", not the raw ADO picklist values "Product Quality" vs "Technical & Infrastructure".
