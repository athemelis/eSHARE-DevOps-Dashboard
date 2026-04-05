# Session Notes — 2026-04-03 (Data Source Corruption Fix)

## Branch: fix/data-source-corruption

## Commits
- `1c96487` v249: Fix WorkItemLinks data truncation, add flow version control tooling

## Changes Made

### Root Cause Investigation
- Compared ALL Items.json files in debugging/ — no corruption found (normal 2-day delta)
- Compared WorkItemLinks.json files — **truncated at exactly 10,000 rows** (should be ~15,400)
- Root cause: Power Automate Foreach+Append pattern created ~15K actions/run, causing Do Until timeout before pagination completed

### Power Automate Flow Fix
- Replaced Foreach+Append with Compose+union() two-step pattern in Export ADO WorkItemLinks flow
- Runtime: 45–270 minutes → 13 seconds
- Actions/run: ~15,000 → 19
- Data restored: 10,000 → 15,398 links

### Flow Version Control Tooling (New)
- `import-flow.sh` — Extracts flow ZIP, pretty-prints definition.json, auto-redacts secrets (PAT, Authorization headers, base64 strings)
- `copy-flows.sh` — Copies flow ZIPs from SharePoint, runs import-flow.sh on each
- `flows/ADO-ALL-Items/` — ALL Items flow definition (no secrets to redact)
- `flows/Export-ADO-WorkItemLinks/` — WorkItemLinks flow definition (PAT and Auth header redacted)
- `.gitignore` updated to ignore raw ZIPs but track JSON definitions

### Recurrence Interval Update
- ALL Items: 1 minute → 3 minutes
- WorkItemLinks: 6 hours → 5 minutes
- Combined action budget: 8,832/day (88% of 10K Office 365 limit)

### Documentation Restructure
- Renamed `README_ExportWorkItemLinks.md` → `README_PowerAutomate.md`
- New structure covers both flows, action budgets, content throughput limits, reconstitution guide
- Updated cross-references in README.md, DASHBOARD-REFERENCE.md, copilot-instructions.md, constitution.md

### Version Bump
- v248 → v249 across all 9 version locations

## Decisions
- Chose 3 min / 5 min intervals as balance between freshness and action budget (88% of limit)
- Used Compose+union two-step pattern to avoid Power Automate self-reference limitation on Set Variable
- Auto-redaction approach for PATs rather than manual scrubbing
- Renamed README to cover both flows since action budget analysis requires considering them together

## Open Items / Next Steps
- Monitor flow execution over next few days at 3 min / 5 min intervals
- Content throughput (~4.4 GB/day) exceeds official Low profile limit (200 MB) — not enforced during transition period but worth monitoring
- Consider trimming unused fields from ALL Items query to reduce payload size (8.6 MB/run)
- May adjust intervals based on monitoring results
