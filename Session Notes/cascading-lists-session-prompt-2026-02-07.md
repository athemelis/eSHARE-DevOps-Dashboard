# Cascading Lists Integration — Session Prompt

## Context

I'm working on my **eSHARE-DevOps-Dashboard** (currently v156), a modular HTML/JS/CSS reporting dashboard that visualizes Azure DevOps work items. Read `CLAUDE.md` for full project context, but **do NOT follow the "Starting a Session" instructions**.

## Goal

Integrate the **Cascading Lists** Azure DevOps extension configuration into my dashboard so users can:

1. **View** the cascading lists JSON (version ↔ date mappings) in the dashboard
2. **Edit** entries and **write changes back** to the Cascading Lists configuration in ADO

## What Are Cascading Lists?

Cascading Lists is an ADO extension by Microsoft DevLabs (`ms-devlabs/cascading-picklists-extension`) that creates parent-child relationships between picklist fields on work item forms. In our case, it links two custom fields:

- `Custom.CascadingVersion` → `Custom.CascadingDate` (and vice versa)
- Example: selecting version `202602.1.0` auto-sets the date to `2026-02-07`

**Source code:** https://github.com/microsoft/azure-devops-extension-cascading-picklist

## JSON Structure

The config JSON has this structure:

```json
{
  "version": "1.0",
  "cascades": {
    "Custom.CascadingVersion": {
      "202602.1.0": {
        "Custom.CascadingDate": ["2026-02-07"]
      }
    },
    "Custom.CascadingDate": {
      "2026-02-07": {
        "Custom.CascadingVersion": ["202602.1.0"]
      }
    }
  }
}
```

The mapping is **bidirectional**: Version→Date AND Date→Version. Currently ~75 version/date pairs spanning Aug 2025 through Dec 2026. An existing manually-exported copy is at `cascading_lists.json` in the project root.

## API Endpoint (Confirmed via Network Capture)

The extension stores its config using Azure DevOps Extension Data Storage. The exact REST API endpoint is:

```
GET/PUT https://extmgmt.dev.azure.com/ncryptedcloud/_apis/ExtensionManagement/InstalledExtensions/ms-devlabs/cascading-picklists-extension/Data/Scopes/Default/Current/Collections/$settings/Documents/manifest|7549e9c5-2259-4a1e-914b-e5989aeb4e3c
```

Key details:
- **Organization:** `ncryptedcloud`
- **Publisher:** `ms-devlabs`
- **Extension:** `cascading-picklists-extension`
- **Scope:** `Default/Current` (shared across all project users)
- **Collection:** `$settings`
- **Document ID:** `manifest|7549e9c5-2259-4a1e-914b-e5989aeb4e3c` (pattern: `manifest|{projectId}`)
- **eShare Project ID:** `7549e9c5-2259-4a1e-914b-e5989aeb4e3c`
- **Concurrency:** Uses `__etag` field — must include in PUT requests for updates

The ADO Cascading Lists settings page is at:
`https://dev.azure.com/ncryptedcloud/eShare/_settings/ms-devlabs.cascading-picklists-extension.cascading-lists-config-hub`

## Authentication

### Current Dashboard Auth (SharePoint)
- **MSAL** with Azure AD tenant `wardedbox.onmicrosoft.com`
- **App Registration Client ID:** `bf683b68-0dc3-4205-a5b7-676f54a958c0`
- **Scope:** `Sites.Selected` (SharePoint/Graph API only)
- **On localhost:** MSAL disabled, loads local JSON files

### For Cascading Lists Data (Export/Read)
I've uploaded the `cascading_lists.json` to SharePoint so the dashboard can fetch it using the **same MSAL/Graph API auth** it already uses for other data files (`ALL Items.json`, `WorkItemLinks.json`, `Org Chart.json`). This avoids needing a new auth mechanism.

**TODO:** Get the SharePoint file ID for the cascading_lists.json file (similar to `01VN5XFOTKZ2ORQHSSKFF3XBLIMIFJ7W6Z` format) and add it to the `CONFIG.SHAREPOINT.FILES` object in `dashboard-loader.js`.

### For Writing Back to ADO (Import/Write)
Writing changes back to the Cascading Lists config in ADO requires calling the `extmgmt.dev.azure.com` API, which needs **Azure DevOps authentication** — NOT the SharePoint MSAL scope. Options:

1. **PAT-based** (simplest): User enters a Personal Access Token, stored in localStorage, used as `Authorization: Basic base64(:PAT)`
2. **Add ADO scope to MSAL app**: Add `499b84ac-1321-427f-aa17-267ca6975798/user_impersonation` to the Azure AD app registration. Requires admin consent.
3. **Manual workflow**: User edits in dashboard, exports updated JSON, manually pastes into ADO Cascading Lists settings page

## Implementation Plan

### Phase 1 — Export (Read from SharePoint)
1. Add the cascading_lists.json SharePoint file ID to `CONFIG.SHAREPOINT.FILES`
2. Add a `loadCascadingLists()` function in `dashboard-loader.js` using the same `getSharePointFileById()` pattern
3. On localhost, fall back to loading local `cascading_lists.json`

### Phase 2 — Display in Dashboard
- **UI placement TBD** — either a new dedicated tab or integrated into the Releases view
- Render an editable table showing Version → Date mappings
- Include search/filter capabilities

### Phase 3 — Import (Write Back to ADO)
- Add UI for adding/editing/deleting version-date pairs
- Decide auth approach for write-back (PAT vs OAuth vs manual)
- PUT modified JSON to the `extmgmt.dev.azure.com` endpoint with `__etag` for concurrency
- Must update BOTH directions of the mapping (Version→Date AND Date→Version)

## Key References

- [Cascading Lists GitHub Repo](https://github.com/microsoft/azure-devops-extension-cascading-picklist)
- [Extension Data Storage Docs](https://learn.microsoft.com/en-us/azure/devops/extend/develop/data-storage?view=azure-devops)
- [API Update Issue #101](https://github.com/microsoft/azure-devops-extension-cascading-picklist/issues/101)
- [Data Storage Issue #24](https://github.com/microsoft/azure-devops-extension-cascading-picklist/issues/24)
- [VS Marketplace Listing](https://marketplace.visualstudio.com/items?itemName=ms-devlabs.cascading-picklists-extension)
