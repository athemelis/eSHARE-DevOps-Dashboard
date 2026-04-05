# eShare DevOps Dashboard - Claude Code Context

## Project Overview
Reporting dashboard visualizing Azure DevOps work items (Features, Delivery Slices, Bugs, Issues, Tasks). Runs as a single HTML file served from SharePoint.

## Related Documentation (read on-demand)
- **[CLAUDE-patterns.md](./CLAUDE-patterns.md)** - UI patterns, implementation patterns
- **[CLAUDE-filters.md](./CLAUDE-filters.md)** - Generic filter components
- **[CLAUDE-changelog.md](./CLAUDE-changelog.md)** - Version history (v70-v85+)
- **[DASHBOARD_README.md](./DASHBOARD_README.md)** - User documentation and data schema

## Architecture
- **Templates/**: Development HTML template parts (local testing)
- **Templates-Production/**: Production HTML template parts (scheduled publishing)
- **generate_dashboard.py**: Combines templates + CSV data → final HTML

## Key Files
| File | Purpose |
|------|---------|
| `Templates/dashboard_v3_part1.html` | HTML structure + CSS |
| `Templates/dashboard_v3_part2.html` | Core JavaScript + generic filter components |
| `Templates/dashboard_v3_part3.html` | Releases, Customers, Bugs views |
| `Templates/dashboard_v3_part4.html` | Teams, Org Chart, Validation views |
| `generate_dashboard.py` | Generation script |

## Development vs Production Workflow

**Two template directories:**
- `Templates/` - Development (local testing)
- `Templates-Production/` - Production (60-second launchd job)

**Development:**
1. Edit `Templates/` files
2. Run `python3 generate_dashboard.py` (generates to local DEV file)
3. Open `eSHARE-DevOps-Dashboard.html` in browser
4. Repeat until ready

**Publishing:**
1. Copy templates: `cp Templates/*.html Templates-Production/`
2. Update version in `Templates-Production/dashboard_v3_part1.html`
3. Run `python3 generate_dashboard.py --publish`

**Key paths:**
- DEV: `/Users/tonythem/GitHub/athemelis/eSHARE-DevOps-Dashboard/eSHARE-DevOps-Dashboard.html`
- PROD: SharePoint `Product Planning/eSHARE-DevOps-Dashboard.html`

## Version Management
When making changes:
1. Increment `CURRENT_VERSION` in `generate_dashboard.py`
2. Update version in `Templates/dashboard_v3_part1.html`: `<span class="version">vXX</span>`
3. Add entry to `DASHBOARD_README.md` Version History

## Current Version: v100

## Git Commit Requirements
**IMPORTANT:** When committing:
1. Include ALL modified files (`git add .`)
2. Include generated `eSHARE-DevOps-Dashboard.html`
3. Always push to GitHub after committing
4. Verify push was successful

```bash
git add .
git commit -m "vXX: [summary]"
git push
```

## Commands
```bash
# Generate locally (DEV)
python3 generate_dashboard.py

# Generate and publish (PROD)
python3 generate_dashboard.py --publish

# Custom CSV
python3 generate_dashboard.py -c "../ALL_Items.csv"

# Open in browser
open "eSHARE-DevOps-Dashboard.html"

# Reload launchd agent
./reload-launchd-agent.sh
```

## Testing Changes
1. Run the generator
2. Check browser console (F12) for JavaScript errors
3. Verify file size is ~5MB (not ~350KB = missing data)
