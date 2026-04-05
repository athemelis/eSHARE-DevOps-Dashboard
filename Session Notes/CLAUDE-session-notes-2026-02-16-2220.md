# Session Notes - February 16, 2026 (10:20 PM)

## Commits in this PR

1. `34ae009` - v174: Add changelog validation to dev-status.sh and update version bump process
2. `1ff6a75` - v174: Improve What's New link visibility in Info popup

## Changes Made

### 1. Changelog Validation & Process Improvement
- **Problem:** v173 and v174 changelog entries were skipped/left as placeholders
- **Root Cause:** Changelog was written at version bump time with placeholder text, then never updated before commit
- **Fix (dev-status.sh):** Added validation that warns if:
  - `changelog.js` contains placeholder text ("Session in progress", "coming soon", "placeholder", "TODO")
  - `changelog.js` is missing an entry for the current version
- **Fix (instructions):** Updated Version Change Checklist in both `CLAUDE.md` and `copilot-instructions.md` to split into two phases:
  - **Version bump time (session start):** Update version numbers only (items 1-8/9)
  - **Commit time:** Write real changelog.js and DASHBOARD_README.md entries (items 9-10/10-11)
- **Also fixed:** Added real v173 ("Clickable Date Issues Insight") and v174 ("Estimate Warnings & Resize Handles") entries to changelog.js and DASHBOARD_README.md

### 2. What's New Link Visibility in Info Popup
- **Problem:** "🚀 What's New" link in Info popup looked like a heading rather than a clickable link
- **Fix (dashboard-body.html):** Changed link text to "🚀 What's New - click to view" across all 8 info panels
- **Fix (dashboard.css):** 
  - Always-visible underline on the link (was only on hover)
  - Hover changes color to white for click feedback
  - Added separator line (bottom border) between What's New link and dashboard info content

## Files Changed
- `dev-status.sh` - Changelog validation warnings
- `CLAUDE.md` - Updated Version Change Checklist
- `.github/copilot-instructions.md` - Updated Version Management checklist
- `changelog.js` - Real v173 and v174 entries
- `DASHBOARD_README.md` - Real v173 and v174 version history rows
- `dashboard-body.html` - What's New link text updated (8 instances)
- `dashboard.css` - What's New link styling improvements

## Decisions
- Changelog content should be written at commit time, not version bump time, to avoid stale placeholders
- dev-status.sh validates changelog before every commit as a safety net

## Open Items
- None

## Next Steps
- Continue with any new feature work
