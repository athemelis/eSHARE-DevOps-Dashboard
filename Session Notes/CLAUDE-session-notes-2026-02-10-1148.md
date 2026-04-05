# Session Notes — 2026-02-10 11:48

## Commits in this PR

| Commit | Description |
|--------|-------------|
| b5fdf19 | v162: Fix What's New popup not showing on auto-refresh version detection (CSP blocked eval) |
| 60a60cd | v162: Auto-refresh triggers full page reload on version change to fix What's New popup |

## Changes Made

### What's New Popup Fix (v162)

**Problem:** When a new version was deployed and detected via auto-refresh, the version number in the header updated correctly but the "What's New" popup never appeared.

**Investigation — Attempt 1 (CSP / script injection):**
Initial analysis found that CSP blocked `new Function()` (eval) used to reload changelog.js. Replaced with CSP-safe dynamic `<script>` tag injection. However, testing revealed this still didn't work.

**Root Cause — Attempt 2 (correct fix):**
The fundamental issue is that the **old** dashboard.js (v161) is still running in the browser when auto-refresh detects a new version. Any fix in v162's dashboard.js doesn't help users currently on v161 — the old code with the broken `new Function()` approach is what's executing. Hot-patching JS in-place during auto-refresh is unreliable.

**Final Fix:** When auto-refresh detects `deployedVersion > localVersion`, trigger a **full page reload** (`window.location.reload()`) instead of trying to dynamically update in-place. This ensures:
- New dashboard.js, CSS, changelog.js, and HTML are all loaded fresh
- `showWhatsNew()` fires naturally on init with the correct changelog entries
- Normal auto-refresh cycles (same version) continue silently as before — no reload

**Files changed:** `dashboard.js`, `changelog.js`

## Decisions

- Full page reload on version change is simpler and more reliable than hot-patching JS/CSS in-place
- Only triggers when `deployedVersion > localVersion` — normal 60s auto-refresh is unaffected

## Open Items

- None

## Next Steps

- Merge PR and test the real auto-refresh version detection flow
