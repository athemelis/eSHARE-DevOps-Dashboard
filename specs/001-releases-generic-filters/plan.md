# Implementation Plan: Releases Dashboard Generic Filter Migration

**Branch**: `001-releases-generic-filters` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-releases-generic-filters/spec.md`

## Summary

Migrate the Releases Dashboard from ~357 lines of legacy inline dropdown-building and manual filter application to the generic filter infrastructure (`populateGenericFilterDropdowns`, `applyGenericSecondaryFilters`, `DASHBOARD_FILTER_REGISTRY`). This involves renaming filter keys from singular to plural, standardizing HTML element IDs, extending the generic infrastructure with 3 new filter types (`type`, `bugType`, `progressStatus`), adding a Bug Owner dropdown, and implementing a one-time localStorage key migration. The Teams2 dashboard serves as the gold-standard reference for a fully-migrated dashboard.

## Technical Context

**Language/Version**: Vanilla JavaScript (ES6+), HTML5, CSS3  
**Primary Dependencies**: Chart.js (CDN), MSAL.js (CDN) — no npm packages for frontend  
**Storage**: localStorage (browser-side state persistence)  
**Testing**: Manual browser testing (no automated test framework)  
**Target Platform**: Modern browsers (Chrome, Edge, Firefox, Safari)  
**Project Type**: Static SPA (Cloudflare Pages)  
**Performance Goals**: Filter operations < 1 second, auto-refresh < 2 seconds  
**Constraints**: No build step; single dashboard.js file (~19,500 lines); all generic infrastructure must coexist  
**Scale/Scope**: 10 dashboard views, ~500 work items rendered per release

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | Generic Infrastructure Over Dashboard-Specific Code | ✅ PASS | This feature IS the migration to generic infrastructure. New generic builders added (buildTypeFilterDropdown, buildProgressStatusFilterDropdown). applyGenericSecondaryFilters extended for types/bugTypes/progressStatus. |
| II | Architecture & Data Pipeline | ✅ PASS | No changes to data pipeline. Filter migration is frontend-only. |
| III | Branching & Deployment Strategy | ✅ PASS | On feature branch `001-releases-generic-filters`, will PR to main. |
| IV | Theme System & UX Consistency | ✅ PASS | No new colors or styles. All filter dropdowns use existing CSS classes/variables. New Bug Owner dropdown reuses existing patterns. |
| V | State Persistence | ✅ PASS | Filter state persists via existing `saveStateToStorage()`/`loadStateFromStorage()` pattern. One-time key migration handled at load time (FR-013). |
| VI | ADO Integration & Inline Editing | ✅ PASS | No changes to inline editing. |
| VII | Regression Testing | ✅ PASS | Spec includes full 7-category Regression Test Plan. Cross-dashboard impact documented for Teams2, Bugs, Customers, Roadmap, Capacity. |
| VIII | Code Organization | ✅ PASS | New generic functions placed near existing generic functions in dashboard.js. Dashboard-specific code stays in Releases section. |
| IX | Performance Considerations | ✅ PASS | Cross-filtering uses existing xf() pattern. No new performance risks. Early returns maintained. |

**Gate result: ALL PASS — proceed to Phase 0.**

### Post-Design Check

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | Generic Infrastructure | ✅ PASS | All 4 new filter types (types, bugTypes, progressStatus, teams) added to generic functions. No dashboard-specific filtering code remains. |
| II | Architecture & Data Pipeline | ✅ PASS | No changes. |
| III | Branching & Deployment | ✅ PASS | No changes. |
| IV | Theme System | ✅ PASS | Bug Owner dropdown reuses existing CSS. No new colors. |
| V | State Persistence | ✅ PASS | One-time key migration in loadStateFromStorage. search moved into filter object. |
| VI | ADO Integration | ✅ PASS | No changes. |
| VII | Regression Testing | ✅ PASS | Full 7-category plan in spec. Cross-dashboard verification for Teams2, Bugs, Customers, Roadmap, Capacity. |
| VIII | Code Organization | ✅ PASS | New builders near existing builders. FILTER_TYPE_MAP extensions in place. |
| IX | Performance | ✅ PASS | orgMembers cached outside filter loop for teams. progressStatus delegates to existing function. |

**Post-design gate: ALL PASS. No violations. No Complexity Tracking entries needed.**

## Project Structure

### Documentation (this feature)

```text
specs/001-releases-generic-filters/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
dashboard-body.html      # Releases filter bar HTML — ID migration + Bug Owner dropdown addition
dashboard.js             # Main application logic:
├── releaseHeaderFilters          (~line 1090)  — key rename + add search/bugOwners
├── getHeaderFilteredReleaseItems (~line 1652)  — delegate to applyGenericSecondaryFilters
├── applyGenericSecondaryFilters  (~line 7379)  — extend with types/bugTypes/progressStatus/teams
├── registerDashboardFilters      (~line 7465)  — add filters/getFilteredItems to releases entry
├── populateGenericFilterDropdowns(~line 7517)  — extend with type/bugtype/progressstatus builders
├── FILTER_TYPE_MAP               (~line 7562)  — add type/bugtype/progressstatus entries
├── buildTypeFilterDropdown       (NEW)         — generic type filter builder
├── buildProgressStatusFilterDropdown (NEW)     — generic progress status builder
├── renderReleasesView            (~line 29091) — replace inline filter code with populateGenericFilterDropdowns
├── releasesSearchFilter          (~line 1105)  — migrate to releaseHeaderFilters.search
├── Items by Release chart        (~line 29916) — update key references to plural names
└── saveStateToStorage/loadStateFromStorage      — one-time key migration logic
```

**Structure Decision**: No new files created. All changes are in-place modifications to `dashboard.js` and `dashboard-body.html`. This is a refactoring migration within the existing 4-file architecture.

## Complexity Tracking

> No Constitution Check violations. No entries needed.
