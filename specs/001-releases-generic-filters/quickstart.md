# Quickstart: Releases Dashboard Generic Filter Migration

## Migration Steps (Execution Order)

### Step 1: Rename HTML Element IDs (dashboard-body.html)

Rename all Releases filter element IDs from `release-*` pattern to `releases-*` pattern to match the generic `${dashboardId}-${type}-suffix` convention.

See [research.md](research.md) Decision 2 for complete ID mapping table.

### Step 2: Rename Filter Keys (dashboard.js)

Update `releaseHeaderFilters` definition and all ~100 references:
- `customer` → `customers`
- `priority` → `priorities`  
- `state` → `states`
- `tag` → `tags`
- `team` → `teams`
- `assignee` → `assignees`
- Add `search: ''` key (replaces `releasesSearchFilter`)
- Add `releases: []` key (for generic release filter integration)

### Step 3: Update DASHBOARD_FILTER_REGISTRY Entry (dashboard.js)

Add `filters: () => releaseHeaderFilters` and `getFilteredItems` to the registry entry.

### Step 4: Replace Inline Dropdown Builders (dashboard.js)

Replace the ~250 lines of `getItemsExcludingFilter()` + inline dropdown HTML builders with a single `populateGenericFilterDropdowns()` call.

### Step 5: Extend applyGenericSecondaryFilters() (dashboard.js)

Add 4 new filter blocks to `applyGenericSecondaryFilters()`:
- `types` — match `item.type` against `filters.types` array
- `bugTypes` — match `item.bugType` for `type === 'Bug'` items against `filters.bugTypes` array
- `progressStatus` — delegate to `applyProgressStatusFilter()` when value is not `'All'`
- `teams` — call `featureMatchesTeams()`/`bugMatchesTeams()` with cached `orgMembers` map

### Step 6: Refactor getHeaderFilteredReleaseItems() (dashboard.js)

Replace ~90 lines of manual filter application with a single `applyGenericSecondaryFilters()` call. All filters (including types, bugTypes, progressStatus, teams) are now handled generically.

### Step 7: Update clearAllReleaseFilters() (dashboard.js)

Use new plural key names. Clear `search` via the filter object instead of separate variable.

### Step 8: Add localStorage Migration (dashboard.js)

In `applyLoadedState()`, map old singular keys to new plural keys for backward compatibility.

### Step 9: Extend populateGenericFilterDropdowns() (dashboard.js)

Add `buildBugTypeFilterDropdown`, `buildTypeFilterDropdown`, and `buildProgressStatusFilterDropdown` to the generic builders array. Add corresponding `FILTER_TYPE_MAP` entries.

### Step 10: Add Bug Owner Dropdown to HTML (dashboard-body.html)

Add `releases-bugowner-dropdown` with `releases-bugowner-menu` element. Follow Bugs Dashboard pattern.

### Step 11: Update All JS References to Old HTML IDs (dashboard.js)

Update any `getElementById()` calls, `onclick` handlers, or other JS references to the old element IDs.

### Step 12: Remove Dead Code (dashboard.js)

Remove `getItemsExcludingFilter()` helper, `releasesSearchFilter` variable, and any orphaned inline dropdown builder code.

### Step 13: Verify (browser)

Test all 6 user stories from spec.md in the browser.

## Verification Checklist

- [ ] All filter dropdowns populate with correct cross-filtered counts
- [ ] Clear All resets everything including Releases-specific filters
- [ ] Individual filter select/deselect/selectAll/clear work
- [ ] State persists across page refresh and auto-refresh
- [ ] Type, Bug Type, and Progress Status filters continue working
- [ ] Tag exclusion mode and AND/OR logic work
- [ ] Items by Release chart highlights with active filters
- [ ] Deep search popup works
- [ ] No JavaScript console errors
- [ ] Dark and light mode both render correctly
