# Generic Filter Components

All generic filter components are located in `Templates/dashboard_v3_part2.html`. These are shared across Releases, Roadmap, and Customers dashboards.

## Philosophy
When a filter type appears on multiple dashboards, use a **generic component**:
- Visual consistency (same dropdown width, styling)
- Behavioral consistency (same Select All/Clear logic)
- Single point of maintenance

## Available Components

| Component | Width | Key Features |
|-----------|-------|--------------|
| Release | 280px | Includes "⚠️ Needs Release" category |
| Search | flex | Title + ID matching, pipe-separated IDs for Roadmap |
| Customer | 280px | "(No Customer)" first, item counts |
| Priority | 200px | P1-P4 sorted numerically, "(No Priority)" last |
| State | 200px | Semantic order (STATE_ORDER constant) |
| Team | 200px | Alphabetical, "(No Team)" last |

## Function Naming Convention

Each generic filter provides these functions (replace `*` with filter name):
- `compute*Info(items)` - Analyze items, return counts and options
- `build*FilterDropdown(config)` - Build dropdown HTML
- `handle*Change(dashboardId, value, checked, event)` - Checkbox handler
- `selectAll*(dashboardId, event)` - Select All action
- `clear*(dashboardId, event)` - Clear action
- `update*Display(dashboardId)` - Update display text
- `sync*Filter(dashboardId)` - Sync checkboxes after localStorage load

---

## Adding a Generic Filter to a New Dashboard

### 1. HTML Structure (part1.html)
```html
<span class="filter-row-label">FilterName:</span>
<div class="filter-dropdown" id="DASHBOARD-filter-dropdown">
    <div class="filter-dropdown-toggle" onclick="toggleFilterDropdown('DASHBOARD-filter-dropdown')">
        <span id="DASHBOARD-filter-display">All Items</span>
        <span class="arrow">▼</span>
    </div>
    <div class="filter-dropdown-menu" id="DASHBOARD-filter-menu">
        <!-- Populated dynamically -->
    </div>
</div>
```

### 2. CSS (part1.html)
```css
#DASHBOARD-filter-menu { right: auto; min-width: 200px; }
```

### 3. Dashboard State
```javascript
let dashboardFilters = {
    filters: [],
    // ... other filters
};
```

### 4. Render Function
```javascript
const filterMenu = document.getElementById('DASHBOARD-filter-menu');
if (filterMenu) {
    filterMenu.innerHTML = buildFilterDropdown({
        dashboardId: 'DASHBOARD',
        items: workItems,
        selectedValues: dashboardFilters.filters
    });
}
```

### 5. Handler Routing (part2.html)
Add to `handleGenericFilterChange()`:
```javascript
} else if (dashboardId === 'DASHBOARD') {
    // Update state
    if (checked) {
        dashboardFilters.filters.push(value);
    } else {
        dashboardFilters.filters = dashboardFilters.filters.filter(v => v !== value);
    }
    saveStateToStorage();
    renderDashboardView();
}
```

### 6. Filter Logic
```javascript
if (dashboardFilters.filters.length > 0) {
    items = items.filter(item => dashboardFilters.filters.includes(item.filterField));
}
```

---

## Filter Row Order Convention

For consistency across all dashboards:
1. **Search** (always first)
2. **Release**
3. **Customer**
4. **Priority**
5. **State**
6. **Team**
7. Dashboard-specific filters (Iteration, Tag, Category, etc.)
8. **Clear All button**
9. **Info popup** (always last, `margin-left: auto`)

---

## Cross-Filter Pattern

When multiple filters are used together, selecting a value in one should update options shown in others.

### Why Cross-Filter Matters
- User selects "Release 1.0" → Customer dropdown shows only customers with items in Release 1.0
- Prevents confusion from seeing options that would return zero results

### Implementation

Create a dashboard-specific excluding filter helper:
```javascript
function getDashboardItemsExcludingFilter(excludeFilter) {
    let items = getBaseItems();

    // Always apply search (never excluded)
    items = applyGenericSearchFilter(items, filters.search);

    // Apply each filter EXCEPT the excluded one
    if (excludeFilter !== 'release' && filters.releases.length > 0) {
        items = items.filter(item => {
            const category = getReleaseCategory(item);
            return filters.releases.includes(category);
        });
    }

    if (excludeFilter !== 'customer' && filters.customers.length > 0) {
        items = items.filter(item => {
            if (filters.customers.includes('(No Customer)') && !item.customer) return true;
            return filters.customers.includes(item.customer);
        });
    }

    // ... other filters ...
    return items;
}
```

### Using in Render
```javascript
// Get items filtered by everything EXCEPT release
const releaseFilteredItems = getDashboardItemsExcludingFilter('release');
releaseMenu.innerHTML = buildReleaseFilterDropdown({
    dashboardId: 'dashboard',
    items: releaseFilteredItems,
    selectedReleases: filters.releases
});
```

**IMPORTANT:** Do NOT cache with `dataset.populated` - dropdowns must rebuild each render for cross-filter to work.

---

## Existing Cross-Filter Implementations

| Dashboard | Helper Function | Location |
|-----------|-----------------|----------|
| Releases | `getItemsExcludingFilter(items, excludeFilter)` | part4.html |
| Roadmap | `getRoadmapFeaturesExcludingFilter(excludeFilter)` | part3.html |
| Customers | `getCustomersIssuesExcludingFilter(excludeFilter)` | part3.html |

---

## Special Notes by Filter Type

### Release Filter
- **Categories:** Regular releases (sorted by target date), "⚠️ Needs Release" (has date, no release), "(No Release)" (neither)
- **Category logic:**
```javascript
const getItemReleaseCategory = (item) => {
    if (item.releaseVersion?.trim()) return item.releaseVersion.trim();
    return item.targetDate ? '(Needs Release)' : '(No Release)';
};
```

### Search Filter
- **Roadmap special:** Supports pipe-separated IDs (`123|456|789`)
```javascript
items = applyGenericSearchFilter(items, searchTerm, { supportPipeSeparated: true });
```

### State Filter
- **STATE_ORDER constant:** `['New', 'Triaged', 'To Do', 'In Progress', 'Ready For Review', 'Done', 'Closed', 'Removed']`

### Team Filter (Roadmap)
- Teams come from delivery slices' `areaPath`, not directly from features
- Use `getLastPathSegment(ds.areaPath)` to extract team name
