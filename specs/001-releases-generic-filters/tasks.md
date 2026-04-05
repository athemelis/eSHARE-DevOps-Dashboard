# Tasks: Releases Dashboard Generic Filter Migration

**Input**: Design documents from `/specs/001-releases-generic-filters/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested — manual browser testing only (per spec).

**Organization**: Tasks grouped by user story. Phase 1-2 are blocking prerequisites for all stories. Phases 3-8 map to spec user stories US1-US6 (P1/P2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files or independent code sections)
- **[Story]**: Which user story this task belongs to (US1-US6)
- File paths: `dashboard.js`, `dashboard-body.html`, `dashboard.css`

---

## Phase 1: Setup (New Generic Infrastructure)

**Purpose**: Create new generic filter builders and extend generic infrastructure BEFORE migrating Releases. These changes are additive — they don't break existing dashboards.

- [X] T001 [P] Create `buildTypeFilterDropdown()` generic builder function near existing generic filter builders in `dashboard.js` (~line 5295 area). Takes `{ dashboardId, items, selectedTypes }`, builds checkbox dropdown with 4 composite work-item-type categories: Feature (`item.type === 'Feature'`), Issue (`item.type === 'Issue'`), Customer Bug (`item.type === 'Bug' && isCustomerBug(item)`), Internal Bug (`item.type === 'Bug' && isInternalBug(item)`). Include `computeTypeInfo()` to aggregate counts, `handleGenericTypeChange()`, `selectAllGenericType()`, `clearGenericType()`, `updateGenericTypeDisplay()` handlers. The `types` filter array stores values `['Feature', 'Issue', 'CustomerBug', 'InternalBug']`.
- [X] T002 [P] Create `buildProgressStatusFilterDropdown()` generic builder function in `dashboard.js` near other generic filter builders. Takes `{ dashboardId, items, selectedStatus, progressCalculator }`, builds single-select dropdown with options (All, On Track ≤100%, Slightly Over 100-120%, Significantly Over >120%, No Work Logged, Has Warnings). Include `handleGenericProgressStatusChange()` and `updateGenericProgressStatusDisplay()` handlers.
- [X] T003 [P] Extend `applyGenericSecondaryFilters()` in `dashboard.js` (~line 7379) to handle four new filter keys: `types` (array — filter by `item.type`), `bugTypes` (array — filter by `item.bugType` for Bug items), `progressStatus` (string — delegate to existing `applyProgressStatusFilter()` when not `'All'`), `teams` (array — call `featureMatchesTeams(item.id, filters.teams)` for Features/Issues and `bugMatchesTeams(item, filters.teams, {orgMembers})` for Bugs; build `orgMembers` map once before filter loop). Add `excludeFilter` support for all four new filter types.
- [X] T004 Extend `populateGenericFilterDropdowns()` in `dashboard.js` (~line 7517) to build `type`, `bugtype`, and `progressstatus` dropdowns when `${dashboardId}-type-menu`, `${dashboardId}-bugtype-menu`, `${dashboardId}-progressstatus-menu` elements exist in HTML. Add entries to the builders array using new builders from T001/T002 and existing `buildBugTypeFilterDropdown()`. Wire cross-filtering via `xf('type')`, `xf('bugtype')`, `xf('progressstatus')`.
- [X] T005 Add `type`, `bugtype`, and `progressstatus` entries to `FILTER_TYPE_MAP` in `dashboard.js` (~line 7562) with correct `filterKey` mappings (`types`, `bugTypes`, `progressStatus`) and `displayFn` references to the update functions created in T001/T002.
- [X] T005b [P] Modify `computeBugTypeInfo()` and `buildBugTypeFilterDropdown()` in `dashboard.js` (~line 5264) to consolidate from 3 raw ADO `Custom.BugType` values to 2 derived categories: "Customer Bug" (matches `bugType === 'Customer Related'`) and "Internal Bug" (matches `bugType === 'Product Quality' || bugType === 'Technical & Infrastructure'`). Update `bugTypeOrder` from `['Customer Related', 'Product Quality', 'Technical & Infrastructure']` to `['Customer Bug', 'Internal Bug']`. Update filter matching in `handleGenericBugTypeChange()` and `applyGenericSecondaryFilters()` so selecting "Internal Bug" matches both raw ADO values. **Cross-dashboard impact**: This changes Bug Type dropdown on Bugs, Validation, Capacity, and Reports dashboards — all must be verified.

**Checkpoint**: Generic infrastructure extended with 4 new filter types (types, bugTypes, progressStatus, teams). Bug Type dropdown consolidated to 2 categories across all dashboards. Ready for Releases migration.

---

## Phase 2: Foundational (HTML + Filter Key Migration)

**Purpose**: Rename HTML element IDs and filter state keys. These are blocking prerequisites — all subsequent tasks depend on the new naming being in place.

**⚠️ CRITICAL**: This phase changes both HTML and JS simultaneously. The dashboard will be broken between T006 and T008.

- [X] T006 Rename all Releases filter HTML element IDs in `dashboard-body.html` from `release-*` pattern to `releases-*` pattern per research.md Decision 2 mapping table. Also add new Bug Owner dropdown HTML (container `releases-bugowner-dropdown`, toggle, display `releases-bugowner-display`, menu `releases-bugowner-menu`) after the Assignee dropdown — follow `bugs-bugowner-dropdown` structure. Update `toggleFilterDropdown()` onclick attributes to use new container IDs.
- [X] T007 Rename `releaseHeaderFilters` keys in `dashboard.js` definition (~line 1090): `customer`→`customers`, `priority`→`priorities`, `state`→`states`, `tag`→`tags`, `team`→`teams`, `assignee`→`assignees`, `type`→`types`, `bugtype`→`bugTypes`. Add new keys: `search: ''`, `releases: []`, `bugOwners: []`. Update ALL references throughout `dashboard.js` (find-and-replace with context matching, e.g., `releaseHeaderFilters.customer` → `releaseHeaderFilters.customers`).
- [X] T008 Update all JS `getElementById()` calls and `onclick` handlers in `dashboard.js` that reference old HTML element IDs (e.g., `release-customer-header-menu` → `releases-customer-menu`, `release-filter-menu` → `releases-release-menu`, `release-clear-filters-btn` → `releases-clear-filters-btn`).
- [X] T009 [P] Update `dashboard.css` for any ID-based selectors that reference old Releases element IDs. Most styles use classes so this may be minimal or empty.

**Checkpoint**: HTML and JS naming are consistent with generic convention. Dashboard may still use inline filter code but IDs are correct.

---

## Phase 3: User Story 1 — Cross-Filtered Dropdown Counts (Priority: P1) 🎯 MVP

**Goal**: Replace inline `getItemsExcludingFilter()` and dropdown builders with `populateGenericFilterDropdowns()` so all dropdowns show accurate cross-filtered counts.

**Independent Test**: Open Releases Dashboard. Select a Customer. Open State dropdown — counts should reflect only that customer's items. Open Priority — same. Counts match visible table items.

### Implementation for User Story 1

- [X] T010 [US1] Update `DASHBOARD_FILTER_REGISTRY` entry for `'releases'` in `dashboard.js` (~line 7465): add `filters: () => releaseHeaderFilters`, add `getFilteredItems: () => getHeaderFilteredReleaseItems(...)`, update `onSearchChange` to write to `releaseHeaderFilters.search` instead of standalone `releasesSearchFilter`.
- [X] T011 [US1] Replace inline `getItemsExcludingFilter()` calls and dropdown HTML builders in `renderReleasesView()` (~line 29276+) with a single `populateGenericFilterDropdowns({ dashboardId: 'releases', items: relevantItems, filters: releaseHeaderFilters, teamItemsBuilder: ... })` call. Include `teamItemsBuilder` callback for Feature→Delivery Slice team mapping (follow teams2 `teamItemsBuilder` pattern at ~line 40649).
- [X] T012 [US1] Remove the `getItemsExcludingFilter()` helper function and all inline dropdown builder code (~250-357 lines) that is now replaced by `populateGenericFilterDropdowns()`.
- [X] T013 [US1] Refactor `getHeaderFilteredReleaseItems()` (~line 1652) to delegate to `applyGenericSecondaryFilters(items, releaseHeaderFilters)` for all filters (search, releases, customers, priorities, states, tags, teams, assignees, bugOwners, bugTypes, types, progressStatus). Remove ~90 lines of manual per-filter application code.

**Checkpoint**: All dropdown counts are cross-filtered. Selecting Customer updates counts in State, Priority, Tag, etc.

---

## Phase 4: User Story 2 — Clear All Filters (Priority: P1)

**Goal**: Clear Filters resets ALL filter state (generic + Type + Bug Type + Bug Owner + Progress Status), persists cleared state, and updates all display texts.

**Independent Test**: Apply 3+ filters. Click Clear All. All dropdowns show defaults. Tables show all items. Refresh page — filters stay cleared.

### Implementation for User Story 2

- [X] T014 [US2] Update `clearAllReleaseFilters()` in `dashboard.js` to use new plural key names (`customers`, `priorities`, `states`, `tags`, `teams`, `assignees`, `bugOwners`, `bugTypes`, `types`). Add clearing of `releaseHeaderFilters.search` (replacing `releasesSearchFilter` clearing). Ensure `progressStatus` resets to `'All'`. Ensure `bugOwners` resets to `[]`.
- [X] T015 [US2] Update `updateClearFiltersButton()` (Releases-specific clear button logic) to check all new filter keys when determining button visibility. Include checks for `types`, `bugTypes`, `bugOwners`, `progressStatus`, and `releaseHeaderFilters.search`.

**Checkpoint**: Clear All resets everything. Button hides when no filters active.

---

## Phase 5: User Story 3 — Individual Filter Operations (Priority: P1)

**Goal**: Select/deselect, Select All, Clear within each dropdown works correctly. Collapsed display text updates.

**Independent Test**: Open State dropdown, select "Active", verify collapsed text and table filter. Click Select All, verify. Click Clear, verify.

### Implementation for User Story 3

- [X] T016 [US3] Verify all generic filter change handlers (`handleGenericCustomerChange`, `handleGenericPriorityChange`, `handleGenericStateChange`, `handleGenericTagChange`, `handleGenericTeamChange`, `handleGenericAssigneeChange`, `handleGenericBugOwnerChange`) route correctly for `dashboardId='releases'` via the registry. Fix any that fall through to legacy code paths because `filters()` was previously missing from the registry entry.
- [X] T017 [US3] Verify new `handleGenericTypeChange()` (from T001), `handleGenericBugTypeChange()` (wired in T004), and `handleGenericProgressStatusChange()` (from T002) integrate correctly with the Releases registry entry — triggering render, saveStateToStorage, and clear button update.
- [X] T018 [US3] Remove any remaining legacy per-dropdown change handlers and event bindings that duplicate generic handler functionality (e.g., old `onchange` handlers hardcoded in inline HTML builders).

**Checkpoint**: Every filter dropdown's select/deselect/selectAll/clear works and updates collapsed text.

---

## Phase 6: User Story 4 — State Persistence (Priority: P2)

**Goal**: Filter selections survive page refresh, auto-refresh (60s), and dashboard tab switches.

**Independent Test**: Apply Customer + Priority filters. Wait 60s for auto-refresh. Verify filters preserved. Hard-refresh. Verify restored from localStorage.

### Implementation for User Story 4

- [X] T019 [US4] Update `saveStateToStorage()` in `dashboard.js` (~line 122) to save `releaseHeaderFilters` with new key names. Remove separate `releasesSearchFilter` save entry (search is now in `releaseHeaderFilters.search`).
- [X] T020 [US4] Update `applyLoadedState()` in `dashboard.js` (~line 227) to restore `releaseHeaderFilters` with singular→plural key migration compatibility per research.md Decision 6. Map `customer`→`customers`, `priority`→`priorities`, `state`→`states`, `tag`→`tags`, `team`→`teams`, `assignee`→`assignees`, `type`→`types`, `bugtype`→`bugTypes`. Handle missing `bugOwners`/`search`/`releases` keys gracefully (default to empty). Also migrate standalone `releasesSearchFilter` into `releaseHeaderFilters.search`.
- [X] T021 [US4] Remove standalone `releasesSearchFilter` variable declaration (~line 1105) and replace all remaining references throughout `dashboard.js` with `releaseHeaderFilters.search`.

**Checkpoint**: Filters persist across refresh and auto-refresh. Old localStorage data migrates cleanly.

---

## Phase 7: User Story 5 — Type, Bug Type, Bug Owner, Progress Status Filters (Priority: P2)

**Goal**: Type, Bug Type, Bug Owner, and Progress Status filters work correctly through generic infrastructure.

**Independent Test**: Select Type=Bug → only bugs. Select Bug Type=Customer Bug → only customer bugs. Select Bug Owner → filters to that owner's bugs. Select Progress Status=Slightly Over → only 100-120% items.

### Implementation for User Story 5

- [X] T022 [US5] Verify `buildTypeFilterDropdown()` (from T001) renders correctly in the Releases Dashboard. Verify type options match current behavior: Feature, Issue, Customer Bug, Internal Bug. Verify filtering maps correctly to `item.type` values in `dashboard.js`.
- [X] T023 [US5] Verify `buildBugTypeFilterDropdown()` (existing generic, wired in T004) renders in Releases Dashboard via `populateGenericFilterDropdowns()`. Verify Bug Type options and filtering match current behavior in `dashboard.js`.
- [X] T024 [US5] Verify `buildBugOwnerFilterDropdown()` (existing generic) renders in new Releases Bug Owner dropdown HTML from T006. Verify Bug Owner filtering correctly filters to bugs owned by selected person in `dashboard.js`.
- [X] T025 [US5] Verify `buildProgressStatusFilterDropdown()` (from T002) renders and filters correctly in `dashboard.js`. Verify progress calculation matches current Releases progress logic (On Track ≤100%, Slightly Over 100-120%, Significantly Over >120%, No Work Logged, Has Warnings).

**Checkpoint**: All four Releases-specific-now-generic filters work through the generic infrastructure.

---

## Phase 8: User Story 6 — No Behavioral Regression (Priority: P2)

**Goal**: Zero behavioral differences from pre-migration. All existing functionality works identically.

**Independent Test**: Compare pre/post behavior for tag exclusion, tag AND/OR, deep search popup, chart highlights, table sort persistence.

### Implementation for User Story 6

- [X] T026 [US6] Verify tag exclusion mode (`tagExclusionMode`) and tag logic mode (`tagLogicMode`) work correctly through `applyGenericSecondaryFilters()` in `dashboard.js`. These keys were already in the correct format — verify they pass through the generic pipeline.
- [X] T027 [US6] Update Items by Release chart filter highlighting code (~line 29916 in `dashboard.js`) to reference new plural key names (e.g., `releaseHeaderFilters.customers.length` instead of `releaseHeaderFilters.customer.length`). Verify chart bars highlight/dim correctly when filters are active.
- [X] T028 [US6] Verify deep search popup works through the generic `onSearchChange` handler in `dashboard.js`. Ensure `_lastDeepSearchPopupTerm` is still cleared on search change and popup appears for matches in collapsed release sections.
- [X] T029 [US6] Verify table sort persistence, column widths, scroll positions, and collapsible section states in `dashboard.js` all survive the migration (these use `buildGenericTable` which is unaffected — verify no regressions).

**Checkpoint**: Dashboard behaves identically to pre-migration.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, dead code removal, documentation updates.

- [X] T030 Remove `releasesSearchFilter` standalone variable declaration and any remaining references in `dashboard.js` (if not completed in T021).
- [X] T031 Remove `getItemsExcludingFilter()` function in `dashboard.js` if not already removed in T012.
- [X] T032 Remove any orphaned inline dropdown builder functions or helper code in `dashboard.js` that is no longer called after migration.
- [X] T033 Regression testing per Constitution Principle VII: execute all 7 categories from spec.md Regression Test Plan — direct feature tests, cross-dashboard impact (Teams2, Bugs, Validation, Capacity, Reports, Customers, Roadmap — including Bug Type 3→2 verification on all Bug Type consumers), auto-refresh test, state persistence test, theme test, performance check, console check.
- [X] T034 Run quickstart.md verification checklist in browser — verify all 10 items pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — T001, T002, T003, T005b parallelizable; T004 depends on T001+T002+T005b; T005 depends on T001+T002
- **Phase 2 (Foundational)**: Depends on Phase 1 — T006 (HTML) and T007 (JS keys) can be semi-parallel, then T008+T009 after
- **Phase 3 (US1)**: Depends on Phase 2 — uses new names + new generic builders
- **Phase 4 (US2)**: Depends on Phase 2 — uses new key names for clearing
- **Phase 5 (US3)**: Depends on Phase 3 — needs generic dropdowns to be wired up
- **Phase 6 (US4)**: Depends on Phase 2 — needs new key names for save/restore
- **Phase 7 (US5)**: Depends on Phases 1 + 3 — needs new builders + populateGenericFilterDropdowns
- **Phase 8 (US6)**: Depends on all previous phases — regression verification
- **Phase 9 (Polish)**: Depends on all phases — final cleanup and regression testing

### Parallel Opportunities

- **Phase 1**: T001, T002, T003 are parallelizable (different functions in dashboard.js). T004, T005 depend on T001+T002.
- **Phase 2**: T006 (HTML) and T007 (JS keys) can be worked semi-parallel, then T008+T009 after
- **Phase 3-4**: US1 (T010-T013) and US2 (T014-T015) can proceed in parallel after Phase 2
- **Phase 6**: US4 (T019-T021) can proceed in parallel with US1/US2 after Phase 2

### User Story Dependencies

| Story | Phase | Depends On | Can Parallelize With |
|-------|-------|-----------|---------------------|
| US1 (Cross-filtered counts) | Phase 3 | Phase 1, Phase 2 | US2, US4 |
| US2 (Clear All) | Phase 4 | Phase 2 | US1, US4 |
| US3 (Individual filter ops) | Phase 5 | US1 (Phase 3) | US4 |
| US4 (State persistence) | Phase 6 | Phase 2 | US1, US2 |
| US5 (Releases-specific filters) | Phase 7 | Phase 1, US1 (Phase 3) | — |
| US6 (No regression) | Phase 8 | All previous | — |

---

## Implementation Strategy

**MVP**: Phase 1 + Phase 2 + Phase 3 (US1) — cross-filtered dropdowns working through generic infrastructure. This delivers the core value (FR-007, SC-001).

**Incremental Delivery**:
1. Phase 1: New generic builders (additive, safe — no existing dashboard affected)
2. Phase 2: Rename HTML IDs + JS keys (breaking change, must be completed atomically with Phase 3)
3. Phase 3: Wire up `populateGenericFilterDropdowns()` — MVP complete, dashboard functional
4. Phase 4: Clear All filters + Phase 6: State persistence (can proceed in parallel)
5. Phase 5: Individual filter operations verification
6. Phase 7: Releases-specific filters (Type, Bug Type, Bug Owner, Progress Status) through generic
7. Phase 8: Regression verification (tag modes, chart, deep search, tables)
8. Phase 9: Dead code removal, regression testing checklist, quickstart validation
