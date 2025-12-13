# eShare DevOps Dashboard - Claude Code Context

## Project Overview
This is a reporting dashboard that visualizes Azure DevOps work items (Features, Delivery Slices, Bugs, Issues, Tasks). It runs as a single HTML file served from SharePoint.

## Architecture
- **Templates/**: HTML template parts that get concatenated
- **generate_dashboard.py**: Python script that combines templates + CSV data → final HTML
- **Data files** (not in repo): `ALL_Items.csv`, `Org_Chart.csv` managed by Power Automate

## Key Files
| File | Purpose |
|------|---------|
| `Templates/dashboard_v3_part1.html` | HTML structure + CSS |
| `Templates/dashboard_v3_part2.html` | Core JavaScript + data placeholder |
| `Templates/dashboard_v3_part3.html` | Releases, Customers, Bugs views |
| `Templates/dashboard_v3_part4.html` | Teams, Org Chart, Validation views |
| `generate_dashboard.py` | Generation script |
| `DASHBOARD_README.md` | User documentation |

## Development Workflow
1. Make changes to template files
2. Run `python3 generate_dashboard.py` to generate output
3. Open `ᵉShare DevOps Dashboard.html` in browser to validate
4. If good: update version number, commit, push

## Version Management
When making changes:
1. Increment `CURRENT_VERSION` in `generate_dashboard.py`
2. Update version in `Templates/dashboard_v3_part1.html`: `<span class="version">vXX</span>`
3. Add entry to Version History in `DASHBOARD_README.md`

## Current Version: v79

## UI Patterns for All Dashboards

### Label-Based Checkbox Filters
All filter dropdowns use `<label class="filter-dropdown-option">` elements so clicking anywhere on the row toggles the checkbox. Use `onchange` handlers (not `onclick`) on the checkbox input.

### Multi-Select Tag Filters with AND Logic
When a filter allows multiple selections (like Tags), use AND logic by default:
```javascript
// Show items that have ALL selected tags
return roadmapFilters.tags.every(selectedTag => featureTags.includes(selectedTag));
```

### Search Filter Integration
When adding a search filter to a dashboard:
1. Add search input to sticky header with `class="filter-search-input"`
2. Create a search state variable (e.g., `releasesSearchFilter = ''`)
3. Add search to `getHeaderFilteredItems()` - always apply search (no exclusion)
4. Add search to `hasActiveFilters()` check
5. Clear search in `clearAllFilters()`
6. Update cross-filter dropdown population to respect search

### Cross-Filter Dropdown Aware of Search
Filter dropdowns should only show options relevant to current search:
```javascript
function getItemsExcludingFilter(items, excludeFilter) {
    return items.filter(item => {
        // Always apply search filter (never excluded)
        if (searchFilter) {
            const searchLower = searchFilter.toLowerCase();
            const titleMatch = (item.title || '').toLowerCase().includes(searchLower);
            const idMatch = String(item.id).includes(searchFilter);
            if (!titleMatch && !idMatch) return false;
        }
        // ... other filters with excludeFilter logic ...
    });
}
```

### Chart Highlighting for Search Results
When search is active, highlight relevant bars/columns:
```javascript
const barColors = releases.map(r => {
    if (searchFilter && releaseInfo[r].matchingItems > 0) {
        return 'rgba(34, 211, 238, 1)'; // Bright cyan for matches
    }
    return searchFilter ? 'rgba(100, 116, 139, 0.4)' : colors.primary[0];
});
```

### Preserving Scroll Position on Re-render
When checkbox selection triggers a re-render that rebuilds the dropdown:
```javascript
// Save scroll position before re-render
const optionsContainer = document.getElementById('dropdown-options');
const scrollTop = optionsContainer ? optionsContainer.scrollTop : 0;
// ... re-render ...
// Restore scroll position after re-render
const newOptionsContainer = document.getElementById('dropdown-options');
if (newOptionsContainer) newOptionsContainer.scrollTop = scrollTop;
```

### Info Popup Standardization
All dashboards use consistent info popup: `<span class="info-toggle">ℹ️ Info</span>`

### Flexible Filter Row Layout
Filter dropdowns use `flex: 1` with min/max widths to fill available space:
- `.filter-dropdown { flex: 1; min-width: 100px; max-width: 200px; }`
- `.filter-search-input { flex: 1; min-width: 120px; max-width: 200px; }`
- Labels and buttons use `flex-shrink: 0`

## Dual-Mode Filter Pattern
When implementing multi-select checkbox filters that need to support both inclusion and exclusion:

**The Problem:**
- User selects "Blocked" → expects to see items WITH "Blocked" tag (inclusion)
- User clicks "Select All" then unchecks "Blocked" → expects to see items WITHOUT "Blocked" tag (exclusion)
- Same checkbox state can mean different things depending on how user got there

**The Solution:**
1. Add a `[filterType]ExclusionMode` flag to filter state (e.g., `tagsExclusionMode: false`)
2. When "Select All" is clicked, set `exclusionMode = true`
3. When "Clear" is clicked or all items are manually unchecked, set `exclusionMode = false`
4. In the filter logic:
   - If `exclusionMode = true`: Calculate unchecked items and EXCLUDE items matching those
   - If `exclusionMode = false`: INCLUDE items matching selected items (using `.some()`)

**Example implementation (from Roadmap Tag filter):**
```javascript
if (roadmapFilters.tags.length > 0) {
    if (roadmapFilters.tagsExclusionMode) {
        // Exclusion mode: hide items with unchecked tags
        const allAvailableTags = new Set();
        // ... collect all available tags ...
        const uncheckedTags = [...allAvailableTags].filter(t => !roadmapFilters.tags.includes(t));
        features = features.filter(f => {
            const featureTags = (f.tags || '').split(';').map(t => t.trim()).filter(t => t);
            return !featureTags.some(tag => uncheckedTags.includes(tag));
        });
    } else {
        // Inclusion mode: show items with any selected tag
        features = features.filter(f => {
            const featureTags = (f.tags || '').split(';').map(t => t.trim()).filter(t => t);
            return featureTags.some(tag => roadmapFilters.tags.includes(tag));
        });
    }
}
```

## v79 Summary (December 2024)
**State Persistence for ALL Dashboard Views:**
Extended localStorage state persistence (originally from v75 Roadmap) to ALL dashboard views. Filter selections now survive page refresh with 24-hour expiration.

**Views Updated:**
- **Executive:** Team/Type header dropdowns and chart filters persist
- **Customers:** Team filter and chart filters persist
- **Bugs:** Date range, custom dates, State/Type/Priority trend filters, categorization chart filters
- **Teams:** Time period, team details selection, engineer filter selection
- **Tasks:** Parent type, team, and state filters
- **Details:** Type, team, and state filters
- **Validation:** Type, team, and state filters
- **Releases:** Already working (from earlier implementation)
- **Roadmap:** Already working (from v75)

**Implementation Pattern - Multi-View State Persistence:**
```javascript
// 1. Add state flags for each view
let executiveStateWasLoaded = false;
let customersStateWasLoaded = false;
let bugsStateWasLoaded = false;
// ... etc for each view

// 2. Cache loaded state for DOM restoration
let loadedStateCache = null;

// 3. In saveStateToStorage(), capture all view states:
const state = {
    currentView: currentView,
    // Executive
    execChartFilters: execChartFilters,
    execTeamFilter: document.getElementById('exec-team-filter')?.value || 'all',
    // Bugs
    bugTrendFilters: bugTrendFilters,
    selectedBugDateRange: selectedBugDateRange,
    bugTrendStartDate: document.getElementById('bug-trend-start')?.value || '',
    // ... etc
    timestamp: Date.now()
};

// 4. In applyLoadedState(), restore state variables and set flags:
if (state.bugTrendFilters) {
    Object.assign(bugTrendFilters, state.bugTrendFilters);
}
bugsStateWasLoaded = true;

// 5. In switchView(), sync UI after render and re-render with filters:
if (bugsStateWasLoaded && view === 'bugs') {
    syncBugsFilterState();
    bugsStateWasLoaded = false;
    applyBugFilters(); // IMPORTANT: Re-render with restored filters
}
```

**Key Implementation Detail - Sync Then Re-render:**
After syncing checkbox states from localStorage, you MUST call the view's render/apply function:
```javascript
// Wrong - checkboxes are synced but data doesn't reflect the filter
syncBugsFilterState();
bugsStateWasLoaded = false;

// Correct - checkboxes are synced AND data is re-rendered with filters
syncBugsFilterState();
bugsStateWasLoaded = false;
applyBugFilters(); // Re-render with restored filters
```

**Pattern - Sync Function for Checkbox Filters:**
```javascript
function syncBugsFilterState() {
    // State filter uses #state-options (no prefix)
    ['state'].forEach(filterType => {
        const checkboxes = document.querySelectorAll(`#${filterType}-options input[type="checkbox"]:not(#${filterType}-select-all)`);
        checkboxes.forEach(cb => {
            cb.checked = bugTrendFilters[filterType].includes(cb.value);
        });
    });
    updateStateFilterDisplay();

    // Type/Priority use #bug-type-options pattern
    ['type', 'priority'].forEach(filterType => {
        const checkboxes = document.querySelectorAll(`#bug-${filterType}-options input[type="checkbox"]:not(#bug-${filterType}-select-all)`);
        checkboxes.forEach(cb => {
            cb.checked = bugTrendFilters[filterType].includes(cb.value);
        });
        updateBugFilterDisplay(filterType);
    });
}
```

**Pattern - Teams View Engineer Filter Preservation:**
When a view has a function that resets filters (like `expandTeamDetails()` calling `resetEngFilters()`):
```javascript
function syncTeamsFilterState() {
    // ... time period restoration ...

    if (currentTeamDetails) {
        // Save filters BEFORE expandTeamDetails() resets them
        const savedEngFilters = JSON.parse(JSON.stringify(engFilters));
        const savedSelectedEngineers = [...selectedEngineers];

        expandTeamDetails(currentTeamDetails);

        // Restore after expansion completes
        setTimeout(() => {
            engFilters = savedEngFilters;
            selectedEngineers = savedSelectedEngineers;
            // Sync checkboxes...
            renderEngineerDetails();
        }, 150);
    }
}
```

**Pattern - Date Range Restoration:**
For views with date range selectors that initialize with defaults:
```javascript
function initBugTrendDates() {
    // Check if we should use restored state instead of defaults
    if (bugsStateWasLoaded && loadedStateCache) {
        const range = selectedBugDateRange;
        // Update button state
        document.querySelectorAll('.date-range-buttons .time-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.range === range);
        });
        // Set dates from cache or calculate from range
        if (range === 'custom' && loadedStateCache.bugTrendStartDate) {
            document.getElementById('bug-trend-start').value = loadedStateCache.bugTrendStartDate;
            document.getElementById('bug-trend-end').value = loadedStateCache.bugTrendEndDate;
        } else {
            // Calculate dates based on range (week/month/quarter)
        }
        return; // Skip default initialization
    }
    // Default initialization...
}
```

## v78 Summary (December 2024)
**Roadmap Dashboard - Priority Filter & Column:**
- Added Priority filter dropdown to sticky header (between Iteration and Release filters)
- Priority values displayed as P1, P2, P3, P4 with "(No Priority)" option
- Priorities sorted numerically (P1 first, "(No Priority)" last)
- Added Priority column to Feature Details table (after Customers column)
- Priority column is sortable like other columns
- Updated total row colspan from 7 to 8

**Roadmap Dashboard - Collapsible Team Summary:**
- Section 2 "Team Summary" is now collapsible
- Collapsed by default to save screen space
- Click header to expand/collapse
- Visual indicator (▼ arrow) rotates when collapsed
- Collapse state persisted via localStorage

**Implementation Pattern - Collapsible Section:**
```html
<!-- HTML structure for collapsible section -->
<div class="roadmap-section collapsible collapsed" id="roadmap-section-teams">
    <div class="roadmap-section-header" onclick="toggleRoadmapTeamSummary()">
        <span class="section-number">2</span>
        <span>Team Summary</span>
        <span class="collapse-indicator">▼</span>
    </div>
    <div class="section-content">
        <!-- Content here -->
    </div>
</div>
```

```css
/* CSS for collapsible sections */
.roadmap-section.collapsible .roadmap-section-header {
    cursor: pointer;
    user-select: none;
}
.roadmap-section.collapsible .collapse-indicator {
    margin-left: auto;
    font-size: 0.7rem;
    color: var(--text-muted);
    transition: transform 0.2s;
}
.roadmap-section.collapsible.collapsed .collapse-indicator {
    transform: rotate(-90deg);
}
.roadmap-section.collapsible .section-content {
    overflow: hidden;
    transition: max-height 0.3s ease-out, opacity 0.2s ease-out;
    max-height: 2000px;
    opacity: 1;
}
.roadmap-section.collapsible.collapsed .section-content {
    max-height: 0;
    opacity: 0;
}
```

```javascript
// Toggle function with state persistence
function toggleRoadmapTeamSummary() {
    const section = document.getElementById('roadmap-section-teams');
    if (section) {
        section.classList.toggle('collapsed');
        roadmapTeamSummaryCollapsed = section.classList.contains('collapsed');
        saveStateToStorage(); // Persist collapse state
    }
}
```

**Implementation Pattern - Adding a New Filter:**
When adding a new filter to a dashboard:
1. Add to filter state object: `roadmapFilters.priorities = []`
2. Add filter HTML in part1.html (dropdown structure)
3. Add filter logic in getFilteredRoadmapFeatures()
4. Update isFiltered check in renderRoadmapView()
5. Add to populateRoadmapFilterDropdowns() - extract unique values and build dropdown
6. Add to getFilterKey() and getFilterLabel() mappings
7. Add to syncRoadmapFilterDropdowns() and clearAllRoadmapFilters()
8. Add CSS for column (.col-priority) if adding table column

## v77 Summary (December 2024)
**Roadmap Dashboard - OKR Summary Effort Percentage:**
- Changed OKR Summary table Effort row to show percentage as primary value
- Percentage calculated as proportion of total effort across all 4 OKR categories
- Days shown as secondary value in smaller, muted text
- Percentage is filter-aware: if filters result in all effort in one category, that category shows 100%
- Example display: "45% 12.5d" where 45% is primary and 12.5d is secondary

**Implementation Pattern - Dual Value Display (Primary % + Secondary Days):**
```javascript
// Calculate total effort across all categories
const totalEffort = results.reduce((sum, r) => sum + r.effort, 0);

// Display percentage as primary, days as secondary
results.map(r => {
    const pct = totalEffort > 0 ? (r.effort / totalEffort * 100) : 0;
    const pctDisplay = pct > 0 ? pct.toFixed(0) + '%' : '0%';
    const daysDisplay = r.effort > 0 ? r.effort.toFixed(1) + 'd' : '0d';
    return `<td class="effort-value">
        <span class="effort-pct">${pctDisplay}</span>
        <span class="effort-days">${daysDisplay}</span>
    </td>`;
});
```

**CSS Pattern - Primary/Secondary Value Styling:**
```css
.effort-value .effort-pct {
    font-weight: 700;
    font-size: 1.25rem;
}

.effort-value .effort-days {
    font-size: 0.8rem;
    font-weight: 400;
    color: var(--text-muted);
    margin-left: 0.4rem;
}
```

## v76 Summary (December 2024)
**Roadmap Dashboard - Three-Section Restructure:**
- Reorganized Roadmap view into 3 distinct sections with numbered headers
- **Section 1: OKR Summary** - Strategy alignment table with 4 OKR columns
- **Section 2: Team Summary** - Existing team effort cards (renamed from "Team View")
- **Section 3: Feature Details** - Feature table with ADO backlog link (renamed from "Feature Roadmap Details")

**OKR Summary Table (Section 1):**
- 4 columns matching OKR strategy categories:
  - Column 1: "eSHARE is must-have" (tags starting with `1:`)
  - Column 2: "eSHARE is the collaboration standard" (tags starting with `2:`)
  - Column 3: "eSHARE deployability" (tags starting with `3:`)
  - Column 4: "eSHARE is customer-focused, stable and secure" (tags starting with `4:`)
- Row 1: Feature count per category (clickable to filter)
- Row 2: Sum of effort per category
- Footer note shows count of features without OKR tags
- Error message appears if features have tags in multiple categories (with "Show in table" link)
- All values respond to header filters (Team, Iteration, etc.)

**Clickable OKR Feature Counts:**
- Clicking a feature count in OKR Summary filters by that category's tags
- Preserves all other existing filters (only updates Tag filter)
- Tag dropdown checkboxes sync to show selected tags
- No auto-scroll - page stays in position

**Implementation Pattern - OKR Category Filtering:**
```javascript
// Strategy categories definition
const strategyCategories = [
    { prefix: '1:', label: 'eSHARE is must-have' },
    { prefix: '2:', label: 'eSHARE is the collaboration standard' },
    { prefix: '3:', label: 'eSHARE deployability' },
    { prefix: '4:', label: 'eSHARE is customer-focused, stable and secure' }
];

// Filter by OKR category - preserves other filters, only updates tags
function filterByOkrCategory(prefix) {
    // Get all tags that start with this prefix
    const matchingTags = new Set();
    allFeatures.forEach(f => {
        const tags = (f.tags || '').split(';').map(t => t.trim()).filter(t => t);
        tags.forEach(tag => {
            if (tag.startsWith(prefix)) matchingTags.add(tag);
        });
    });

    // Update only the tag filter (preserve all other filters)
    roadmapFilters.tags = [...matchingTags];
    roadmapFilters.tagsExclusionMode = false;
    roadmapFilters.tagsLogicMode = 'or';

    // Sync checkboxes AFTER render
    renderRoadmapView();
    const tagOptionsContainer = document.getElementById('roadmap-tag-options');
    if (tagOptionsContainer) {
        tagOptionsContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = roadmapFilters.tags.includes(cb.value);
        });
    }
}
```

**Implementation Pattern - Checkbox Value Attribute:**
When dynamically creating checkbox filters that need to be programmatically synced, always include a `value` attribute:
```javascript
// Without value attribute, cb.value returns empty string
<input type="checkbox" onchange="handleChange('${tagName}', this.checked)">

// With value attribute, cb.value returns the tag name for syncing
<input type="checkbox" value="${tagName}" onchange="handleChange('${tagName}', this.checked)">
```

**Implementation Pattern - Multi-Category Detection:**
```javascript
// Track features matching multiple OKR categories
const multiCategoryFeatures = [];
features.forEach(f => {
    const matchedCategories = [];
    strategyCategories.forEach((cat, idx) => {
        if (tags.some(tag => tag.startsWith(cat.prefix))) {
            matchedCategories.push(idx);
        }
    });
    if (matchedCategories.length > 1) {
        multiCategoryFeatures.push({ id: f.id, categories: matchedCategories });
    }
});
```

## v75 Summary (December 2024)
**Roadmap Dashboard - Tags Column:**
- Added Tags column to table between Customers and Assigned To columns
- Tags displayed comma-separated with ellipsis for overflow (hover for full list)
- Column is sortable; CSS class `.col-tags` with width 150px

**Roadmap Dashboard - State Persistence (localStorage):**
- Current view preserved across page refreshes (no longer resets to Executive)
- All Roadmap filter selections saved automatically to localStorage
- Sort state (column and direction) also persisted
- State expires after 24 hours to prevent stale data issues
- Key: `eshare-devops-dashboard-state`

**Roadmap Dashboard - Default Filters Removed:**
- Release filter no longer defaults to "(No Release)" - starts empty
- Tag filter no longer defaults to "Candidate" - starts empty
- All filters now behave consistently (empty = show all)
- Clear All now clears all filters completely

**Roadmap Dashboard - AND/OR Toggle for Tag Filter:**
- New "Match:" toggle in Tag dropdown with "Any (OR)" and "All (AND)" buttons
- OR mode (default): Shows features matching ANY selected tag
- AND mode: Shows features matching ALL selected tags
- Logic mode preference is persisted with other filter state

**Implementation Pattern - State Persistence:**
```javascript
// Save state to localStorage
const STORAGE_KEY = 'eshare-devops-dashboard-state';
function saveStateToStorage() {
    const state = {
        currentView: currentView,
        roadmapFilters: roadmapFilters,
        roadmapSortState: roadmapSortState,
        timestamp: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

// Load and apply state on page load
const loadedState = loadStateFromStorage();
if (loadedState) applyLoadedState(loadedState);

// Sync dropdown UI after state load
if (stateWasLoaded) {
    syncRoadmapFilterDropdowns(); // Updates checkboxes to match loaded state
    stateWasLoaded = false;
}
```

**Implementation Pattern - AND/OR Filter Logic Toggle:**
```javascript
// Filter state includes logic mode
let roadmapFilters = {
    tags: [],
    tagsLogicMode: 'or'  // 'and' or 'or'
};

// Filter logic respects mode
if (roadmapFilters.tagsLogicMode === 'and') {
    return roadmapFilters.tags.every(tag => featureTags.includes(tag));
} else {
    return roadmapFilters.tags.some(tag => featureTags.includes(tag));
}

// UI toggle buttons
<div class="tag-logic-toggle">
    <span class="tag-logic-label">Match:</span>
    <button class="tag-logic-btn ${mode === 'or' ? 'active' : ''}" onclick="setTagLogicMode('or')">Any (OR)</button>
    <button class="tag-logic-btn ${mode === 'and' ? 'active' : ''}" onclick="setTagLogicMode('and')">All (AND)</button>
</div>
```

## v74 Summary (December 2024)
**Roadmap Dashboard - Release Version Filter:**
- Added Release Version filter dropdown (between Iteration and Tag filters)
- Default filter is "(No Release)" to show Features with no release version assigned
- Previously, this was a hardcoded filter in `getRoadmapFeatures()` - now it's user-controllable
- Dual-mode filter behavior: inclusion mode for manual selections, exclusion mode after "Select All"
- Clear All preserves both "(No Release)" and "Candidate" defaults
- Updated Info popup to document the two default filters

**Release Version Column in Table:**
- Added Release column between Assigned To and Effort columns
- Column is sortable like other columns
- CSS class `.col-release` with width 120px

**Bug Fix - Team + Iteration Filter Combination:**
- Fixed issue where Team and Iteration filters were evaluated independently
- Before: Feature passed if it had ANY slice from selected team AND ANY slice in selected iteration (could be different slices)
- After: Feature passes only if it has at least one slice matching BOTH team AND iteration filters
- Example: Analytics + CY2025Q4-Dec now correctly excludes features that only have Analytics slices in October

**Bug Fix - Effort Column Sorting:**
- Fixed sorting by Effort column which wasn't working
- Effort values are calculated dynamically in `featureEffortMap`, not stored on the item
- `sortRoadmapItems()` now accepts optional `effortMap` parameter
- When sorting by 'effort', looks up values from the map instead of item properties

**Implementation Pattern - Release Filter:**
- Filter dropdown with "(No Release)" as first option, followed by sorted release versions
- `roadmapFilters.releases` defaults to `['(No Release)']`
- `roadmapFilters.releasesExclusionMode` tracks inclusion vs exclusion mode
- `isFiltered` check treats `releases: ['(No Release)']` as default (not filtered) state

**Implementation Pattern - Combined Slice Filters:**
When filtering features by delivery slice properties (team, iteration), combine the filters:
```javascript
// Apply team and iteration filters together (based on delivery slices)
// When both are active, a feature must have at least one slice that matches BOTH filters
if (roadmapFilters.teams.length > 0 || roadmapFilters.iterations.length > 0) {
    features = features.filter(f => {
        const slices = getDeliverySlicesForFeatures([f.id]);
        return slices.some(ds => {
            const team = getLastPathSegment(ds.areaPath) || '(No Team)';
            const iteration = getLastPathSegment(ds.iterationPath) || '(No Iteration)';
            const teamMatch = roadmapFilters.teams.length === 0 || roadmapFilters.teams.includes(team);
            const iterationMatch = roadmapFilters.iterations.length === 0 || roadmapFilters.iterations.includes(iteration);
            return teamMatch && iterationMatch;
        });
    });
}
```

## v73 Summary (December 2024)
**Roadmap Dashboard - Team-Centric UX Improvements:**
- Added "Link to ADO Feature Backlog" hyperlink next to "Feature Roadmap" title
- Team cards are now clickable: click to filter by that team (syncs with Team dropdown)
- "Total Effort" card clears team filter when clicked
- Added Effort column to table showing sum of child delivery slice efforts
- When team/iteration filters are active, Effort column shows only matching effort
- Added total row at bottom of table with sum of all visible effort
- Added inline effort summary badge above table showing "Table Total: Xd (Team · Iteration)"

**Delivery Slices Popup Improvements:**
- When team/iteration filters are active, matching slices appear at the top
- Non-matching slices are visible but grayed out (45% opacity)
- Effort summary shows filtered effort vs total effort
- Example: "Analytics · CY2025Q4-Dec Effort: 12.5d / Total: 45.0d"

**New Patterns:**
- Clickable stat cards that sync with filter dropdowns
- Team/iteration-aware popup sorting and styling
- Combined filter effort calculations (team + iteration)

## v72 Summary (December 2024)
**Releases & Roadmap Dashboards - UX Improvements:**
- Search filter added to Releases dashboard (searches title and ID)
- Search placeholder updated to "Search titles and IDs..." on both dashboards
- Checkbox click behavior aligned: `<label>` elements make entire row clickable
- Release filter scroll position preserved when selecting items
- Tag filter uses AND logic (items must have ALL selected tags)
- Filter dropdowns expand to fill available space (`flex: 1`)
- Info popups standardized to "ℹ️ Info" across all dashboards

**Releases Dashboard - Search Integration:**
- Filter dropdowns only show options relevant to search results
- Release dropdown shows matching item count when search is active
- Items by Release chart highlights bars with matching items
- Release Version column added to all tables

**Documentation:**
- Added UI Patterns section to CLAUDE.md for reuse across dashboards

## v71 Summary (December 2024)
**Roadmap View - Tag Filter Refactor:**
- Refactored base filter: now shows all Features with no Release Version (tag filtering moved to UI)
- "Candidate" tag selected by default in Tag dropdown (same behavior as before, but now user-controllable)
- Dual-mode tag filter: inclusion mode for manual selections, exclusion mode after "Select All"
- Clear All button preserves Candidate as default (resets to default state, not empty)
- Clear All button hidden when filters are in default state (only Candidate selected)
- Compact sticky header (reduced padding from 0.25rem to 0.15rem, font sizes reduced)
- Filter dropdowns widened from 120px to 140px for better readability
- Info popup updated: "Filtered by 'Candidate' tag (default)"

**Default Filter State Pattern:**
When a filter has a default value that should be preserved:
1. Initialize filter state with default value (e.g., `tags: ['Candidate']`)
2. Set initial display text in HTML to match default
3. In `clearAllFilters()`, reset to default instead of empty
4. In `isFiltered` check, treat default state as "not filtered" for UI purposes (hide Clear button)

## v70 Summary (December 2024)
Key changes implemented in v70:

**Releases View Fixes:**
- Dropdown search filter for release selection
- Scroll-to-close for filter dropdowns
- Sticky header Clear button fix (`flex-wrap: nowrap`)
- Stat cards now non-clickable (removed hover effect)

**Validation View:**
- Data Source Validation section comparing CSV source counts vs dashboard counts
- Uses `CSV_VALIDATION_DATA_PLACEHOLDER` injected by generator

**Infrastructure:**
- `-p/--publish` flag: default outputs to local directory, `--publish` outputs to SharePoint
- Retry logic (5 attempts with exponential backoff) for OneDrive file locks
- `reload-launchd-agent.sh` helper script for testing scheduled job
- Plist updated to include `--publish` for scheduled runs

**Key paths:**
- Local output: `/Users/tonythem/GitHub/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html`
- Published output: SharePoint `Product Planning/ᵉShare DevOps Dashboard.html`
- CSV source: SharePoint `Product Planning/ALL Items.csv`

## Data Schema
The dashboard expects specific field names. See `DASHBOARD_README.md` for the complete schema.

## Commands for Claude
- To generate dashboard (local): `python3 generate_dashboard.py`
- To generate and publish: `python3 generate_dashboard.py --publish`
- To generate with custom CSV: `python3 generate_dashboard.py -c "../ALL_Items.csv"`
- To open in browser (macOS): `open "eSHARE-DevOps-Dashboard.html"`
- To reload launchd agent: `./reload-launchd-agent.sh`

## Testing Changes
After making edits, always:
1. Run the generator
2. Check browser console (F12) for JavaScript errors
3. Verify file size is ~5MB (not ~350KB which indicates missing data)
