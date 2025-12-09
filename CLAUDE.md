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

## Current Version: v71

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
