# Session Notes: Workflow Instruction Fixes

**Date:** 2026-02-08  
**PR:** #71  
**Version:** v157 (no version bump - documentation only)

## Summary

Fixed workflow instructions in CLAUDE.md and copilot-instructions.md to ensure Copilot CLI runs commands directly instead of asking user to run them, and added explicit checklists to prevent skipping required steps.

## Commits in PR

1. **ec3f632** - `Fix After PR Merged workflow - Copilot runs commands directly`
   - Updated "After PR Merged" section to have Copilot run dev-status.sh directly
   - Changed from "ask user to run" to "run and display output"
   - Added confirmation step before syncing tony-dev with main

## Issues Identified During Session

Two instruction violations occurred:
1. **PR without session notes** - Created PR #70 without first creating session notes file
2. **git status instead of dev-status.sh** - Used `git status` before commit instead of `./dev-status.sh`

## Fixes Applied

### PR Checklist (new section)
Added explicit checklist requiring session notes BEFORE creating PR:

| # | Step | Action |
|---|------|--------|
| 1 | Create session notes | Create `Session Notes/CLAUDE-session-notes-YYYY-MM-DD-HHMM.md` |
| 2 | Include in notes | All commits, changes, decisions, open items |
| 3 | Commit session notes | `git add . && git commit` |
| 4 | Push to remote | `git push origin tony-dev` |
| 5 | THEN create PR | `gh pr create ...` |

### Commit Checklist (new section)
Added explicit checklist requiring dev-status.sh BEFORE committing:

| # | Step | Action |
|---|------|--------|
| 1 | Run dev-status | `./dev-status.sh` |
| 2 | Display output | Include FULL output in response |
| 3 | ASK user | "Ready to commit?" |
| 4 | WAIT | For explicit confirmation |
| 5 | THEN commit | `git add . && git commit && git push` |
| 6-8 | After commit | Run dev-status again, display, wait |

### After PR Merged (updated)
Changed from asking user to run commands to running them directly:
- Run `./dev-status.sh` and display output
- ASK user: "Ready to sync tony-dev with main?"
- Wait for confirmation, then run sync commands

### CRITICAL RULES (updated)
Added: `NEVER create PR without session notes`

## Files Changed

| File | Changes |
|------|---------|
| `CLAUDE.md` | Added Commit Checklist, PR Checklist, updated After PR Merged, added CRITICAL RULE |
| `.github/copilot-instructions.md` | Same updates for consistency |

## Decisions

- Checklists use table format (like Version Change Checklist) for visibility and enforceability
- Both instruction files kept in sync with identical checklists
- Legacy "ask user to paste output" instructions removed for Copilot CLI context

## Next Steps

- Monitor future sessions for instruction compliance
- Consider adding more checklists if other steps are frequently skipped
