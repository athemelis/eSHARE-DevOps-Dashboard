# UI & Implementation Patterns

Reusable patterns for the eShare DevOps Dashboard.

## UI Patterns

### Label-Based Checkbox Filters
Use `<label class="filter-dropdown-option">` so clicking anywhere on the row toggles the checkbox. Use `onchange` handlers (not `onclick`).

### Multi-Select Tag Filters with AND Logic
```javascript
return roadmapFilters.tags.every(selectedTag => featureTags.includes(selectedTag));
```

### Search Filter Integration
1. Add input with `class="filter-search-input"`
2. Create search state variable
3. Add to `getHeaderFilteredItems()` - always apply (no exclusion)
4. Add to `hasActiveFilters()` check
5. Clear in `clearAllFilters()`

### Chart Highlighting for Search Results
```javascript
const barColors = releases.map(r => {
    if (searchFilter && releaseInfo[r].matchingItems > 0) {
        return 'rgba(34, 211, 238, 1)'; // Bright cyan for matches
    }
    return searchFilter ? 'rgba(100, 116, 139, 0.4)' : colors.primary[0];
});
```

### Preserving Scroll Position on Re-render
```javascript
const scrollTop = optionsContainer ? optionsContainer.scrollTop : 0;
// ... re-render ...
if (newOptionsContainer) newOptionsContainer.scrollTop = scrollTop;
```

### Info Popup Standardization
`<span class="info-toggle">ℹ️ Info</span>`

### Flexible Filter Row Layout
- `.filter-dropdown { flex: 1; min-width: 100px; max-width: 200px; }`
- `.filter-search-input { flex: 1; min-width: 120px; max-width: 200px; }`
- Labels and buttons: `flex-shrink: 0`

---

## Implementation Patterns

### Dual-Mode Filter (Inclusion/Exclusion)

**Problem:** "Select Blocked" = show items WITH tag, but "Select All → uncheck Blocked" = show items WITHOUT tag.

**Solution:**
1. Add `[filterType]ExclusionMode` flag
2. "Select All" → `exclusionMode = true`
3. "Clear" → `exclusionMode = false`

```javascript
if (filters.tagsExclusionMode) {
    const uncheckedTags = [...allTags].filter(t => !filters.tags.includes(t));
    items = items.filter(i => !itemTags.some(tag => uncheckedTags.includes(tag)));
} else {
    items = items.filter(i => itemTags.some(tag => filters.tags.includes(tag)));
}
```

---

### State Persistence (localStorage)

```javascript
const STORAGE_KEY = 'eshare-devops-dashboard-state';

function saveStateToStorage() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
        currentView,
        filters,
        timestamp: Date.now()
    }));
}

// After loading: sync UI THEN re-render
syncFilterDropdowns();
stateWasLoaded = false;
renderView(); // IMPORTANT: must re-render with restored filters
```

---

### Collapsible Section

```html
<div class="roadmap-section collapsible collapsed" id="section-id">
    <div class="roadmap-section-header" onclick="toggleSection()">
        <span class="section-number">2</span>
        <span>Title</span>
        <span class="collapse-indicator">▼</span>
    </div>
    <div class="section-content"><!-- Content --></div>
</div>
```

```css
.collapsible .collapse-indicator { transition: transform 0.2s; }
.collapsible.collapsed .collapse-indicator { transform: rotate(-90deg); }
.collapsible .section-content { max-height: 2000px; transition: max-height 0.3s; }
.collapsible.collapsed .section-content { max-height: 0; opacity: 0; }
```

---

### Combined Slice Filters (Team + Iteration)

Feature must have a slice matching BOTH filters:
```javascript
if (filters.teams.length > 0 || filters.iterations.length > 0) {
    features = features.filter(f => {
        const slices = getDeliverySlicesForFeatures([f.id]);
        return slices.some(ds => {
            const team = getLastPathSegment(ds.areaPath) || '(No Team)';
            const iteration = getLastPathSegment(ds.iterationPath) || '(No Iteration)';
            return (filters.teams.length === 0 || filters.teams.includes(team)) &&
                   (filters.iterations.length === 0 || filters.iterations.includes(iteration));
        });
    });
}
```

---

### Default Filter State

When a filter has a default value that should be preserved:
1. Initialize state with default: `tags: ['Candidate']`
2. Set initial display text in HTML to match
3. In `clearAllFilters()`, reset to default (not empty)
4. In `isFiltered` check, treat default state as "not filtered"

---

### Checkbox Value Attribute

Always include `value` attribute for programmatic syncing:
```javascript
// Wrong - cb.value returns empty string
<input type="checkbox" onchange="handleChange('${tag}', this.checked)">

// Correct - cb.value returns the tag for syncing
<input type="checkbox" value="${tag}" onchange="handleChange('${tag}', this.checked)">
```

---

### Dual Value Display (Primary % + Secondary Days)

```javascript
const pct = totalEffort > 0 ? (effort / totalEffort * 100) : 0;
return `<td class="effort-value">
    <span class="effort-pct">${pct.toFixed(0)}%</span>
    <span class="effort-days">${effort.toFixed(1)}d</span>
</td>`;
```

```css
.effort-pct { font-weight: 700; font-size: 1.25rem; }
.effort-days { font-size: 0.8rem; color: var(--text-muted); margin-left: 0.4rem; }
```
