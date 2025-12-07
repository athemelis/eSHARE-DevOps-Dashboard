# eShare DevOps Dashboard

## Current Version: v69

---

## Quick Start (Local Execution)

### Prerequisites
- Python 3.9+ installed
- pandas library (`pip3 install pandas`)

### Folder Structure
After extracting the package, your folder should look like:
```
Your SharePoint Folder/
├── Templates/
│   ├── dashboard_v3_part1.html
│   ├── dashboard_v3_part2.html
│   ├── dashboard_v3_part3.html
│   ├── dashboard_v3_part4.html
│   └── dashboard_v3_template.html
├── generate_dashboard.py
├── DASHBOARD_README.md
├── ALL_Items.csv              ← Your data (managed by Power Automate)
├── Org_Chart.csv              ← Your org chart data
└── ᵉShare DevOps Dashboard.html  ← Generated output
```

### Running the Script

**Simple run** (all files in current directory):
```bash
cd "/path/to/your/folder"
python3 generate_dashboard.py
```

**With custom CSV location:**
```bash
python3 generate_dashboard.py -c "../ALL Items.csv"
```

**Full run with all paths specified:**
```bash
python3 generate_dashboard.py \
    -c "/path/to/ALL Items.csv" \
    -g "/path/to/Org_Chart.csv" \
    -t "./Templates" \
    -o "./ᵉShare DevOps Dashboard.html"
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --csv` | Path to ALL_Items.csv | `./ALL_Items.csv` |
| `-g, --org` | Path to Org_Chart.csv | `./Org_Chart.csv` |
| `-t, --templates` | Folder containing template files | `./Templates` |
| `-o, --output` | Output HTML file path | `./ᵉShare DevOps Dashboard.html` |
| `-h, --help` | Show help message | |

### Refresh Timestamp
The refresh timestamp in the dashboard header is **automatically read from the CSV file's last modified date**. No manual editing required!

---

## Version vs. Refresh Timestamp

| Indicator | Meaning | When to Update |
|-----------|---------|----------------|
| **Version** (e.g., v64) | Code/template changes | Only when JavaScript, CSS, or HTML structure changes |
| **Refresh** timestamp | Data freshness | Automatic - reads from CSV file's modified date |

---

## Workflows

### Data Refresh (Automated via Power Automate)
1. Power Automate updates `ALL_Items.csv` every minute
2. Run `python3 generate_dashboard.py`
3. Dashboard HTML is regenerated with fresh data and timestamp
4. SharePoint versions the HTML file automatically

### Code Changes (Via Claude)
1. Work with Claude to make template/script changes
2. Download new `eShare_DevOps_Dashboard.zip` from Claude
3. Extract to your SharePoint folder (overwrites `Templates/` and `generate_dashboard.py`)
4. Run `python3 generate_dashboard.py` to regenerate with your current data
5. SharePoint versions all files automatically

---

## Continuing Development with Claude

### Standard Prompt (code changes, questions):
```
I'm continuing development on the eShare DevOps Dashboard.

**Uploaded Files:**
1. eShare_DevOps_Dashboard.zip (current version)

Please:
1. Extract the package to /mnt/user-data/outputs/
2. Check /mnt/transcripts/journal.txt for recent session history
3. [Your request here]
```

### Debugging Prompt (when data validation needed):
```
I'm continuing development on the eShare DevOps Dashboard.

**Uploaded Files:**
1. eShare_DevOps_Dashboard.zip (current version)
2. ALL_Items.csv (for debugging)
3. Org_Chart.csv (if relevant)

Please:
1. Extract the package to /mnt/user-data/outputs/
2. Copy CSV files to /mnt/user-data/outputs/
3. Check /mnt/transcripts/journal.txt for recent session history
4. [Your request here - e.g., "Work item 631 shows wrong date, please investigate"]
```

---

## Package Contents

The zip package contains **code files only** (no data):

```
eShare_DevOps_Dashboard.zip
├── Templates/
│   ├── dashboard_v3_part1.html    # HTML + CSS + header
│   ├── dashboard_v3_part2.html    # Core JS + data placeholder
│   ├── dashboard_v3_part3.html    # Releases, Customers, Bugs views
│   ├── dashboard_v3_part4.html    # Teams, Org Chart, Validation views
│   └── dashboard_v3_template.html # Concatenated template
├── generate_dashboard.py          # Generation script
└── DASHBOARD_README.md            # This file
```

**NOT included in package:**
- `ALL_Items.csv` - Managed by Power Automate
- `Org_Chart.csv` - Managed separately  
- `ᵉShare DevOps Dashboard.html` - Regenerated locally

---

## Data Schema Reference (CRITICAL)

The dashboard JavaScript expects these exact field names. **Do not change these:**

```javascript
{
  id: number,              // Work item ID
  type: string,            // "Feature", "Bug", "Task", etc.
  title: string,
  state: string,
  assignedTo: string|null,
  areaPath: string,
  team: string,            // Extracted from areaPath
  iterationPath: string,
  iteration: string,       // Extracted from iterationPath
  createdDate: string,     // ISO datetime: "2025-08-01T18:50:47"
  stateChangeDate: string, // ISO datetime
  closedDate: string|null, // ISO datetime
  targetDate: string|null, // DATE-ONLY: "2025-12-31" (no time component!)
  priority: number|null,
  severity: string|null,
  tags: string|null,
  parentId: number|null,
  effort: number|null,
  effortRollup: number,
  backlogPriority: number|null,
  customers: string|null,
  teamsAffected: string|null,
  releaseVersion: string|null,
  bugType: string|null,
  component: string|null,
  feature: string|null,
  ticketCategory: string|null,
  deliverySliceOwner: string|null,
  url: string
}
```

### CSV Column Formats Supported

The script auto-detects and supports both formats:

| Format | Example Column | Source |
|--------|---------------|--------|
| **ADO Field Names** | `System.WorkItemType` | Power Automate exports |
| **Friendly Names** | `Work Item Type` | Analytics View exports |

### Date Handling

| Field | Format | Notes |
|-------|--------|-------|
| `targetDate` | Date only (`2025-12-31`) | Converted from UTC to Athens timezone |
| `createdDate`, `stateChangeDate`, `closedDate` | ISO datetime | `2025-09-11T22:18:10` |

---

## Validation Checks

The generation script includes:

1. **Column format detection** - Auto-detects ADO field names vs friendly names
2. **Placeholder validation** - Fails if placeholders remain in output
3. **Schema validation** - Warns if expected fields are missing
4. **Size check** - Warns if output < 3MB (expected ~5MB with data)

---

## Troubleshooting

### "Data isn't populating" / Charts show zeros

1. Open browser console (F12)
2. Look for JavaScript errors
3. Check that generation script reports "Validation passed"
4. Verify file size is ~5MB (not ~350KB)

### Script can't find files

Check your paths:
```bash
# See what's in current directory
ls -la

# See what's in Templates folder
ls -la Templates/

# Run with explicit paths
python3 generate_dashboard.py -c "./ALL_Items.csv" -t "./Templates"
```

### Missing pandas

```bash
pip3 install pandas
```

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v69 | 12/6/2025 | Bug fixes: Added null checks to updateSelectionInfo, renderDrilldown, and closeDrilldown functions to prevent errors when drilldown panel element doesn't exist (removed in v68). |
| v68 | 12/6/2025 | Releases view: (1) Stat cards now update dynamically based on active filters. (2) Removed stat card drilldown feature. (3) Added Customer filter to header. (4) Filters update view immediately while dropdown stays open. (5) Cross-filter aware dropdowns show only options available in current filtered context. |
| v67 | 12/6/2025 | Releases view: Replaced doughnut charts with header filters (Type, Bug Type, State, Team). Full bar chart when no filters, mini-bar when any filter active. Added "Clear All" button. Chart header pattern: title + subtitle on same line. Fixed dropdown behavior for Select All/Clear. |
| v66 | 12/6/2025 | Releases view: Implemented sticky two-row header with view navigation and filter row. Moved "How is release progress calculated?" to expandable info panel in header. |
| v65 | 12/6/2025 | Restructured package: Templates in subfolder, code-only zip (no CSVs/HTML), removed -p package option from script, auto-refresh timestamp from CSV modified date, simplified command-line args. |
| v64 | 12/5/2025 | Support for ADO field names (System.*, Microsoft.VSTS.*, Custom.*) from Power Automate exports. Legacy friendly names still supported. Target dates now converted from UTC to Athens timezone to match ADO display. Local execution with command-line arguments. |
| v63 | 12/5/2025 | Org chart data now dynamically loaded from Org_Chart.csv instead of hardcoded. |
| v62 | 12/4/2025 | Bug fix: State filter in Engineer Workload section now dynamically populated from actual work item states. |
| v61 | 12/3/2025 | Team Details: Added Work Item Type filter to Engineer Workload section. |
| v60 | 12/3/2025 | Team Details: Added team member coverage indicator. |
| v59 | 12/3/2025 | Team Details: Added State and Priority multi-select filters to Engineer Workload section. |
| v58 | 12/3/2025 | Added "All Teams" card showing aggregated totals across all teams. |
| v57 | 12/3/2025 | Teams view filtering: Time period filter now applies to all 8 visuals. Added "Last Week" time period. |
| v56 | 12/3/2025 | Teams view layout: Moved CTA and team cards below Work Item Distribution section. |
| v55 | 12/3/2025 | Engineer Workload: Replaced bar chart with matrix table (engineers × work item types). |
| v54 | 12/3/2025 | Engineer Workload: Dynamic chart height, added "Unassigned (?)" filter option. |
| v53 | 12/3/2025 | Engineer Workload: Fixed bar chart to show engineer's home team from Org Chart. |
| v52 | 12/2/2025 | Teams view redesign with Team Insights section. |
| v51 | 12/2/2025 | Multi-select chart filters across all views. |
| v50 | 12/2/2025 | Releases: Added Customers card. Bugs: Multi-select filters. |
| v48 | 12/1/2025 | Fixed targetDate to date-only format. |
| v47 | 12/1/2025 | Fixed schema (restored v45 compatibility), added validation. |

---

## Updating the Version (Code Changes)

When making code changes in Claude:

1. Increment `CURRENT_VERSION` in `generate_dashboard.py`
2. Update version in `Templates/dashboard_v3_part1.html`:
   ```html
   <span class="version">v65</span>
   ```
3. Update this README's version history
4. Download new zip package from Claude
5. Extract to your SharePoint folder
6. Run `python3 generate_dashboard.py` to regenerate
