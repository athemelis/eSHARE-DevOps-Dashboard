# Session Notes — 2026-02-22 (ADO Data Envelope Fix)

## Commits in This PR

| Commit | Description |
|--------|-------------|
| `978de63` | v179: Fix ADO Extension Management API data envelope (unwrap value on read, wrap on save) |
| (this commit) | Add session notes for PR |

## Changes Made

### ADO Extension Management API Data Envelope Fix (`dashboard-loader.js`)
- **Problem:** Versions modal showed "No matches" in production despite ADO API returning 200 OK with valid data
- **Root cause:** ADO Extension Management API wraps documents in `{ id, value: { version, cascades }, __etag }` envelope. The `fetchCascadingListsFromADO()` function was returning the full envelope as `data`, so `result.data.cascades` was `undefined` (cascades lives at `result.data.value.cascades`)
- **Read fix:** Now returns `data.value` (the unwrapped inner document) instead of the full envelope
- **Save fix:** Wraps the payload back in `{ id, value: updatedData, __etag }` format that ADO expects. Previously sent flat `{ version, cascades, __etag }` which would have failed

## Context
This is the third hotfix for v179 cascading list features:
1. PR #101 — Picklist sync & conversation modal (original v179)
2. PR #102 — CSP fix for `extmgmt.dev.azure.com`
3. This PR — ADO data envelope unwrap/wrap fix
