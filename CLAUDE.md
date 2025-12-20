# eShare DevOps Dashboard - Claude Code Context

## Project Overview
This is a reporting dashboard that visualizes Azure DevOps work items (Features, Delivery Slices, Bugs, Issues, Tasks). It runs as a single HTML file served from SharePoint.

## Architecture
- **Templates/**: Development HTML template parts (for local testing)
- **Templates-Production/**: Production HTML template parts (for scheduled publishing)
- **generate_dashboard.py**: Python script that combines templates + CSV data → final HTML
- **Data files** (not in repo): `ALL_Items.csv`, `Org_Chart.csv` managed by Power Automate

## Key Files
| File | Purpose |
|------|---------|
| `Templates/dashboard_v3_part1.html` | HTML structure + CSS (DEV) |
| `Templates/dashboard_v3_part2.html` | Core JavaScript + data placeholder (DEV) |
| `Templates/dashboard_v3_part3.html` | Releases, Customers, Bugs views (DEV) |
| `Templates/dashboard_v3_part4.html` | Teams, Org Chart, Validation views (DEV) |
| `Templates-Production/*` | Production templates (stable version) |
| `generate_dashboard.py` | Generation script |
| `DASHBOARD_README.md` | User documentation |

## Development vs Production Workflow

**Two separate template directories:**
- `Templates/` - Development templates for local testing
- `Templates-Production/` - Production templates used by the 60-second launchd job

**Development workflow:**
1. Make changes to `Templates/` files
2. Run `python3 generate_dashboard.py` (no flags) to generate to local DEV file
3. Open `eSHARE-DevOps-Dashboard.html` in browser to validate
4. Repeat until changes are ready

**Publishing to production:**
1. When ready, copy updated templates to `Templates-Production/`:
   ```bash
   cp Templates/*.html Templates-Production/
   ```
2. Update version in `Templates-Production/dashboard_v3_part1.html`
3. Run `python3 generate_dashboard.py --publish` to publish once
4. The launchd job will continue refreshing data every 60 seconds using production templates

**Key paths:**
- DEV output: `/Users/tonythem/GitHub/athemelis/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html`
- PROD output: SharePoint `Product Planning/eSHARE-DevOps-Dashboard.html`

**Shell script behavior:**
- `./update-eSHARE-DevOps-Dashboard.sh` → Uses `Templates/`, outputs to DEV
- `./update-eSHARE-DevOps-Dashboard.sh --publish` → Uses `Templates-Production/`, outputs to PROD

## Version Management
When making changes:
1. Increment `CURRENT_VERSION` in `generate_dashboard.py`
2. Update version in `Templates/dashboard_v3_part1.html`: `<span class="version">vXX</span>`
3. Add entry to Version History in `DASHBOARD_README.md`

## Git Commit and Push Requirements
**IMPORTANT:** When committing changes, you MUST:
1. Include ALL modified files in the project folder (use `git add .` or explicitly add each file)
2. Include the generated `eSHARE-DevOps-Dashboard.html` file - this is the local DEV dashboard
3. Always push changes to GitHub after committing
4. Verify the push was successful before considering the task complete

**Commit workflow:**
```bash
# Stage all changes including generated files
git add .

# Commit with version summary
git commit -m "vXX: [summary of changes]"

# Push to GitHub
git push

# Verify push was successful (should show "Everything up-to-date" or commit info)
```

## Current Version: v100

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

## Generic Filter Components (v83+)

### Philosophy: Shared Components for Cross-Dashboard Consistency
When a filter type appears on multiple dashboards, use a **generic component** instead of dashboard-specific implementations. This ensures:
- Visual consistency (same dropdown width, styling, options)
- Behavioral consistency (same Select All/Clear logic, scroll preservation)
- Single point of maintenance (fix once, works everywhere)

### Generic Release Filter Component (part2.html)
The Release filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 680-1015)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `computeReleaseInfo(items)` | Analyzes work items → releases, dates, counts |
| `buildReleaseFilterDropdown(config)` | Builds dropdown HTML with search, options, actions |
| `handleGenericReleaseChange(dashboardId, ...)` | Routes checkbox changes to correct dashboard state |
| `selectAllGenericRelease(dashboardId, ...)` | Select All handler |
| `clearGenericRelease(dashboardId, ...)` | Clear handler |
| `updateGenericReleaseDisplay(dashboardId)` | Updates display text |
| `syncGenericReleaseFilter(dashboardId)` | Syncs checkboxes after localStorage load |

**Usage - Adding Release Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the dropdown structure:
<span class="filter-row-label">Release:</span>
<div class="filter-dropdown" id="DASHBOARD-release-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-release-dropdown')">
        <span id="DASHBOARD-release-display">All Releases</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-release-menu">
        <!-- Populated dynamically -->
    </div>
</div>

// 2. In CSS (part1.html), add to wide dropdown list:
#DASHBOARD-release-menu { right: auto; min-width: 280px; }

// 3. In render function, populate the dropdown:
const releaseMenu = document.getElementById('DASHBOARD-release-menu');
if (releaseMenu) {
    const items = workItems.filter(w => w.type === 'YourType');
    releaseMenu.innerHTML = buildReleaseFilterDropdown({
        dashboardId: 'DASHBOARD',  // Must match ID prefix
        items: items,
        selectedReleases: dashboardFilters.releases
    });
}

// 4. In handleGenericReleaseChange(), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    openDropdownId = 'DASHBOARD-release-dropdown';
    // Update state, call render function
}

// 5. In filter logic, handle all three categories:
const getItemReleaseCategory = (item) => {
    if (item.releaseVersion?.trim()) return item.releaseVersion.trim();
    return item.targetDate ? '(Needs Release)' : '(No Release)';
};
```

**Release Categories:**
- **Regular releases** - Items with `releaseVersion` set (sorted by target date)
- **⚠️ Needs Release** - Items with `targetDate` but no `releaseVersion` (warning styling)
- **(No Release)** - Items with neither `releaseVersion` nor `targetDate`

### Creating a New Generic Filter Component
When adding a new filter type that will appear on multiple dashboards:

1. **Create compute function** in part2.html:
   ```javascript
   function computeFilterInfo(items) {
       // Return { options: [...], optionInfo: {...}, counts }
   }
   ```

2. **Create build function** in part2.html:
   ```javascript
   function buildFilterDropdown(config) {
       const { dashboardId, items, selectedValues } = config;
       // Return HTML string with data-search-value, checkbox value attributes
   }
   ```

3. **Create handler functions** in part2.html:
   - `handleGenericFilterChange(dashboardId, value, checked, event)`
   - `selectAllGenericFilter(dashboardId, event)`
   - `clearGenericFilter(dashboardId, event)`
   - `updateGenericFilterDisplay(dashboardId)`

4. **Add CSS** in part1.html for dropdown width if needed

5. **Update each dashboard** to use the generic component instead of custom logic

6. **Implement cross-filter behavior** (see Cross-Filter Pattern below)

### Cross-Filter Pattern for Generic Filter Components
When multiple generic filters are used together, selecting a value in one filter should update the options shown in other filter dropdowns. This ensures users only see relevant options.

**Why cross-filter matters:**
- If user selects "Release 1.0" in Release filter, Customer dropdown should only show customers with items in Release 1.0
- Prevents confusion from seeing options that would return zero results
- Makes filter exploration more intuitive

**Implementation Steps:**

1. **Create dashboard-specific excluding filter helper** in the dashboard's template file:
   ```javascript
   // Example for "MyDashboard" - put in the dashboard's part file
   function getMyDashboardItemsExcludingFilter(excludeFilter) {
       let items = getBaseItems(); // Your base item getter

       // Always apply search filter (never excluded)
       items = applyGenericSearchFilter(items, myDashboardFilters.search);

       // Apply each filter EXCEPT the excluded one
       if (excludeFilter !== 'release' && myDashboardFilters.releases.length > 0) {
           items = items.filter(item => {
               const category = getReleaseCategory(item);
               return myDashboardFilters.releases.includes(category);
           });
       }

       if (excludeFilter !== 'customer' && myDashboardFilters.customers.length > 0) {
           items = items.filter(item => {
               if (myDashboardFilters.customers.includes('(No Customer)') && !item.customer) return true;
               return myDashboardFilters.customers.includes(item.customer);
           });
       }

       if (excludeFilter !== 'priority' && myDashboardFilters.priorities.length > 0) {
           items = items.filter(item => {
               const priority = item.priority ? 'P' + item.priority : '(No Priority)';
               return myDashboardFilters.priorities.includes(priority);
           });
       }

       // Add other filters as needed...

       return items;
   }
   ```

2. **Use excluding helper when populating dropdowns** - DO NOT cache with `dataset.populated`:
   ```javascript
   // In render function - rebuild dropdowns dynamically each time
   const releaseMenu = document.getElementById('myDashboard-release-menu');
   if (releaseMenu) {
       // Get items filtered by everything EXCEPT release
       const releaseFilteredItems = getMyDashboardItemsExcludingFilter('release');
       releaseMenu.innerHTML = buildReleaseFilterDropdown({
           dashboardId: 'myDashboard',
           items: releaseFilteredItems,
           selectedReleases: myDashboardFilters.releases
       });
   }

   const customerMenu = document.getElementById('myDashboard-customer-menu');
   if (customerMenu) {
       // Get items filtered by everything EXCEPT customer
       const customerFilteredItems = getMyDashboardItemsExcludingFilter('customer');
       customerMenu.innerHTML = buildCustomerFilterDropdown({
           dashboardId: 'myDashboard',
           items: customerFilteredItems,
           selectedCustomers: myDashboardFilters.customers
       });
   }

   const priorityMenu = document.getElementById('myDashboard-priority-menu');
   if (priorityMenu) {
       // Get items filtered by everything EXCEPT priority
       const priorityFilteredItems = getMyDashboardItemsExcludingFilter('priority');
       priorityMenu.innerHTML = buildPriorityFilterDropdown({
           dashboardId: 'myDashboard',
           items: priorityFilteredItems,
           selectedPriorities: myDashboardFilters.priorities
       });
   }
   ```

3. **IMPORTANT: Do NOT use `dataset.populated` caching** - dropdowns must rebuild each render:
   ```javascript
   // WRONG - prevents cross-filter updates
   if (!releaseMenu.dataset.populated) {
       releaseMenu.innerHTML = buildReleaseFilterDropdown({...});
       releaseMenu.dataset.populated = 'true';
   }

   // CORRECT - rebuilds dropdown to reflect current filter state
   releaseMenu.innerHTML = buildReleaseFilterDropdown({...});
   ```

**Existing cross-filter implementations:**
- **Releases dashboard:** `getItemsExcludingFilter(items, excludeFilter)` in part4.html
- **Roadmap dashboard:** `getRoadmapFeaturesExcludingFilter(excludeFilter)` in part3.html
- **Customers dashboard:** `getCustomersIssuesExcludingFilter(excludeFilter)` in part3.html

### Generic Search Filter Component (part2.html)
The Search filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 1036-1152)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `applyGenericSearchFilter(items, searchTerm, options)` | Filters items by title/ID match |
| `handleGenericSearchChange(dashboardId)` | Routes input changes to correct dashboard state |
| `clearGenericSearch(dashboardId)` | Clears search input and state |
| `getGenericSearchValue(dashboardId)` | Gets current search value from state |
| `syncGenericSearchFilter(dashboardId)` | Syncs input with state after localStorage load |
| `hasGenericSearchFilter(dashboardId)` | Checks if search is active |

**Usage - Adding Search Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the search input:
<span class="filter-row-label">Search:</span>
<input type="text" id="DASHBOARD-search-input" class="filter-search-input"
       placeholder="Search titles and IDs..." oninput="handleGenericSearchChange('DASHBOARD')">

// 2. In dashboard state, add search property:
let dashboardFilters = {
    search: '',
    // ... other filters
};

// 3. In filter logic, apply generic search filter:
let items = getAllItems();
items = applyGenericSearchFilter(items, dashboardFilters.search);

// 4. In handleGenericSearchChange() (part2.html), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    dashboardFilters.search = searchValue;
    saveStateToStorage();
    renderDashboardView();
}

// 5. In clearAllFilters(), use generic clear:
clearGenericSearch('DASHBOARD');

// 6. In syncFilterState(), use generic sync:
syncGenericSearchFilter('DASHBOARD');

// 7. In hasActiveFilters(), use generic check:
if (hasGenericSearchFilter('DASHBOARD')) return true;
```

**Special Features:**
- **Pipe-separated IDs:** Roadmap supports `123|456|789` syntax for multi-ID filtering
  ```javascript
  items = applyGenericSearchFilter(items, searchTerm, { supportPipeSeparated: true });
  ```
- **Case-insensitive title search:** Title matching is always lowercase
- **Exact ID matching:** ID matching is case-sensitive (numbers)

### Generic Customer Filter Component (part2.html)
The Customer filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 1135-1441)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `computeCustomerInfo(items)` | Analyzes items → customer list, counts, noCustomerCount |
| `buildCustomerFilterDropdown(config)` | Builds dropdown HTML with search, (No Customer), options, actions |
| `filterGenericCustomerOptions(optionsId, searchText)` | Filters options by search text |
| `handleGenericCustomerChange(dashboardId, ...)` | Routes checkbox changes to correct dashboard state |
| `selectAllGenericCustomer(dashboardId, ...)` | Select All handler |
| `clearGenericCustomer(dashboardId, ...)` | Clear handler |
| `updateGenericCustomerDisplay(dashboardId)` | Updates display text |
| `syncGenericCustomerFilter(dashboardId)` | Syncs checkboxes after localStorage load |

**Usage - Adding Customer Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the dropdown structure:
<span class="filter-row-label">Customer:</span>
<div class="filter-dropdown" id="DASHBOARD-customer-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-customer-dropdown')">
        <span id="DASHBOARD-customer-display">All Customers</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-customer-menu">
        <!-- Populated dynamically -->
    </div>
</div>

// 2. In CSS (part1.html), add to wide dropdown list:
#DASHBOARD-customer-menu { right: auto; min-width: 280px; }

// 3. In render function, populate the dropdown:
const customerMenu = document.getElementById('DASHBOARD-customer-menu');
if (customerMenu) {
    customerMenu.innerHTML = buildCustomerFilterDropdown({
        dashboardId: 'DASHBOARD',
        items: workItems,
        selectedCustomers: dashboardFilters.customers
    });
}

// 4. In handleGenericCustomerChange() (part2.html), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    // Update state, call render function
}

// 5. Update display, sync, and clear functions similarly
```

**Features:**
- **"(No Customer)" option** shown first with count of items without customers
- **Item count** displayed next to each customer name
- **Search box** filters options as you type
- **Alphabetical sorting** (case-insensitive)
- **Scroll position preserved** when selecting items

### Generic Priority Filter Component (part2.html)
The Priority filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 1449-1742)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `computePriorityInfo(items)` | Analyzes items → priority list, counts, noPriorityCount |
| `buildPriorityFilterDropdown(config)` | Builds dropdown HTML with search, options (P1-P4), (No Priority), actions |
| `filterGenericPriorityOptions(optionsId, searchText)` | Filters options by search text |
| `handleGenericPriorityChange(dashboardId, ...)` | Routes checkbox changes to correct dashboard state |
| `selectAllGenericPriority(dashboardId, ...)` | Select All handler |
| `clearGenericPriority(dashboardId, ...)` | Clear handler |
| `updateGenericPriorityDisplay(dashboardId)` | Updates display text |
| `syncGenericPriorityFilter(dashboardId)` | Syncs checkboxes after localStorage load |

**Usage - Adding Priority Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the dropdown structure:
<span class="filter-row-label">Priority:</span>
<div class="filter-dropdown" id="DASHBOARD-priority-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-priority-dropdown')">
        <span id="DASHBOARD-priority-display">All Priorities</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-priority-menu">
        <!-- Populated dynamically -->
    </div>
</div>

// 2. In CSS (part1.html), add to wide dropdown list:
#DASHBOARD-priority-menu { right: auto; min-width: 200px; }

// 3. In dashboard state, add priorities property:
let dashboardFilters = {
    priorities: [],
    // ... other filters
};

// 4. In render function, populate the dropdown:
const priorityMenu = document.getElementById('DASHBOARD-priority-menu');
if (priorityMenu) {
    priorityMenu.innerHTML = buildPriorityFilterDropdown({
        dashboardId: 'DASHBOARD',
        items: workItems,
        selectedPriorities: dashboardFilters.priorities
    });
}

// 5. In handleGenericPriorityChange() (part2.html), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    // Update state, call render function
}

// 6. In filter logic, apply priority filter:
if (dashboardFilters.priorities.length > 0) {
    items = items.filter(item => {
        const priority = item.priority ? 'P' + item.priority : '(No Priority)';
        return dashboardFilters.priorities.includes(priority);
    });
}
```

**Features:**
- **Priorities sorted numerically** (P1, P2, P3, P4)
- **"(No Priority)" option** shown last with count
- **Item count** displayed next to each priority
- **Search box** filters options as you type
- **Scroll position preserved** when selecting items

### Generic State Filter Component (part2.html)
The State filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 1758-2049)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `computeStateInfo(items)` | Analyzes items → state list, counts, noStateCount |
| `buildStateFilterDropdown(config)` | Builds dropdown HTML with search, options (semantic order), actions |
| `filterGenericStateOptions(optionsId, searchText)` | Filters options by search text |
| `handleGenericStateChange(dashboardId, ...)` | Routes checkbox changes to correct dashboard state |
| `selectAllGenericState(dashboardId, ...)` | Select All handler |
| `clearGenericState(dashboardId, ...)` | Clear handler |
| `updateGenericStateDisplay(dashboardId)` | Updates display text |
| `syncGenericStateFilter(dashboardId)` | Syncs checkboxes after localStorage load |

**Usage - Adding State Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the dropdown structure:
<span class="filter-row-label">State:</span>
<div class="filter-dropdown" id="DASHBOARD-state-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-state-dropdown')">
        <span id="DASHBOARD-state-display">All States</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-state-menu">
        <!-- Populated dynamically -->
    </div>
</div>

// 2. In CSS (part1.html), add to wide dropdown list:
#DASHBOARD-state-menu { right: auto; min-width: 200px; }

// 3. In dashboard state, add states property:
let dashboardFilters = {
    states: [],
    // ... other filters
};

// 4. In render function, populate the dropdown:
const stateMenu = document.getElementById('DASHBOARD-state-menu');
if (stateMenu) {
    stateMenu.innerHTML = buildStateFilterDropdown({
        dashboardId: 'DASHBOARD',
        items: workItems,
        selectedStates: dashboardFilters.states
    });
}

// 5. In handleGenericStateChange() (part2.html), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    // Update state, call render function
}

// 6. In filter logic, apply state filter:
if (dashboardFilters.states.length > 0) {
    items = items.filter(item => dashboardFilters.states.includes(item.state));
}
```

**Features:**
- **States sorted semantically** using STATE_ORDER constant
- **STATE_ORDER:** `['New', 'Triaged', 'To Do', 'In Progress', 'Ready For Review', 'Done', 'Closed', 'Removed']`
- **"(No State)" option** shown last with count (if items exist without state)
- **Item count** displayed next to each state
- **Search box** filters options as you type
- **Scroll position preserved** when selecting items

### Generic Team Filter Component (part2.html)
The Team filter is shared across **Releases**, **Roadmap**, and **Customers** dashboards.

**Location:** `Templates/dashboard_v3_part2.html` (lines 2054-2376)

**Core Functions:**
| Function | Purpose |
|----------|---------|
| `computeTeamInfo(items, options)` | Analyzes items → team list, counts, noTeamCount |
| `buildTeamFilterDropdown(config)` | Builds dropdown HTML with search, options (alphabetical), actions |
| `filterGenericTeamOptions(optionsId, searchText)` | Filters options by search text |
| `handleGenericTeamChange(dashboardId, ...)` | Routes checkbox changes to correct dashboard state |
| `selectAllGenericTeam(dashboardId, ...)` | Select All handler |
| `clearGenericTeam(dashboardId, ...)` | Clear handler |
| `updateGenericTeamDisplay(dashboardId)` | Updates display text |
| `syncGenericTeamFilter(dashboardId)` | Syncs checkboxes after localStorage load |
| `getLastPathSegment(path)` | Helper to extract team name from area path |

**Usage - Adding Team Filter to a New Dashboard:**
```javascript
// 1. In HTML (part1.html), add the dropdown structure:
<span class="filter-row-label">Team:</span>
<div class="filter-dropdown" id="DASHBOARD-team-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-team-dropdown')">
        <span id="DASHBOARD-team-display">All Teams</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-team-menu">
        <!-- Populated dynamically -->
    </div>
</div>

// 2. In CSS (part1.html), add to wide dropdown list:
#DASHBOARD-team-menu { right: auto; min-width: 200px; }

// 3. In dashboard state, add teams property:
let dashboardFilters = {
    teams: [],
    // ... other filters
};

// 4. In render function, populate the dropdown:
const teamMenu = document.getElementById('DASHBOARD-team-menu');
if (teamMenu) {
    teamMenu.innerHTML = buildTeamFilterDropdown({
        dashboardId: 'DASHBOARD',
        items: workItems,
        selectedTeams: dashboardFilters.teams
    });
}

// 5. In handleGenericTeamChange() (part2.html), add dashboard routing:
} else if (dashboardId === 'DASHBOARD') {
    // Update state, call render function
}

// 6. In filter logic, apply team filter:
if (dashboardFilters.teams.length > 0) {
    items = items.filter(item => {
        const team = item.team || '(No Team)';
        return dashboardFilters.teams.includes(team);
    });
}
```

**Features:**
- **Teams sorted alphabetically** (case-insensitive)
- **"(No Team)" option** shown last with count (if items exist without team)
- **Item count** displayed next to each team
- **Search box** filters options as you type
- **Scroll position preserved** when selecting items

**Special Cases:**
- **Roadmap Dashboard:** Teams come from delivery slices, not directly from features. The populate function extracts teams from `areaPath` of delivery slices.

### Filter Row Order Convention
For consistency, generic filters should follow this order across all dashboards:
1. **Search** (always first)
2. **Release** (second - most common cross-dashboard filter)
3. **Customer** (third)
4. **Priority** (fourth)
5. **State** (fifth)
6. **Team** (sixth)
7. Dashboard-specific filters (Iteration, Tag, Category, etc.)
8. **Clear All button** (before Info)
9. **Info popup** (always last, `margin-left: auto`)

This order ensures users have a consistent experience when switching between dashboards.

## v85 Summary (December 2024)
**Generic Priority Filter Component:**
- Created shared Priority filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- Shows P1, P2, P3, P4 with item counts (sorted numerically)
- Shows "(No Priority)" option last with count of items without priority
- Includes search box at top for filtering options
- Wide dropdown (200px) for better readability

**Priority Functions Added:**
- `computePriorityInfo()` - Analyze items for priority data
- `buildPriorityFilterDropdown()` - Build dropdown HTML with search, options, actions
- `filterGenericPriorityOptions()` - Search filter for options
- `handleGenericPriorityChange()` - Checkbox change handler
- `selectAllGenericPriority()` - Select All handler
- `clearGenericPriority()` - Clear handler
- `updateGenericPriorityDisplay()` - Update display text
- `syncGenericPriorityFilter()` - Sync checkboxes after localStorage load

**Generic State Filter Component:**
- Created shared State filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- States sorted semantically using STATE_ORDER constant
- Shows "(No State)" option last with count (if items exist without state)
- Includes search box at top for filtering options
- Wide dropdown (200px) for better readability
- Full cross-filter support

**State Functions Added:**
- `computeStateInfo()` - Analyze items for state data
- `buildStateFilterDropdown()` - Build dropdown HTML with search, options, actions
- `filterGenericStateOptions()` - Search filter for options
- `handleGenericStateChange()` - Checkbox change handler
- `selectAllGenericState()` - Select All handler
- `clearGenericState()` - Clear handler
- `updateGenericStateDisplay()` - Update display text
- `syncGenericStateFilter()` - Sync checkboxes after localStorage load

**Generic Team Filter Component:**
- Created shared Team filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- Teams sorted alphabetically (case-insensitive)
- Shows "(No Team)" option last with count (if items exist without team)
- Includes search box at top for filtering options
- Wide dropdown (200px) for better readability
- Full cross-filter support

**Team Functions Added:**
- `computeTeamInfo()` - Analyze items for team data
- `buildTeamFilterDropdown()` - Build dropdown HTML with search, options, actions
- `filterGenericTeamOptions()` - Search filter for options
- `handleGenericTeamChange()` - Checkbox change handler
- `selectAllGenericTeam()` - Select All handler
- `clearGenericTeam()` - Clear handler
- `updateGenericTeamDisplay()` - Update display text
- `syncGenericTeamFilter()` - Sync checkboxes after localStorage load
- `getLastPathSegment()` - Helper to extract team from area path

**Cross-Filter Behavior for All Generic Filters:**
- All generic filters (Search, Release, Customer, Priority, State, Team) now have cross-filter behavior
- Selecting a value in one filter updates options shown in other filter dropdowns
- Ensures users only see relevant options based on current selections
- Documented cross-filter pattern in CLAUDE.md for future components

**Cross-Filter Helper Functions Added:**
- `getRoadmapFeaturesExcludingFilter(excludeFilter)` - Roadmap cross-filter helper (part3.html)
- `getCustomersIssuesExcludingFilter(excludeFilter)` - Customers cross-filter helper (part3.html)
- `getItemsExcludingFilter(items, excludeFilter)` - Releases cross-filter helper (part4.html)

**Filter Order Standardized:**
- All three dashboards now use consistent filter order: Search → Release → Customer → Priority → State → Team
- Standard order: Search → Release → Customer → Priority → State → Team → dashboard-specific filters

**Releases Dashboard:**
- Added Priority filter after Customer filter (before Type)
- Refactored State and Team filters to use generic components with item counts
- Cross-filter aware: dropdown options update based on other active filters

**Roadmap Dashboard:**
- Refactored to use generic Priority, State, and Team components
- Updated filter logic to use P1/P2/P3/P4 format (instead of raw numbers)
- Updated sync and clear functions to use generic components
- All generic filter dropdowns now rebuild dynamically (removed `dataset.populated` caching)
- Team filter extracts teams from delivery slices' areaPath

**Customers Dashboard:**
- Refactored to use generic Priority, State, and Team components
- Added Team filter (new) with full cross-filter support
- Updated dropdown population and display functions
- All generic filter dropdowns now rebuild dynamically (removed `dataset.populated` caching)
- Updated `getCustomersIssuesExcludingFilter()` to accept 'state' and 'team' parameters

## v84 Summary (December 2024)
**Generic Search Filter Component:**
- Created shared Search filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- Searches both Title (case-insensitive) and ID (exact match)
- Roadmap supports pipe-separated ID lists (`123|456|789`)

**Generic Customer Filter Component:**
- Created shared Customer filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- Shows "(No Customer)" option first with item count
- Shows item count next to each customer name
- Wide dropdown (280px) with search box
- Alphabetically sorted customers

**Search Functions Added:**
- `applyGenericSearchFilter()` - Core filtering logic
- `handleGenericSearchChange()` - Input handler routing
- `clearGenericSearch()` - Clear search state
- `getGenericSearchValue()` - Get current search value
- `syncGenericSearchFilter()` - Sync input after localStorage load
- `hasGenericSearchFilter()` - Check if search is active

**Customer Functions Added:**
- `computeCustomerInfo()` - Analyze items for customer data
- `buildCustomerFilterDropdown()` - Build dropdown HTML
- `filterGenericCustomerOptions()` - Search filter for options
- `handleGenericCustomerChange()` - Checkbox change handler
- `selectAllGenericCustomer()` - Select All handler
- `clearGenericCustomer()` - Clear handler
- `updateGenericCustomerDisplay()` - Update display text
- `syncGenericCustomerFilter()` - Sync after localStorage load

**Refactored:**
- Releases: Uses generic search and customer components
- Roadmap: Uses generic search and customer components
- Customers: Uses generic search and customer components

## v83 Summary (December 2024)
**Generic Release Filter Component:**
- Created shared Release filter component in part2.html
- Used by Releases, Roadmap, and Customers dashboards
- Shows release version + target date in dropdown (280px wide)
- Includes "⚠️ Needs Release" warning category for items with date but no release
- Moved Release filter to position 2 (after Search) on Roadmap and Customers dashboards

**Functions Added:**
- `computeReleaseInfo()`, `buildReleaseFilterDropdown()`
- `handleGenericReleaseChange()`, `selectAllGenericRelease()`, `clearGenericRelease()`
- `updateGenericReleaseDisplay()`, `syncGenericReleaseFilter()`

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
- Local output: `/Users/tonythem/GitHub/athemelis/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html`
- Published output: SharePoint `Product Planning/eSHARE-DevOps-Dashboard.html`
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
