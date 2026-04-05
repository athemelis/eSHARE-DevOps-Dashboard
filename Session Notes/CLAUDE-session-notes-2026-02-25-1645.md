# Session Notes — 2026-02-25 1645

## Commits in this PR
- `920534c` — v186: Standardize table columns across all dashboards

## Changes Made

### 1. Standardized Table Columns (all 7 generic tables)
Aligned columns across Releases (Features, Issues, Customer Bugs, Internal Bugs), Roadmap (Feature Details), Customers (Issue Details), and Bugs (Bug Details) to a consistent spec.

**Columns added:**
- Priority → all 4 Releases tables
- Tags → Releases Features, Releases Issues
- Assigned To → Releases Issues, Customers Issue Details
- Team → Roadmap Feature Details, Bugs Bug Details
- Architecture → Bugs Bug Details

**Columns removed:**
- Category → Releases Issues
- Bug Type → Releases Internal Bugs
- Tags → Bugs Bug Details

**Column order standardized** to: ID → Title → State → Priority → Customer → Category → Bug Type → Progress → Aging → Architecture → Tags → CS Owner → Bug Owner → Assigned To → Team → Release → Target Date → Effort

### 2. Generic Default Renderers
Moved Tags, Customer, and Architecture column rendering into `genericTableDefaultRenderCell()` so all tables consistently show each value on a separate line using `<div class="tag-line">`. Per-table custom renderCells now delegate to the default via `return null`.

### 3. Reference Document
Created `Table-Columns.md` — defines the standard column spec for all 7 tables plus a column key reference mapping labels to JS keys.

## Decisions
- Effort column kept only on Roadmap Feature Details (per user spec)
- Customer label standardized to singular "Customer" across all tables
- Architecture column in Bugs uses same `getArchitectureTags()` helper as Releases bug tables

## Open Items
None

## Next Steps
- Merge PR and sync branches
