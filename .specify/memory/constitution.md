<!--
  Sync Impact Report
  ==================
  Version change: 1.0.0 → 1.1.0 (MINOR — template alignment)
  Modified principles:
    - III. Branching & Deployment Strategy: Updated legacy note
      (tony-dev migration complete in v247, no longer tracked separately)
  Added sections: None
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ compatible (no changes needed)
    - .specify/templates/spec-template.md ✅ UPDATED
      (Added mandatory "Regression Test Plan" section with 7 test
      categories per Principle VII)
    - .specify/templates/tasks-template.md ✅ UPDATED
      (Changed regression testing from optional to mandatory in
      Polish phase, per Principle VII)
    - .specify/templates/checklist-template.md ✅ compatible (no changes needed)
    - .specify/templates/agent-file-template.md ✅ compatible (no changes needed)
  Follow-up TODOs:
    - DASHBOARD-REFERENCE.md architecture diagrams section may need
      upload; now deployed via Cloudflare Pages — update pending
-->

# eSHARE DevOps Dashboard Constitution

## Core Principles

### I. Generic Infrastructure Over Dashboard-Specific Code

This is the single most important principle. The dashboard has 10 views
(Executive, Roadmap, Teams, Customers, Bugs, Releases, Tasks,
Validation, Capacity, Reports) that share common UI patterns. ALL
reusable UI MUST use the generic infrastructure — NEVER duplicate
logic per-dashboard.

**Filter dropdowns**: ALL filter dropdowns MUST use
`populateGenericFilterDropdowns()`. This function builds dropdowns
(release, customer, priority, state, tag, team, bugOwner, assignee),
applies cross-filtering (each dropdown sees items filtered by all
OTHER active filters), and updates display text. Dashboards register
via `registerDashboardFilters()` into `DASHBOARD_FILTER_REGISTRY`.
Secondary filtering uses `applyGenericSecondaryFilters()`. Search
uses `handleGenericSearchChange()` with `applyGenericSearchFilter()`.

**Tables**: ALL tables MUST use `buildGenericTable()` with a column
definition array. Default sort is `backlogPriority` ascending.
`reorderable: true` enables drag-to-reorder (writes backlog priority
back to ADO). Column widths and sort state auto-persist to
localStorage. Use the `renderCell` callback for custom columns
(return `<td>` HTML, or `null` to fall back to
`genericTableDefaultRenderCell`). NEVER create custom table HTML.

**Column rendering**: `genericTableDefaultRenderCell` handles: id,
title (with relationship pills), state (badge + inline edit),
priority, backlogPriority, progress, aging, ticketCategory, tags,
customers, architecture, release, assignedTo, team, csOwner,
bugOwner, bugType, effort, closedDate, createdDate,
cascadingVersion, cascadingDate. Do NOT reimplement these.

**Alert requirement**: If a spec or plan introduces dashboard-specific
code for something that could be generic, the spec MUST flag it with
a "⚠️ SPECIFIC CODE JUSTIFICATION" section explaining why generic
infrastructure cannot be used and proposing a path to make it generic
in the future.

### II. Architecture & Data Pipeline

**Data flow**: Azure DevOps → Power Automate (3min/5min exports) →
SharePoint (JSON files) → MSAL Auth (prod) / direct file load
(local) → Browser renders dashboard. Flow definitions are
version-controlled in `flows/` (secrets redacted by `import-flow.sh`).

**Data files** (not in repo, fetched at runtime):
- `ALL Items.json` — Work items (Features, Bugs, Tasks, Issues,
  Delivery Slices)
- `WorkItemLinks.json` — Parent/child/related relationships
- `Org Chart.json` — Team structure, members, capacity percentages
- `cascading_lists.json` — Picklist values for cascading fields

**Authentication**:
- Production: MSAL with Azure AD, scopes `Sites.Selected`, client
  ID `bf683b68-0dc3-4205-a5b7-676f54a958c0`
- Local development (localhost:8000): MSAL bypassed, JSON files
  loaded directly from ./

**Auto-refresh**: Data reloads every 60 seconds. `isAutoRefresh` flag
disables chart animations during refresh. Data hash comparison
(`computeXxxDataHash()`) skips re-render when data hasn't changed.

**No build step**: The dashboard is vanilla HTML/JS/CSS. No
transpilation, bundling, or package managers for the frontend.
Chart.js and MSAL loaded via CDN.

### III. Branching & Deployment Strategy

**Branching model**: Standard GitHub Flow. Feature branches are
created from `main` for each spec/feature. PRs merge feature branches
directly to `main`, which triggers Cloudflare Pages deployment.
Feature branches are deleted after merge. There is no shared
development branch — each piece of work is isolated on its own branch.

**Legacy note**: The project previously used a `tony-dev` branch as a
single-contributor development branch. This was retired in v247 in
favor of per-feature branches. The pre-migration state is archived
at git tag `pre-speckit`.

**Deployment**: Merging to `main` triggers Cloudflare Pages deployment
automatically. The live site is https://devops-dashboard.e-share.io.
Cache-busting uses `?v=XXX` query strings on all module files in
dashboard.html. Branch protection on `main` requires PR review before
merge.

**Local development**:
1. `git checkout -b feature/my-feature main` — create feature branch
2. `./copy-data-files.sh` — copy JSON data files from SharePoint
3. `./serve-dashboard.sh -b` — start Python HTTP server on
   localhost:8000, opens browser
4. Edit files, hard-refresh browser (Cmd+Shift+R) to see changes
5. `./dev-status.sh` — check branch state, version consistency,
   uncommitted changes
6. `git push -u origin feature/my-feature` — push and create PR

**Version management**: Version is bumped ONCE per feature branch (not
per commit). Update 9 locations: dashboard.html (5 query strings),
dashboard-body.html (version span), DASHBOARD-REFERENCE.md,
copilot-instructions.md, README.md. Changelog entries
(changelog.js, README.md version history) are written at
commit time with real content — NEVER placeholder text.

### IV. Theme System & UX Consistency

**Dual theme**: Dark mode (default) and light mode, toggled via
`#theme-toggle` button. Theme persists to localStorage key
`eshare-devops-dashboard-theme`.

**19 CSS custom properties** defined in `:root` with overrides in
`body.light-mode`:
- Backgrounds: `--bg-primary`, `--bg-secondary`, `--bg-tertiary`,
  `--bg-card`
- Text: `--text-primary`, `--text-secondary`, `--text-muted`
- Accents: `--accent-cyan`, `--accent-purple`, `--accent-green`,
  `--accent-orange`, `--accent-red`, `--accent-blue`,
  `--accent-pink`, `--accent-yellow`
- UI: `--border-color`, `--hover-bg`, `--shadow-color`
- Special: `--highlight-next`

All new CSS MUST use these variables. Never hardcode colors. If a new
color is needed, add it as a variable with both dark and light mode
values.

**Font system**: 'Space Grotesk' for UI, 'JetBrains Mono' for IDs and
code. Weights: 400/500/600/700.

**Z-index hierarchy** (MUST be respected): Sticky headers (1000) →
Filter dropdowns (1001) → Info panels (1002) → Modals (1100) →
Portal components (100010).

**Standard UI patterns that MUST be followed**:
- Info popups: `<span class="info-toggle">ℹ️ Info</span>` with
  consistent styling
- Relationship pills: Red (blocked/bug warnings), Purple (feature),
  Orange (issue/parent), Cyan (children)
- State badges: Green (Done), Blue (In Progress), Grey (New),
  Orange (Triaged), Red (Blocked)
- Collapsible sections: CSS transitions with localStorage persistence
- Sticky headers: `position: sticky; top: 85px; z-index: 90` for
  dashboard filter bars
- Filter row order: Search → Release → Customer → Priority → State →
  Team → Dashboard-specific → Clear All → Info

### V. State Persistence

ALL user-configurable UI state MUST persist to localStorage:
- Filter selections: via `{dashboardName}Filters` key
- Table sort state: auto-managed by `buildGenericTable` via
  `{tableId}-sort`
- Column widths: auto-managed by `buildGenericTable` via
  `gt-cw-{tableId}`
- Scroll positions: tracked in `tableScrollPositions` object
- Collapse states: per-section localStorage keys
- Theme: `eshare-devops-dashboard-theme`
- Quick toggles: (Active, Unreleased) via dashboard-specific
  localStorage

State MUST survive auto-refresh (60-second cycle), manual refresh
(↻ button), and page reload. Never add per-dashboard boilerplate for
state that `buildGenericTable` or `populateGenericFilterDropdowns`
already manages automatically.

### VI. ADO Integration & Inline Editing

Work items are editable inline via the Unified Modal and table cells.
All edits use `patchItemField()` to write to Azure DevOps `Custom.*`
fields, followed by `refreshUnifiedModalHeader()` for in-place
refresh. No full page reloads.

Editable fields: State, Priority, Tags, Customers, Architecture tags,
Release Version, Target Date, Assigned To, Bug Owner, CS Owner.
Non-editable (read-only): Bug Type, Ticket Category, relationship
pills, work item ID.

Drag-to-reorder in tables writes
`Microsoft.VSTS.Common.BacklogPriority` field to ADO.

### VII. Regression Testing

Every new spec MUST include a "Regression Test Plan" section with:

1. **Direct feature tests**: Verify the new feature works as specified
2. **Cross-dashboard impact**: If the change touches generic
   infrastructure, list ALL dashboards that use it and what to verify
   on each
3. **Auto-refresh test**: Verify the feature survives a 60-second
   auto-refresh cycle without visual disruption
4. **State persistence test**: Verify filter/sort/scroll state
   persists across page reload
5. **Theme test**: Verify the feature renders correctly in both dark
   and light mode
6. **Performance check**: For changes touching render paths, verify
   Clear Filters and auto-refresh remain responsive (< 2 seconds)
7. **Console check**: Verify no JavaScript errors in browser console
   (F12)

The test plan MUST be concrete and executable — not abstract. Include
specific steps: "Navigate to Bugs dashboard → Apply Priority P1
filter → Verify table shows only P1 bugs → Click ↻ refresh → Verify
P1 filter is still active."

### VIII. Code Organization

**4-file modular architecture** (no single-file monolith):
- `dashboard.html` — Shell/loader, fetches other files dynamically
- `dashboard-body.html` — HTML structure (nav, views, modals)
- `dashboard.css` — All styles (use CSS variables, no inline styles)
- `dashboard.js` — Main application logic (~19,500 lines, single
  file)
- `dashboard-loader.js` — Data loading module (SharePoint/local file
  fetching)
- `capacity-planning-data.js` — Capacity planning helper functions
- `changelog.js` — Version changelog data

**Key code locations in dashboard.js**:
- Dashboard Filter Registry: ~line 7430
- `populateGenericFilterDropdowns`: ~line 7517
- `applyGenericSecondaryFilters`: ~line 7379
- `buildGenericTable`: ~line 9378
- `genericTableDefaultRenderCell`: ~line 10297
- `performAutoRefresh`: ~line 19393
- `scheduleAutoRefresh`: ~line 19369

New generic infrastructure belongs in dashboard.js near the existing
generic functions. Dashboard-specific rendering functions live in
their respective dashboard sections.

### IX. Performance Considerations

**Patterns to follow**:
- Data hash comparison before re-render (skip if unchanged)
- Cache expensive lookups (e.g., `buildOrgMembersMap()`) outside loops
- Early returns when no active filters
- Batch API calls (e.g., `batchFetchCommentCounts()` with 200 items
  per call)
- Lazy evaluation in registry (`() => filters` not `filters`)
- Chart animation disabled during auto-refresh (`isAutoRefresh` flag)

**Anti-patterns to avoid**:
- Rebuilding org chart maps inside filter loops
- Multiple full re-renders in sequence (batch into one)
- Blocking API calls in render path
- Uncached repeated DOM queries

## Summary of Alerts

Specs and plans MUST flag these situations:

1. ⚠️ **SPECIFIC CODE**: Dashboard-specific logic where generic
   infrastructure exists — requires justification
2. ⚠️ **HARDCODED COLOR**: Any color not using CSS custom properties —
   must add variable
3. ⚠️ **NEW FILTER TYPE**: Filter not built by
   `populateGenericFilterDropdowns` — must extend generic system
4. ⚠️ **CUSTOM TABLE**: Table HTML not built by `buildGenericTable` —
   requires justification
5. ⚠️ **STATE NOT PERSISTED**: User-configurable state not saved to
   localStorage — must add persistence
6. ⚠️ **NO REGRESSION PLAN**: Missing regression test section — must
   add before implementation
7. ⚠️ **PERFORMANCE RISK**: Changes to render-critical paths — must
   include performance verification

## Governance

This constitution is the authoritative source for project-wide rules
and constraints. All specs, plans, and task lists MUST comply.

**Amendment procedure**:
1. Propose change via PR with rationale
2. Update this file with new principle or modification
3. Increment version per semantic versioning (see below)
4. Verify all templates remain consistent (see Sync Impact Report)
5. Merge to `main`

**Versioning policy** (semantic versioning):
- MAJOR: Backward-incompatible principle removal or redefinition
- MINOR: New principle added or existing principle materially expanded
- PATCH: Clarifications, wording fixes, non-semantic refinements

**Compliance review**:
- The plan template's "Constitution Check" section gates Phase 0
  research — plans MUST pass all relevant principle checks before
  proceeding
- PRs that touch generic infrastructure (Principle I) MUST include
  cross-dashboard verification
- Runtime development guidance lives in `DASHBOARD-REFERENCE.md` and
  `.github/copilot-instructions.md`; those files provide operational
  detail but this constitution takes precedence on principle conflicts

**Version**: 1.1.0 | **Ratified**: 2026-03-27 | **Last Amended**: 2026-04-01
