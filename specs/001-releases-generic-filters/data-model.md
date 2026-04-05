# Data Model: Releases Dashboard Generic Filter Migration

## Entity: releaseHeaderFilters (After Migration)

The filter state object for the Releases Dashboard. Keys renamed to match generic convention.

```javascript
let releaseHeaderFilters = {
    // Generic filter keys (plural — used by populateGenericFilterDropdowns / applyGenericSecondaryFilters)
    search: '',             // String — search term (replaces standalone releasesSearchFilter)
    releases: [],           // Array<string> — note: 'releases' key used by generic release filter
    customers: [],          // Array<string> — was 'customer'
    priorities: [],         // Array<string> — was 'priority'
    states: [],             // Array<string> — was 'state'
    tags: [],               // Array<string> — was 'tag'
    teams: [],              // Array<string> — was 'team'
    assignees: [],          // Array<string> — was 'assignee'
    bugOwners: [],          // Array<string> — NEW (required: dashboards with Bug tables must have Bug Owner)
    bugTypes: [],           // Array<string> — was 'bugtype' (already generic via buildBugTypeFilterDropdown)
    types: [],              // Array<string> — was 'type' (new generic via buildTypeFilterDropdown)
    
    // Generic control flags (already correct)
    tagExclusionMode: false,    // Boolean — exclude matching tags instead of include
    tagLogicMode: 'or',         // 'or' | 'and' — AND/OR logic for multi-tag selection
    
    // New generic filter (available to Releases, Roadmap, Bugs, Teams)
    progressStatus: 'All',      // String — 'All' | 'On Track' | 'Slightly Over' | 'Significantly Over' | 'No Work Logged' | 'Has Warnings'
};
```

### Validation Rules
- All array keys default to `[]` (empty = all items pass filter)
- `tagExclusionMode` defaults to `false`
- `tagLogicMode` defaults to `'or'`
- `progressStatus` defaults to `'All'`
- `search` defaults to `''`

### State Transitions
- **Load**: `applyLoadedState()` restores from localStorage with singular→plural key migration
- **Change**: Individual filter handler updates the relevant key, calls `saveStateToStorage()` + `renderReleasesView()`
- **Clear**: `clearAllReleaseFilters()` resets all keys to defaults, calls `saveStateToStorage()` + `renderReleasesView()`
- **Auto-refresh**: State preserved across 60s refresh cycle via localStorage

## Entity: DASHBOARD_FILTER_REGISTRY Entry for 'releases'

```javascript
registerDashboardFilters('releases', {
    label: 'Releases',
    filters: () => releaseHeaderFilters,
    render: () => renderReleasesView(),
    clearBtn: () => updateClearFiltersButton(),
    getAllItems: () => workItems.filter(w => ['Feature', 'Issue', 'Bug'].includes(w.type)),
    getFilteredItems: () => getHeaderFilteredReleaseItems(
        workItems.filter(w => ['Feature', 'Issue', 'Bug'].includes(w.type))
    ),
    onSearchChange: (v) => {
        releaseHeaderFilters.search = v;
        _lastDeepSearchPopupTerm = '';
        updateClearFiltersButton();
        saveStateToStorage();
        renderReleasesView();
    },
});
```

### Properties
| Property | Type | Purpose |
|----------|------|---------|
| `label` | string | Display name in UI |
| `filters` | `() => object` | Accessor for filter state — enables generic handlers |
| `render` | `() => void` | Re-render the dashboard |
| `clearBtn` | `() => void` | Update clear button visibility |
| `getAllItems` | `() => Array` | All items relevant to this dashboard (unfiltered) |
| `getFilteredItems` | `() => Array` | Items after applying all filters |
| `onSearchChange` | `(string) => void` | Handle search input changes |

## Entity: HTML Element ID Convention

Pattern: `${dashboardId}-${filterType}-${suffix}`

Where `dashboardId = 'releases'`:

| Filter Type | `-menu` (dropdown content) | `-display` (collapsed text) | `-dropdown` (container) |
|-------------|---------------------------|---------------------------|------------------------|
| release | `releases-release-menu` | `releases-release-display` | `releases-release-dropdown` |
| customer | `releases-customer-menu` | `releases-customer-display` | `releases-customer-dropdown` |
| priority | `releases-priority-menu` | `releases-priority-display` | `releases-priority-dropdown` |
| state | `releases-state-menu` | `releases-state-display` | `releases-state-dropdown` |
| tag | `releases-tag-menu` | `releases-tag-display` | `releases-tag-dropdown` |
| team | `releases-team-menu` | `releases-team-display` | `releases-team-dropdown` |
| assignee | `releases-assignee-menu` | `releases-assignee-display` | `releases-assignee-dropdown` |
| bugowner | `releases-bugowner-menu` | `releases-bugowner-display` | `releases-bugowner-dropdown` |
| bugtype | `releases-bugtype-menu` | `releases-bugtype-display` | `releases-bugtype-dropdown` |
| type | `releases-type-menu` | `releases-type-display` | `releases-type-dropdown` |
| progressstatus | `releases-progressstatus-menu` | `releases-progressstatus-display` | `releases-progressstatus-dropdown` |

## Relationship: populateGenericFilterDropdowns → releaseHeaderFilters

```
populateGenericFilterDropdowns({
    dashboardId: 'releases',     → looks up 'releases-{type}-menu' elements
    items: relevantItems,         → work items for dropdown option counting
    filters: releaseHeaderFilters → reads .customers, .priorities, .states, .tags, .teams, .assignees
    teamItemsBuilder: (items) => ... → optional: transform items for Team dropdown
})
    ↓
For each filter type in [release, customer, priority, state, tag, team, bugowner, assignee]:
    1. Compute cross-filtered items: applyGenericSecondaryFilters(items, filters, excludeType)
    2. Build dropdown HTML: build{Type}FilterDropdown({ dashboardId, items, selected })
    3. Inject into DOM: document.getElementById('releases-{type}-menu').innerHTML = html
    4. Update display text: updateGeneric{Type}Display('releases')
```

## Relationship: applyGenericSecondaryFilters → releaseHeaderFilters

```
applyGenericSecondaryFilters(items, releaseHeaderFilters)
    ↓
Applies in order:
    1. search filter (releaseHeaderFilters.search)
    2. releases filter (releaseHeaderFilters.releases)
    3. customers filter (releaseHeaderFilters.customers)
    4. priorities filter (releaseHeaderFilters.priorities)
    5. states filter (releaseHeaderFilters.states)
    6. tags filter (releaseHeaderFilters.tags + tagExclusionMode + tagLogicMode)
    7. teams filter (releaseHeaderFilters.teams) — NEW: uses featureMatchesTeams/bugMatchesTeams
    8. assignees filter (releaseHeaderFilters.assignees)
    9. bugOwners filter (releaseHeaderFilters.bugOwners)
    10. bugTypes filter (releaseHeaderFilters.bugTypes) — NEW generic filter
    11. types filter (releaseHeaderFilters.types) — NEW generic filter
    12. progressStatus filter (releaseHeaderFilters.progressStatus) — NEW generic filter (single-select, delegates to applyProgressStatusFilter)
    ↓
Returns: fully filtered items (all filters applied generically, no custom post-processing needed)
```
