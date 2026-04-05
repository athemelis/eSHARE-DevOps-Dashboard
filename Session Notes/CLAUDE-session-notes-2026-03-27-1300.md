# Session Notes - 2026-03-27 (v247)

## Summary
Spec Kit onboarding and migration from tony-dev branch to Standard GitHub Flow.

## Commits
- `b6151ad` v247: Spec Kit onboarding & GitHub Flow migration

## Changes Made

### 1. Pre-Migration Archive
- Created git tag `pre-speckit` on the last tony-dev commit (c88a972) before any changes
- Tag pushed to remote — any file can be restored with `git show pre-speckit:<filename>`

### 2. Spec Kit Constitution (`.specify/memory/constitution.md`)
- Initialized GitHub Spec Kit with 9 project principles:
  - I. Generic Infrastructure Over Dashboard-Specific Code
  - II. Architecture & Data Pipeline
  - III. Branching & Deployment Strategy (GitHub Flow)
  - IV. Theme System & UX Consistency
  - V. State Persistence
  - VI. ADO Integration & Inline Editing
  - VII. Regression Testing
  - VIII. Code Organization
  - IX. Performance Considerations
- 7 alert types that specs must flag (specific code, hardcoded colors, custom tables, etc.)
- Governance section with amendment procedure and semantic versioning

### 3. Branching Model Migration
- **Old**: All work on `tony-dev` branch, PR from `tony-dev` → `main`
- **New**: Standard GitHub Flow — feature branches from `main`, PRs directly to `main`
- Updated files:
  - `dev-status.sh` — rewritten to be branch-agnostic (works with any branch, not just tony-dev)
  - `.github/copilot-instructions.md` — new session workflow with Spec Kit integration
  - `CLAUDE.md` — removed Cowork-specific sections, updated to GitHub Flow
  - `GIT-WORKFLOW.md` — rewritten for feature branch model

### 4. Spec Kit Files Added
- `.specify/` — constitution, templates, scripts
- `.github/agents/` — 9 Spec Kit agent definitions
- `.github/prompts/` — 9 Spec Kit prompt files

## Decisions
- **Drop tony-dev entirely**: Moving to per-feature branches eliminates the single-contributor bottleneck
- **Include branching migration in this PR**: Cleaner than having stale tony-dev references in production after merge
- **Archive via git tag, not file copies**: `pre-speckit` tag is permanent and covers all files

## Next Steps
- After PR merge: delete `tony-dev` branch (local + remote)
- First feature spec via Spec Kit to validate the new workflow
