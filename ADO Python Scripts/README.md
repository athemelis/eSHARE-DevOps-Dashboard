# Azure DevOps Python Scripts - Field Migration Tools

This directory contains Python scripts created for one-time data migrations in the eShare Azure DevOps project.

## Project Context

**Organization:** ncryptedcloud  
**Project:** eShare  
**Process Template:** ᵉShareScrum  
**Date:** February 3-4, 2026

## Migration Overview

Three-phase data migration to improve field management and user experience:

### Phase 1: UTC to Athens Timezone Conversion
**Problem:** The system field `Microsoft.VSTS.Scheduling.TargetDate` stores dates in UTC, causing confusion for the Athens-based team.  
**Solution:** Created `Custom.Target_Date` field to store dates in Athens timezone (YYYY-MM-DD format).

- **Script:** `convert_all_target_dates_production.py`
- **Work Items Affected:** 368 Features and Bugs
- **Result:** All target dates now display correctly in Athens timezone

### Phase 2: Target Date Field Migration
**Problem:** Need to migrate from single-line text field to picklist for better data validation.  
**Solution:** Migrated `Custom.Target_Date` (text) → `Custom.CascadingDate` (picklist).

- **Script:** `copy_target_date_to_cascading.py`
- **Work Items Affected:** 351 work items
- **Picklist Values:** 84 unique dates (2025-08-02 through 2026-12-26)

### Phase 3: Release Version Field Migration
**Problem:** Release versions stored as free text, inconsistent formatting.  
**Solution:** Migrated `Custom.ReleaseVersion` (text) → `Custom.CascadingVersion` (picklist).

- **Script:** `copy_release_version_to_cascading.py`
- **Work Items Affected:** 590 work items
- **Picklist Values:** 90 release versions (202508.0.0 through 202612.3.0, plus 202601.3.0)

### Phase 4: Bug Estimation to Task Migration
**Problem:** Bug effort estimates are stored in 8 team-specific fields at the Bug level, inconsistent with Features which track estimates in child Delivery Slices.  
**Solution:** Migrate Bug estimation fields to child Task `originalEstimate` field, creating consistency across work item types.

- **Script:** `migrate_bug_estimates_to_tasks.py`
- **Work Items Affected:** 204 Bugs with estimation data
- **Tasks Updated:** 282
- **Tasks Created:** 54 new Tasks (for teams with estimates but no existing Task)
- **Tasks Skipped:** 23 (already had `originalEstimate` populated)
- **Status:** ✅ Complete (February 4, 2026)
- **Log File:** `migration_log_20260204_101730.txt`

### Phase 5: Issue Cascading Fields Migration
**Problem:** Issues use legacy fields (`Custom.ReleaseVersion`, `Microsoft.VSTS.Scheduling.TargetDate`) while Features and Bugs have been migrated to cascading picklist fields.  
**Solution:** Migrate Issue fields to `Custom.CascadingVersion` and `Custom.CascadingDate` for consistency.

#### Phase 5a: ReleaseVersion → CascadingVersion
- **Script:** `migrate_issue_release_version.py`
- **Work Items Affected:** 6 Issues (with ReleaseVersion but no CascadingVersion)
- **Status:** ✅ Complete (February 5, 2026)

#### Phase 5b: TargetDate → CascadingDate
- **Script:** `migrate_issue_target_date.py`
- **Work Items Affected:** 75 Issues (with TargetDate but no CascadingDate)
- **Successfully Updated:** 70 (automated)
- **Fixed Manually:** 5 (missing picklist values: 2025-09-23, 2025-10-03, 2025-11-25, 2026-03-01)
- **Note:** Converts UTC datetime to Athens timezone date (YYYY-MM-DD format)
- **Status:** ✅ Complete (February 5, 2026)

#### Background

| Work Item Type | Estimation Approach |
|----------------|---------------------|
| **Feature** | Estimates entered in child Delivery Slices |
| **Bug (old)** | Estimates entered in 8 team-specific fields on the Bug itself |
| **Bug (new)** | Estimates entered in child Tasks via `originalEstimate` field |

#### Team Estimation Fields Being Deprecated

| Field Name | Team | Area Path |
|------------|------|-----------|
| `analyticsEstimation` | Analytics | eShare\Analytics |
| `backendEstimation` | Backend | eShare\Backend |
| `frontendEstimation` | Frontend | eShare\Frontend |
| `governEstimation` | Govern | eShare\Govern |
| `scgEstimation` | SCG | eShare\Security and Compliance |
| `devopsEstimation` | DevOps | eShare\DevOps |
| `qaEstimation` | QA | eShare\QA |
| `staffEstimation` | Staff | eShare\Staff |

#### Migration Rules

1. **Split evenly:** If multiple Tasks exist for the same team (matching Area Path), the estimate is split evenly across them.
2. **Skip existing:** Tasks that already have `originalEstimate` populated are skipped (no overwrite).
3. **Create missing:** If a Bug has an estimate for a team but no child Task with matching Area Path, a new Task is created.
4. **Task Type:** Created Tasks use `Code` for all teams except QA which uses `Test`.
5. **Iteration Path:** Created Tasks inherit the Bug's Iteration Path.
6. **Task Title:** Created Tasks use format `[Team] Bug title...` (truncated to 80 chars).

#### Analysis Summary (Pre-Migration)

| Metric | Count |
|--------|-------|
| Total Bugs | 530 |
| Bugs with any estimation field | 204 (38.5%) |
| Tasks with existing `originalEstimate` | 334 of 2,682 (12.5%) |

| Estimation Field | Bugs with Estimate | Has Matching Task | Missing Task |
|------------------|-------------------|-------------------|--------------|
| analyticsEstimation | 0 | 0 | 0 |
| backendEstimation | 57 | 55 | 2 |
| frontendEstimation | 49 | 47 | 2 |
| governEstimation | 4 | 2 | 2 |
| scgEstimation | 1 | 1 | 0 |
| devopsEstimation | 0 | 0 | 0 |
| qaEstimation | 143 | 100 | 43 |
| staffEstimation | 63 | 57 | 6 |

## Scripts Included

### Production Scripts

#### 1. `convert_all_target_dates_production.py`
Converts UTC datetime values to Athens timezone dates.

**What it does:**
- Queries all Features and Bugs with `Microsoft.VSTS.Scheduling.TargetDate` populated
- Converts UTC datetime to Athens timezone (handles DST automatically)
- Stores result in `Custom.Target_Date` as YYYY-MM-DD string
- Processes in batches of 200 work items

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"
python3 convert_all_target_dates_production.py
```

**Requirements:**
- azure-devops
- pytz

**Example Conversion:**
- UTC: 2026-02-06T22:00:00Z
- Athens: 2026-02-07 (advanced +1 day due to timezone)

#### 2. `copy_target_date_to_cascading.py`
Copies target date values from text field to picklist field.

**What it does:**
- Queries all work items with `Custom.Target_Date` populated
- Copies exact string values to `Custom.CascadingDate`
- Skips items already correctly set
- Processes in batches of 200

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"
python3 copy_target_date_to_cascading.py
```

**Note:** Target picklist field must either:
- Have validation disabled (allow any value), OR
- Have all date values pre-populated in picklist

#### 3. `copy_release_version_to_cascading.py`
Copies release version values from text field to picklist field.

**What it does:**
- Queries all work items with `Custom.ReleaseVersion` populated
- Copies exact string values to `Custom.CascadingVersion`
- Skips items already correctly set
- Processes in batches of 200

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"
python3 copy_release_version_to_cascading.py
```

#### 4. `migrate_bug_estimates_to_tasks.py`
Migrates Bug estimation fields to child Task `originalEstimate` fields.

**What it does:**
- Reads local data files (`ALL Items.json`, `WorkItemLinks.json`) to identify Bugs with estimations
- For each Bug, finds child Tasks matching team Area Paths
- Updates existing Tasks with `originalEstimate` (split evenly if multiple Tasks per team)
- Creates new Tasks for teams that have estimates but no existing Task
- Skips Tasks that already have `originalEstimate` populated

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"

# Dry run (read-only, shows what would happen)
python3 migrate_bug_estimates_to_tasks.py --dry-run

# Test on specific Bug
python3 migrate_bug_estimates_to_tasks.py --bug-id 2284

# Test on first N Bugs
python3 migrate_bug_estimates_to_tasks.py --limit 10

# Full migration
python3 migrate_bug_estimates_to_tasks.py
```

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would happen without making changes |
| `--limit N` | Process only first N Bugs |
| `--bug-id ID` | Process only a specific Bug ID |

**Task Creation Details:**
| Field | Value |
|-------|-------|
| Title | `[Team] Bug title...` (truncated to 80 chars) |
| Work Item Type | Task |
| Area Path | Team's Area Path (e.g., `eShare\Frontend`) |
| Iteration Path | Inherited from parent Bug |
| Task Type | `Test` for QA, `Code` for all others |
| Original Estimate | Team's estimation value from Bug |
| Parent Link | Linked to parent Bug |

#### 5. `migrate_issue_release_version.py`
Migrates Issue ReleaseVersion to CascadingVersion.

**What it does:**
- Queries Issues with `Custom.ReleaseVersion` populated but `Custom.CascadingVersion` empty
- Copies exact string values to the cascading field
- Supports dry-run, single-issue, and limit modes

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"

# Dry run (show what would be updated)
python3 migrate_issue_release_version.py --dry-run

# Test on specific Issue
python3 migrate_issue_release_version.py --issue-id 3347

# Test on first N Issues
python3 migrate_issue_release_version.py --limit 10

# Full migration
python3 migrate_issue_release_version.py
```

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would happen without making changes |
| `--limit N` | Process only first N Issues |
| `--issue-id ID` | Process only a specific Issue ID |

#### 6. `migrate_issue_target_date.py`
Migrates Issue TargetDate to CascadingDate with timezone conversion.

**What it does:**
- Queries Issues with `Microsoft.VSTS.Scheduling.TargetDate` populated but `Custom.CascadingDate` empty
- Converts UTC datetime to Athens timezone date (YYYY-MM-DD format)
- Supports dry-run, single-issue, and limit modes

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"

# Dry run (show what would be updated)
python3 migrate_issue_target_date.py --dry-run

# Test on specific Issue
python3 migrate_issue_target_date.py --issue-id 544

# Test on first N Issues
python3 migrate_issue_target_date.py --limit 10

# Full migration
python3 migrate_issue_target_date.py
```

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would happen without making changes |
| `--limit N` | Process only first N Issues |
| `--issue-id ID` | Process only a specific Issue ID |

**Note:** If the CascadingDate picklist doesn't have all required date values, you may need to add them manually in the ADO UI or temporarily disable picklist validation.

### Utility Scripts

#### 7. `list_processes.py`
Lists all available process templates in the organization.

**Usage:**
```bash
export AZURE_DEVOPS_PAT="your-pat-here"
python3 list_processes.py
```

**Output Example:**
```
Available Process Templates:
================================================================================
Name: ᵉShareScrum
  Type ID: f947341c-51f4-4bc9-a4af-529e218cb4dc
  Is Enabled: True
  Is Default: False
```

#### 8. `audit_issue_links.py`
Audits Issue work item links to verify correct Related link types.

**What it does:**
- Reads local data files (`ALL Items.json`, `WorkItemLinks.json`) — no ADO PAT required
- Checks Enhancement Request Issues for a Related link to a Feature
- Checks Bug Issues for a Related link to a Bug
- Reports items with no link, wrong link type (Parent/Child instead of Related), or correct links
- Categorizes Issues by Ticket Category field (Enhancement Request, Bug, or other)

**Usage:**
```bash
# Full audit (all states)
python3 audit_issue_links.py

# Filter to active Issues only
python3 audit_issue_links.py --state Active

# Show ADO URLs for problem items
python3 audit_issue_links.py --verbose
```

**Options:**
| Option | Description |
|--------|-------------|
| `--state STATE` | Filter by state: `Active` (excludes Done/Closed), `Done`, `Closed`, or `All` (default) |
| `--verbose` | Show Azure DevOps URLs for each problem item |

**Example Output:**
```
Enhancement Request Issues:  60 total → 49 ✅ correct, 8 ❌ no link, 3 ⚠️ wrong type
Bug Issues:                 100 total → 56 ✅ correct, 28 ❌ no link, 16 ⚠️ wrong type
```

#### 9. `sync_tags_between_linked_items.py`
Syncs tags between linked Issue and Feature/Bug work items.

**What it does:**
- Reads local data files (`ALL Items.json`, `WorkItemLinks.json`) for analysis — no ADO PAT required for dry run
- Copies CS tags (`CS: High Value`, `CS: Low Value`, `CS: Strategic`) from Issue (ER) → Related Feature
- Copies OKR tags (`1:*`, `2:*`, `3:*`, `4:*`) from Feature → Related Issue (ER)
- Copies architecture tags (`UI:*`, `CWP:*`, `SCG:*`, `ESG:*`, `Analytics:*`, `Utilities:*`, `Infra:*`) from Bug → Related Issue (Bug)
- Only processes items with Related links (not Parent/Child)
- Checks for existing tags — no duplicates

**Usage:**
```bash
# Dry run — report what needs updating (default, no PAT needed)
python3 sync_tags_between_linked_items.py

# Show details of each update
python3 sync_tags_between_linked_items.py --verbose

# Filter to active Issues only
python3 sync_tags_between_linked_items.py --state Active

# Apply updates to Azure DevOps (requires PAT)
export AZURE_DEVOPS_PAT="your-pat-here"
python3 sync_tags_between_linked_items.py --apply
```

**Options:**
| Option | Description |
|--------|-------------|
| `--state STATE` | Filter Issues by state: `Active` (excludes Done/Closed), `Done`, `Closed`, or `All` (default) |
| `--verbose` | Show details of each update (target, source, tags to add, ADO URL) |
| `--apply` | Push tag updates to Azure DevOps (requires `AZURE_DEVOPS_PAT`) |

**Tag Sync Rules:**
| Source | Target | Tags Copied |
|--------|--------|-------------|
| Issue (ER) | Related Feature | CS tags (`CS:*`) |
| Feature | Related Issue (ER) | OKR tags (`1:*` – `4:*`) |
| Bug | Related Issue (Bug) | Architecture tags (`UI:*`, `CWP:*`, etc.) |

#### 10. `add_picklist_bulk.py`
Attempts to add picklist values in bulk (API limitations encountered).

**Note:** This script encountered Azure DevOps API limitations. Manual picklist population was ultimately required through the UI.

#### 11. `add_picklist_values_v2.py`
Alternative approach for adding picklist values (also encountered API limitations).

**Historical Note:** Multiple API approaches were attempted but ultimately manual UI entry was most reliable.

## Installation

### Prerequisites
- Python 3.11+
- Azure DevOps Personal Access Token (PAT) with Work Items (Read & Write) permissions

### Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install azure-devops pytz requests
```

### Environment Configuration
```bash
# Set your Azure DevOps PAT
export AZURE_DEVOPS_PAT="your-personal-access-token-here"
```

## Migration Results

### Summary Statistics

| Phase | Script | Work Items | Success | Failed |
|-------|--------|-----------|---------|--------|
| 1 | convert_all_target_dates_production.py | 378 | 368 | 0 |
| 2 | copy_target_date_to_cascading.py | 381 | 351 | 0 |
| 3 | copy_release_version_to_cascading.py | 590 | 586 | 4* |

*4 failures resolved manually after adding missing picklist value `202601.3.0`

**Total:** 941 successful field migrations across 969 work items

### Data Quality Notes

1. **Timezone Conversions:**
   - 8 out of 10 test bugs showed +1 day advancement (22:00 UTC → next day in Athens)
   - 2 out of 10 remained same day (daytime hours)
   - All conversions used UTC+02:00 offset (correct for January/February 2026)

2. **Picklist Values:**
   - Target dates: 84 unique values covering August 2025 through December 2026
   - Release versions: 90 values (89 planned + 1 discovered during migration)

3. **Field Coverage:**
   - Custom.Target_Date: 381 work items (378 queried initially, 3 added during migration)
   - Custom.ReleaseVersion: 590 work items

## Lessons Learned

### API Challenges
1. **Process Template API:** Unable to programmatically add picklist values to custom fields using the process template API
2. **Organization-level Picklists:** PUT operations required exact payload structure that was difficult to determine
3. **Solution:** Manual UI entry was most reliable for populating picklists

### Best Practices Discovered
1. **Picklist Validation:** Temporarily disable "allow only values in list" during bulk migrations
2. **Batch Processing:** 200 items per batch proved optimal for ADO API
3. **Progress Indicators:** Show progress every 50 items for long-running operations
4. **Verification First:** Always test with 10 items before running full migration

### Timezone Handling
- Use `pytz.timezone('Europe/Athens')` for Athens timezone
- Azure DevOps stores all datetime fields in UTC (ISO format with 'Z')
- Conversion formula: `utc_dt.astimezone(ATHENS).strftime('%Y-%m-%d')`
- Always test timezone conversions with sample data first

## Next Steps

### Recommended Actions
1. ✅ **Hide deprecated fields from UI:**
   - `Microsoft.VSTS.Scheduling.TargetDate`
   - `Custom.Target_Date`
   - `Custom.ReleaseVersion`

2. ✅ **Configure new picklist fields:**
   - `Custom.CascadingDate` - Target dates
   - `Custom.CascadingVersion` - Release versions

3. ⚠️ **Data Cleanup (Optional):**
   - Review and remove unused picklist values
   - Verify all work items have correct cascading values

4. 📝 **Documentation:**
   - Update team wiki with new field usage
   - Train team on using picklist fields instead of free text

### Future Migrations
If similar migrations are needed:
1. Start with test environment
2. Use process template copy for experimentation
3. Test with 10 items first
4. Consider UI automation for picklist population
5. Keep batch size at 200 for optimal performance

## Troubleshooting

### Common Issues

**Problem:** `AZURE_DEVOPS_PAT environment variable not set`  
**Solution:** `export AZURE_DEVOPS_PAT="your-pat-here"`

**Problem:** `Process 'eShareScrum' not found`  
**Solution:** Process name has superscript 'e': `ᵉShareScrum`

**Problem:** `The field 'X' contains the value 'Y' that is not in the list of supported values`  
**Solution:** Either add the value to the picklist or temporarily disable list validation

**Problem:** `pip: command not found`  
**Solution:** Use `pip3` or `python3 -m pip`

**Problem:** Rate limiting / 429 errors  
**Solution:** Scripts include small delays; if persistent, increase batch delay or reduce batch size

## Security Notes

- **Never commit PAT tokens to Git**
- PAT tokens should have minimal required permissions (Work Items: Read & Write)
- Use environment variables for all credentials
- Tokens expire - update as needed
- Consider using Azure CLI authentication for production environments

## References

### Azure DevOps API Documentation
- [Work Item Tracking REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/)
- [Process Template API](https://learn.microsoft.com/en-us/rest/api/azure/devops/processes/)
- [Python SDK](https://github.com/microsoft/azure-devops-python-api)

### Timezone Resources
- [pytz Documentation](https://pythonhosted.org/pytz/)
- [Europe/Athens Timezone](https://en.wikipedia.org/wiki/Time_in_Greece)

## Support

For questions or issues with these scripts:
1. Check the troubleshooting section above
2. Review the SESSION_LOG.md for detailed implementation notes
3. Consult Azure DevOps API documentation
4. Contact: Tony Themistokleous (tonythem@)

## License

These scripts are internal tools for eShare Azure DevOps data migration.

---

**Last Updated:** February 4, 2026  
**Migration Status:** ✅ Complete  
**Total Work Items Migrated:** 941 successful updates across 969 work items
