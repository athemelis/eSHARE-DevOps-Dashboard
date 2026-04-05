# Session Notes - February 6, 2026

## Summary
This session focused on Issue cascading fields migration, creating a periodic sync script, and updating the Capacity Dashboard to use child Task iteration paths for Bug effort allocation.

## Commits in This PR

1. **eb325bd** `docs: Add copilot-instructions.md for Copilot CLI workflow`
   - Created copilot-instructions.md as alternative to CLAUDE.md for GitHub Copilot CLI
   - Added sections clarifying Copilot CLI vs Claude Cowork differences

2. **47572d8** `docs: Add script output display rule to copilot-instructions.md`
   - Added workflow confirmation requirements
   - Added script output display rule for dev-status, copy-data-files, serve-dashboard

3. **6164a08** `v156: Add Issue cascading fields migration scripts`
   - Created migrate_issue_release_version.py (6 Issues migrated)
   - Created migrate_issue_target_date.py (75 Issues migrated, 70 auto + 5 manual)
   - Updated ADO Python Scripts/README.md with Phase 5 documentation

4. **99ff58c** `feat: Add periodic sync script for Issue cascading fields`
   - Created sync_issue_cascading_fields.py for periodic sync of Issue cascading fields
   - Compares Bug Issues vs related Bugs, ER Issues vs related Features
   - Interactive prompts with options a/b/c/d for sync actions
   - Supports --dry-run, --auto-empty, --auto-all modes
   - Logs all changes to timestamped log file

5. **373cded** `feat: Bug effort from child Tasks, add Progress/Bug Owner columns`
   - Bug effort now calculated from child Tasks (iteration-aware) like Features use Delivery Slices
   - Bug 4100 example: shows 1.5d in Jan (Task 4101) and 1.1d in Feb (Tasks 5324, 4831)
   - Added originalEstimate field to data loader for Tasks
   - Progress popup: Renamed "Work" to "Actual", added Iteration column
   - Added Progress column to Bugs Dashboard and Roadmap Dashboard
   - Added Bug Owner column to Releases Dashboard (Customer/Internal Bugs)

## Key Changes

### Issue Cascading Fields Migration
- Migrated Issues to use Custom.CascadingVersion and Custom.CascadingDate
- 6 Issues needed ReleaseVersion migration
- 75 Issues needed TargetDate migration (with UTC→Athens timezone conversion)
- 5 Issues failed due to missing picklist values (fixed manually)

### Sync Script for Issues
- sync_issue_cascading_fields.py compares Issue cascading fields with related Bug/Feature
- Reports orphan Issues (Bug Issues without related Bug, ER Issues without related Feature)
- Interactive mode prompts for each category separately

### Capacity Dashboard - Bug Effort by Task Iteration
- Previously: Bug effort came from Bug's 8 estimation fields, shown in Bug's own iteration
- Now: Bug effort comes from child Tasks' originalEstimate, filtered by Task iteration
- Bug can now appear in multiple iterations if it has Tasks in different iterations
- Team assignment comes from Task's areaPath (e.g., eShare\Frontend → Frontend)

### New Table Columns
| Dashboard | Table | New Column | Position |
|-----------|-------|------------|----------|
| Bugs | Bug Details | Progress | After State |
| Roadmap | Feature Details | Progress | After State |
| Releases | Customer Bugs | Bug Owner | Before Assigned To |
| Releases | Internal Bugs | Bug Owner | Before Assigned To |

## Files Modified
- copilot-instructions.md (new)
- ADO Python Scripts/migrate_issue_release_version.py (new)
- ADO Python Scripts/migrate_issue_target_date.py (new)
- ADO Python Scripts/sync_issue_cascading_fields.py (new)
- ADO Python Scripts/README.md
- dashboard.js
- dashboard-loader.js
- CLAUDE.md

## Open Items
- None

## Next Steps
- Monitor sync_issue_cascading_fields.py usage and adjust as needed
- Consider adding sync script to scheduled automation
