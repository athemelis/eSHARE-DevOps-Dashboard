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

## Current Version: v70

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
