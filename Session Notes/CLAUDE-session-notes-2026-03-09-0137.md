# Session Notes — 2026-03-09 0137

## Version: v222

## Commits in this PR
- `652d328` — v222: Modal contextual tags & pill breadcrumb navigation

## Changes Made

### Modal Contextual Tags
- **Feature**: Unified Modal header already showed OKR + CS tags (no change needed)
- **Issue (Enhancement Request)**: Added CS tags (orange pills) to the header
- **Bug**: Already showed Architecture tags (no change needed)
- **Task**: Added Iteration Path (cyan pill) to the header, with `eShare\` prefix stripped and backslashes replaced with ` › `

### Pill Breadcrumb Navigation
- **Problem**: Clicking a relationship pill in the modal header (e.g., Issue pill on a Bug) opened the linked item as a fresh modal without breadcrumbs, so there was no way to navigate back
- **Fix**: Added `_modalCurrentItem` variable to track the currently displayed item. `openPillModal()` now pushes the current item onto `_modalNavStack` and opens the linked item with `{ _navigate: true }`, enabling breadcrumb trail navigation
- Cleared `_modalCurrentItem` on modal close to prevent stale state

## Files Modified
- `dashboard.js` — Added `_modalCurrentItem` tracking, CS tags for ER Issues, Iteration Path for Tasks, updated `openPillModal` for breadcrumb navigation
- `dashboard.css` — Added `.modal-iteration-pill` style (cyan)
- `dashboard.html` — Version bump v221 → v222
- `dashboard-body.html` — Version bump
- `CLAUDE.md` — Version bump
- `.github/copilot-instructions.md` — Version bump
- `DASHBOARD_README.md` — Version bump + v222 history entry
- `changelog.js` — v222 changelog entry

## Decisions
- Reused existing pill styles for consistency (cyan for iteration, orange for CS, purple for architecture)
- Iteration Path strips the root `eShare\` prefix for readability

## Open Items
- None

## Next Steps
- Merge PR, sync tony-dev with main
