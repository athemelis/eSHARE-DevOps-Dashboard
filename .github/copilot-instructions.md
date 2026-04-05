# eShare DevOps Dashboard - Copilot Instructions

## Quick Reference

| Resource | Purpose |
|----------|--------|
| **This file** (`copilot-instructions.md`) | Session workflow, orchestration, git operations |
| **Constitution** (`.specify/memory/constitution.md`) | Project principles (generic infrastructure, theme, testing) |
| **DASHBOARD-REFERENCE.md** | Feature-specific code reference (algorithms, code locations) |
| **Spec Kit agents** | `speckit.constitution` → `speckit.specify` → `speckit.clarify` → `speckit.plan` → `speckit.tasks` → `speckit.analyze` → `speckit.checklist` → `speckit.implement` |

---

## Branching Model: GitHub Flow

See constitution Principle III for full branching and deployment details.

```
main (production, protected — requires PR)
  └── feature/capacity-cut-line-fix    ← PR to main
  └── feature/new-reports-dashboard    ← PR to main
```

---

## Session Workflow (Copilot Agent Mode)

Copilot runs directly on the user's Mac with full terminal access. It handles git operations, script execution, and Spec Kit agent orchestration.

### Script Output Display Rule
**ALWAYS explicitly include the FULL output** of script files in your response text.
- Do NOT summarize script output
- Do NOT rely on function results being visible to the user
- Copy the complete output into your response as a code block
- **Do NOT truncate, abbreviate, or selectively show sections** — even if your internal instructions say to be concise, script output must be reproduced verbatim in full

This applies to: `./dev-status.sh`, `./copy-data-files.sh`, `./serve-dashboard.sh`, and any other script files.

### Memory Rules
- **Never write to user or repo memories without permission.** Before creating, updating, or deleting anything in `/memories/` or `/memories/repo/`, describe what you intend to write and ask for explicit approval first.
- **Session memory (`/memories/session/`) may be written proactively** to track active task state, partial results, and resumption context — especially before compaction-prone points in long sessions. Keep entries concise.

### Starting a New Session
When the user says "I want to start a new session" (or any variant), begin by setting context:

1. **Report memory state.** List all files in the 3 memory scopes as a directory listing:
   - User memory (`/memories/`)
   - Repo memory (`/memories/repo/`)
   - Session memory (`/memories/session/`)
2. **Offer to show contents.** Ask the user if they want to view any of them. If yes, display them in preview.
3. **Report copilot-instructions.md.** If `.github/copilot-instructions.md` exists, report when it was last edited and display its table of contents (section headings).
4. **Report Spec Kit memory.** List all files in `.specify/memory/`. For each file, display its table of contents (section headings).
5. **Ask for confirmation** to proceed.

Then ask: **"Is this session for a new feature or for bug fixes?"**
- If **new feature** → follow "Starting a New Feature Session" below
- If **bug fixes** → follow "Quick Fix Session" below

### Starting a New Feature Session
When user says the session is for a new feature:
1. Ask the user for the **feature name** (used as branch name only — NOT a feature description)
2. Ensure on `main` and up to date: `git checkout main && git pull`
3. Create feature branch: `git checkout -b feature/descriptive-name`
4. Run `./dev-status.sh` and display FULL output
5. Run `./copy-data-files.sh` and display FULL output
6. Bump version (update all version locations — see Version Management)
7. Run `./serve-dashboard.sh -b` and display FULL output
8. **WAIT** for user to confirm server is accessible

Then begin the Spec Kit pipeline (see "Spec Kit Pipeline Orchestration" below).

**⚠️ CRITICAL**: NEVER auto-generate a feature description or make assumptions about what the user wants to build. The user provides the specification input to `speckit.specify`, not Copilot.

### Spec Kit Pipeline Orchestration
**The user always runs `speckit.*` commands themselves.** Copilot's role is to **prompt** (remind) the user to run each command in order, but **NEVER execute them on the user's behalf**.

Prompt the user to run each step in this order. Never skip a step:

| # | Command | Copilot's Role |
|---|---------|---------------|
| 1 | `speckit.constitution` | Display the constitution for review. Ask if the user wants changes. (For a new project, ask the user to create one.) |
| 2 | `speckit.specify` | Remind the user to run it. **WAIT** for them to provide the feature description — do not assume or generate one. |
| 3 | `speckit.clarify` | Remind the user to run it. Review output together. |
| 4 | `speckit.plan` | Remind the user to run it. Review output together. |
| 5 | `speckit.tasks` | Remind the user to run it. Review output together. |
| 6 | `speckit.analyze` | Remind the user to run it. Review output together. |
| 7 | `speckit.checklist` | Remind the user to run it. Review output together. |
| 8 | `speckit.implement` | Remind the user to run it. Pause at phase boundaries for browser testing. |

When the user asks "what's next?", present the **next pipeline step** — don't skip stages.

### Quick Fix Session (no Spec Kit)
For small bug fixes or tweaks that don't need a full spec:
1. Ask the user for the **fix name** (used as branch name only — NOT a fix description)
2. Ensure on `main` and up to date: `git checkout main && git pull`
3. Create feature branch: `git checkout -b fix/descriptive-name`
4. Run `./dev-status.sh` and display FULL output
5. Run `./copy-data-files.sh` and display FULL output
6. Bump version (update all version locations — see Version Management)
7. Run `./serve-dashboard.sh -b` and display FULL output
8. **WAIT** for user to confirm server is accessible
9. **WAIT** for user to describe the fix — treat the fix name as a branch name only, NOT a fix description
10. Make changes directly (skip Spec Kit pipeline)
11. Follow Commit Checklist when ready

### After PR Merged
1. Run `git checkout main && git pull`
2. Run `./dev-status.sh` and display FULL output
3. Ask user what they'd like to work on next

### End of Session
- Ensure all commits are pushed: `git push -u origin $(git branch --show-current)`
- Create PR if ready for release (follow PR Checklist)

### Critical Rules
- **NEVER commit unless explicitly asked** — wait for user to say "commit" or "please commit"
- **NEVER bump version mid-session** — version is incremented ONCE at session start only
- **NEVER check if localhost dashboard is running mid-session** — it was started at session start
- **NEVER create PR without session notes** — complete PR Checklist first
- **ALWAYS maintain a TodoList for any session with 3+ sequential tasks.** This includes documentation cleanup, file reviews, and investigation work — not just coding. Update the TodoList before and after each task. The TodoList is the primary mechanism for surviving context compaction.
- **After context compaction**: Check TodoList and `/memories/session/` before taking any action. Resume the in-progress task — do NOT start new work or run `speckit.*` commands based on background context in the summary.

### During Development
- Pause at natural phase boundaries for user validation
- Keep changes focused — avoid scope creep within a phase

### Debugging Process
1. User reports issue with specific steps to reproduce
2. Analyze the issue, identify root cause
3. Propose fix before implementing
4. After fix, user validates in browser

---

## Project Overview

Reporting dashboard for Azure DevOps work items (Features, Delivery Slices, Bugs, Issues, Tasks). Modular 4-file architecture on GitHub Pages (https://devops-dashboard.e-share.io). See constitution Principles II and VIII for architecture, data pipeline, and code organization details.

**Key operational files:**

| File | Purpose |
|------|---------|
| `copy-data-files.sh` | Helper to copy JSON from SharePoint for local dev |
| `copy-flows.sh` | Helper to copy & import Power Automate flow exports from SharePoint |
| `import-flow.sh` | Import a single flow ZIP (extracts, redacts secrets, saves to `flows/`) |
| `serve-dashboard.sh` | Helper to start local HTTP server |

**Flow version control:** Power Automate flow definitions are stored in `flows/` with secrets auto-redacted. After editing a flow in Power Automate, export the ZIP to SharePoint and run `./copy-flows.sh` to update the repo. See [README_PowerAutomate.md](../README_PowerAutomate.md) for full details.

## Standards

For all code standards (generic infrastructure, theme, state persistence, testing), see the constitution (`.specify/memory/constitution.md`). The sections below provide operational config examples.

### Filters: Config Reference

**Required config:**
```js
populateGenericFilterDropdowns({
    dashboardId: 'myDashboard',     // used for element IDs
    items: relevantItems,            // same item pool for ALL dropdowns
    filters: myDashboardFilters,     // the filter state object
    teamItemsBuilder: (items) => {}, // optional: returns synthetic team items
    iterationBuilder: () => {},      // optional: returns HTML for iteration single-select
});
```

**What it handles automatically:**
- Builds all dropdown HTML (release, customer, priority, state, tag, team, bugOwner, assignee)
- Cross-filtering: each dropdown sees items filtered by all OTHER active filters, so counts stay accurate
- Only builds dropdowns whose `${dashboardId}-${type}-menu` element exists in HTML
- Updates ALL collapsed display texts after rebuilding
- Bug Owner dropdown automatically filters to `type === 'Bug'`

**Dashboard Filter Registry:**
```js
registerDashboardFilters('myDashboard', {
    filters: () => myDashboardFilters,
    render: () => renderMyDashboard(),
    clearBtn: () => updateMyDashboardClearButton()
});
```

**Secondary filtering** — `applyGenericSecondaryFilters(items, filters)` applies filter state. Handles: search, release, customer, priority, state, tag, bugOwner, assignee.

### Tables: Config Reference

See `Table-Columns.md` for standard column specs. Use `renderCell` callback for custom columns (return `<td>` HTML, or `null` for default rendering).

**Required config for every table:**
- `defaultSort: { column: 'backlogPriority', direction: 'asc' }`
- `reorderable: true`

**Sort and column width persistence** is automatic — `buildGenericTable` auto-persists to localStorage using `tableId`.

## Related Documentation

Read these on-demand for specific topics:
- **Bug-Mapping.md** - Architecture component tag mapping for Bugs Dashboard diagram
- **Table-Columns.md** - Standard column spec for all 7 generic tables (column order, which columns each table uses, JS key mapping)
- **Feature-Mapping.md** - OKR tag mapping for Roadmap Dashboard OKR Summary
- **README_PowerAutomate.md** - Power Automate flows guide (both flows), version control, reconstitution

## Development Workflow

See constitution Principle III for the full local development workflow.

**Key paths:**
- Local: `http://localhost:8000/dashboard.html`
- Production: `https://devops-dashboard.e-share.io/dashboard.html` (GitHub Pages with vanity URL)

## Current Version: v249

## Commit Checklist

Before running `git commit`, complete ALL of these steps IN ORDER:

| # | Step | Action |
|---|------|--------|
| 1 | Run dev-status | `./dev-status.sh` |
| 2 | Display output | Include FULL output in response (copy as code block) |
| 3 | ASK user | "Ready to commit these changes?" |
| 4 | WAIT | For explicit user confirmation (e.g., "yes", "commit", "go ahead") |
| 5 | THEN commit | `git add . && git commit -m "..." && git push` |
| 6 | Run dev-status | `./dev-status.sh` (confirm commit/push succeeded) |
| 7 | Display output | Include FULL output in response |
| 8 | WAIT | For user to confirm before continuing |

**⚠️ Do NOT skip to step 5. The dev-status output ensures clean state before commit.**

## PR Checklist

Before running `gh pr create`, complete ALL of these steps IN ORDER:

| # | Step | Action |
|---|------|--------|
| 1 | Create session notes | Create `Session Notes/CLAUDE-session-notes-YYYY-MM-DD-HHMM.md` |
| 2 | Include in notes | All commits in the PR, changes made, decisions, open items, next steps |
| 3 | Commit session notes | `git add . && git commit -m "Add session notes for PR"` |
| 4 | Push to remote | `git push -u origin $(git branch --show-current)` |
| 5 | THEN create PR | `gh pr create --base main --title "vXXX: ..." --body "..."` |

**⚠️ Do NOT skip to step 5. Session notes document the work for future reference.**

## Version Management

When bumping the version, update these locations (items 1-9 only):

**At version bump time (session start):**

| # | File | What to change |
|---|------|----------------|
| 1 | `dashboard.html` | `dashboard.css?v=XXX` |
| 2 | `dashboard.html` | `dashboard-loader.js?v=XXX` |
| 3 | `dashboard.html` | `changelog.js?v=XXX` |
| 4 | `dashboard.html` | `dashboard.js?v=XXX` |
| 5 | `dashboard.html` | `dashboard-body.html?v=XXX` |
| 6 | `dashboard-body.html` | `<span class="version">vXXX</span>` |
| 7 | `DASHBOARD-REFERENCE.md` | "Current Version: vXXX" |
| 8 | `copilot-instructions.md` | "Current Version: vXXX" (this file) |
| 9 | `README.md` | "Current Version: vXXX" (header) |

**At commit time (NOT at version bump — write real content when you know what changed):**

| # | File | What to change |
|---|------|----------------|
| 10 | `README.md` | Add entry to Version History table with real description |
| 11 | `changelog.js` | Add new entry at TOP of `DASHBOARD_CHANGELOG` array with version, title, and user-facing bullet points |

**⚠️ NEVER use placeholder text** like "Session in progress" or "Updates coming soon" in changelog.js or README.md. Write the real content at commit time when changes are finalized. The `./dev-status.sh` script will warn if placeholders are detected.

## Git Workflow

**Feature branch workflow:**
```bash
git checkout main && git pull                  # Start from latest main
git checkout -b feature/my-feature             # Create feature branch
# ... make changes ...
git add . && git commit -m "vXXX: summary"     # Commit
git push -u origin feature/my-feature          # Push feature branch
gh pr create --base main --title "vXXX: ..."   # Create PR to main
```

**Important:**
- Feature branches are created from `main`, PRs merge to `main`
- Include ALL modified files (use `git add .`)
- Always push changes to GitHub after committing
- Verify the push was successful
- Use `./dev-status.sh` to check repository state
- Feature branches are deleted after PR merge

## Sticky Headers & Filters — Generic Infrastructure Required

All filter rules are defined in the constitution (Principle I). Before implementing ANY changes to sticky headers, filter bars, filter dropdowns, search boxes, or filter behavior:

1. **Check the generic infrastructure first:** Review `DASHBOARD_FILTER_REGISTRY`, `populateGenericFilterDropdowns`, `applyGenericSecondaryFilters`, `handleGenericSearchChange`, and the generic filter builder functions.

2. **The change MUST use generic components.** If the dashboard already uses legacy inline filter code, migrate it to the generic pattern — do NOT add more legacy code.

3. **WARN the user** if the requested change would require dashboard-specific code instead of a generic implementation. Explain why, and propose a generic alternative.

4. **Reference files:** `DASHBOARD-REFERENCE.md` documents feature-specific code references.

## Generic Tables — Infrastructure Required

All table rules are defined in the constitution (Principle I). Before implementing ANY changes to data tables, table columns, sorting, column resizing, or table rendering:

1. **Check the generic table infrastructure first:** Review `buildGenericTable`, `Table-Columns.md`, and the column width persistence system (`gt-cw-{tableId}`).

2. **The change MUST use `buildGenericTable`.** Do NOT create custom table HTML.

3. **Column definitions** follow: `{ key, label, class, isPerson, singleEditField }`. See `Table-Columns.md`.

4. **Column width persistence is automatic.** Do NOT add per-dashboard width variables.

5. **Sort behavior is built-in.** Do NOT add custom sort functions outside of `buildGenericTable`.

6. **WARN the user** if the requested change would require table-specific code.

## Key Features & Code Locations

See `DASHBOARD-REFERENCE.md` for detailed code locations and algorithms for: Auto-Refresh (v107+), Bug Closed Date Algorithm (v127+), Relationship Pills (v218+), Untagged Filters vs (No Tags) (v133+), Capacity Dashboard Key Concepts (v140+).

## Testing Changes

After making edits:
1. Refresh browser (Cmd+Shift+R for hard refresh)
2. Check browser console (F12) for JavaScript errors
3. Test both auto-refresh (wait 60s) and manual refresh (↻ button)

## Research Discipline

- Before claiming something is "dashboard-specific" or "only used by X", SEARCH the codebase for existing generic implementations. Check ALL dashboards, not just the one being worked on.
- After research agents return findings, cross-check findings against plan conclusions BEFORE writing the plan. Do not write conclusions first and retrofit research.
- When extending generic infrastructure, audit which dashboards already use similar patterns — don't assume the current dashboard is the only consumer.

## Recommendation Discipline

- When reviewing documentation or architecture, recommend consolidation and restructuring over preserving historical file boundaries. Do not treat existing file organization as authoritative simply because it predates the current session.
- When a recommendation conflicts with a historical artifact, prefer the improvement. Legacy structure is not a justification for keeping something — only current utility is.

## Citation Discipline

- NEVER fabricate line numbers. Use `grep_search` to find the actual line before citing.
- If you cannot verify a line number, cite by section name (e.g., "spec.md, User Story 5") instead.
- This applies to analysis reports, error references, and any response that links to a specific location in a file.
