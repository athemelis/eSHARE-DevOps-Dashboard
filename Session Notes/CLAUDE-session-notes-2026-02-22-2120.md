# Session Notes — 2026-02-22 (CSP Fix)

## Commits in This PR

| Commit | Description |
|--------|-------------|
| `777a7d9` | v179: Add extmgmt.dev.azure.com to CSP connect-src |
| (this commit) | Update v179 release notes with CSP fix, add session notes |

## Changes Made

### CSP Fix (`_headers`)
- **Problem:** Production dashboard blocked all ADO Extension Management API calls (`extmgmt.dev.azure.com`) due to Content Security Policy `connect-src` directive only allowing `dev.azure.com`
- **Root cause:** The Extension Management API uses a different subdomain (`extmgmt.dev.azure.com`) than the core ADO API (`dev.azure.com`)
- **Fix:** Added `https://extmgmt.dev.azure.com` to the `connect-src` directive in `_headers`
- **Impact:** Unblocks cascading list fetch, save, and picklist sync in production

### Release Notes Updates
- Updated `changelog.js` v179 entry with CSP fix bullet
- Updated `DASHBOARD_README.md` v179 entry with CSP fix note

## Decisions
- Kept same version (v179) since this is a post-production bug fix for the same release

## Open Items
- User needs to test full cascading list save flow in production after merge
- Verify picklist sync adds new values to ADO field definitions
- Verify conversation modal works with ADO auth in production
